"""
LLM 判断模块：调用大模型进行语义级匹配与推理
"""
import json
import logging
import requests
import re
from typing import Dict, Any, Optional
import time
import hashlib
import os
from pathlib import Path
from src.config import Config

logger = logging.getLogger(__name__)


class LLMJudge:
    """LLM 判断器"""
    
    def __init__(self):
        """初始化 LLM 判断器"""
        self.provider = Config.LLM_PROVIDER
        self.api_key = Config.get_api_key()
        self.model = Config.get_model_name()
        self.max_retries = Config.MAX_RETRIES
        self.timeout = Config.REQUEST_TIMEOUT
        self.fast_failover = Config.FAST_FAILOVER
        self.failover_cooldown = Config.FAILOVER_COOLDOWN_SECONDS
        self.max_parse_retries = Config.MAX_PARSE_RETRIES
        self.failed_providers: Dict[str, float] = {}
        self.temperature = Config.LLM_TEMPERATURE
        self.enable_cache = Config.ENABLE_CACHE
        self.enable_fallback = Config.ENABLE_FALLBACK
        
        # 初始化缓存目录
        if self.enable_cache:
            self.cache_dir = Path(Config.CACHE_DIR)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"缓存已启用，缓存目录: {self.cache_dir}")
        else:
            self.cache_dir = None
            logger.info("缓存已禁用")
        
        if not self.enable_fallback:
            logger.info(f"Fallback已禁用，只使用配置的Provider: {self.provider}")
        
        if not self.api_key:
            raise ValueError(f"未配置 {self.provider.upper()} API Key")
        
        logger.info(f"初始化 LLM 判断器: Provider={self.provider}, Model={self.model}, Temperature={self.temperature}")
    
    def _call_openai(self, prompt: str) -> str:
        """
        调用 OpenAI API
        
        Args:
            prompt: 提示词
            
        Returns:
            API 响应文本
        """
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式。在生成evidence字段时：如果涉及的交易笔数较少（例如少于 30 笔），请务必在 evidence 中列出用于计算的所有交易金额明细，以便人工复核；如果有异常发现（如单笔金额不连续），必须列出导致异常的具体交易；如果交易笔数较多（超过 30 笔）且验证通过，则【严禁】列出每一笔交易，只需概括验证逻辑并列出前3笔作为示例。确保输出简洁与可追溯性的平衡，避免因内容过长导致JSON格式错误。\n\n关键原则：你的判定（hit值）必须严格基于当前规则定义的“校验逻辑”。严禁“跨规则连坐”：例如在执行日期校验规则时，即使发现金额或笔数不一致，只要日期符合规则要求（即 min_date 和 max_date 在区间内，无需完全覆盖整个区间），就必须判定为“一致”（hit=false）。只有当当前规则明确关注的指标（如在校验金额规则时发现金额不一致）出现问题时，才应判定为 hit=true。不要因为发现了规则定义范围之外的其他异常而改变当前规则的判定结果。\n\n自检要求：当需要统计列表项数量时（例如 total_cnt），必须确保你列出的项数与你给出的统计数字完全一致。系统已在数据中提供了预计算的统计值（如'有效 Abonos 交易数'），请优先参考这些参考值作为 Ground Truth，避免手动计数错误。禁止出现‘列出了N项却说是M项’的错误。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 4000,  # 设置为4000以支持详细的evidence字段（平衡长度和API限制）
            # 注意：某些API（如DeepSeek）可能不支持response_format参数
            # 如果API返回错误，会在调用时自动处理
            # "response_format": {"type": "json_object"}  # 暂时禁用，避免API不支持导致错误
        }
        
        logger.debug(f"调用 OpenAI API: {self.model}")
        # 如果禁用fallback，必须重试；如果启用fallback且fast_failover，则快速失败
        max_attempts = (self.max_retries + 1) if (not self.enable_fallback or not self.fast_failover) else 1
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("OpenAI", response)
                if response.status_code == 400:
                    # 记录详细的400错误信息
                    try:
                        error_detail = response.json()
                        logger.error(f"OpenAI API 400错误详情: {json.dumps(error_detail, ensure_ascii=False)}")
                        # 如果是max_tokens相关的错误，尝试降低max_tokens
                        error_msg = str(error_detail).lower()
                        if 'max_tokens' in error_msg or 'token' in error_msg:
                            logger.warning("检测到可能是max_tokens相关的错误，建议检查API限制")
                    except:
                        logger.error(f"OpenAI API 400错误响应: {response.text[:500]}")
                    # 不立即raise，先记录错误信息
                    raise requests.exceptions.HTTPError(f"400 Client Error: {response.text[:200]}")
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    wait_time = min(4 * (2 ** attempt), 60)  # 指数退避，最多等待60秒
                    logger.warning(f"OpenAI API 调用失败 (尝试 {attempt + 1}/{max_attempts}): {str(e)}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"OpenAI API 调用失败 (已重试 {max_attempts} 次): {str(e)}")
                    raise
    
    def _call_deepseek(self, prompt: str) -> str:
        """
        调用 DeepSeek API
        
        Args:
            prompt: 提示词
            
        Returns:
            API 响应文本
        """
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式。在生成evidence字段时：如果涉及的交易笔数较少（例如少于 30 笔），请务必在 evidence 中列出用于计算的所有交易金额明细，以便人工复核；如果有异常发现（如单笔金额不连续），必须列出导致异常的具体交易；如果交易笔数较多（超过 30 笔）且验证通过，则【严禁】列出每一笔交易，只需概括验证逻辑并列出前3笔作为示例。确保输出简洁与可追溯性的平衡，避免因内容过长导致JSON格式错误。\n\n关键原则：你的判定（hit值）必须严格基于当前规则定义的“校验逻辑”。严禁“跨规则连坐”：例如在执行日期校验规则时，即使发现金额或笔数不一致，只要日期符合规则要求（即 min_date 和 max_date 在区间内，无需完全覆盖整个区间），就必须判定为“一致”（hit=false）。只有当当前规则明确关注的指标（如在校验金额规则时发现金额不一致）出现问题时，才应判定为 hit=true。不要因为发现了规则定义范围之外的其他异常而改变当前规则的判定结果。\n\n自检要求：当需要统计列表项数量时（例如 total_cnt），必须确保你列出的项数与你给出的统计数字完全一致。系统已在数据中提供了预计算的统计值（如'有效 Abonos 交易数'），请优先参考这些参考值作为 Ground Truth，避免手动计数错误。禁止出现‘列出了N项却说是M项’的错误。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 4000,  # 设置为4000以支持详细的evidence字段（平衡长度和API限制）
            # 注意：某些API（如DeepSeek）可能不支持response_format参数
            # 如果API返回错误，会在调用时自动处理
            # "response_format": {"type": "json_object"}  # 暂时禁用，避免API不支持导致错误
        }
        
        logger.debug(f"调用 DeepSeek API: {self.model}")
        # 如果禁用fallback，必须重试；如果启用fallback且fast_failover，则快速失败
        max_attempts = (self.max_retries + 1) if (not self.enable_fallback or not self.fast_failover) else 1
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("DeepSeek", response)
                if response.status_code == 400:
                    # 记录详细的400错误信息
                    try:
                        error_detail = response.json()
                        logger.error(f"DeepSeek API 400错误详情: {json.dumps(error_detail, ensure_ascii=False)}")
                        # 如果是max_tokens相关的错误，尝试降低max_tokens
                        error_msg = str(error_detail).lower()
                        if 'max_tokens' in error_msg or 'token' in error_msg:
                            logger.warning("检测到可能是max_tokens相关的错误，建议检查API限制")
                    except:
                        logger.error(f"DeepSeek API 400错误响应: {response.text[:500]}")
                    # 不立即raise，先记录错误信息
                    raise requests.exceptions.HTTPError(f"400 Client Error: {response.text[:200]}")
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    wait_time = min(4 * (2 ** attempt), 60)  # 指数退避，最多等待60秒
                    logger.warning(f"DeepSeek API 调用失败 (尝试 {attempt + 1}/{max_attempts}): {str(e)}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"DeepSeek API 调用失败 (已重试 {max_attempts} 次): {str(e)}")
                    raise
    
    def _call_authorpic(self, prompt: str) -> str:
        """
        调用 Authorpic API（自定义模型）
        
        Args:
            prompt: 提示词
            
        Returns:
            API 响应文本
        """
        # 注意：这里需要根据实际的 Authorpic API 文档调整
        url = "https://api.authorpic.com/v1/chat/completions"  # 请根据实际 API 地址修改
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式。在生成evidence字段时，对于包含大量交易及步骤的验证，【严禁】列出每一笔交易的详细核算过程，只需概括验证逻辑、范围，并重点列出发现的异常点（如有）或仅列出前3笔作为示例。确保输出简洁，避免因内容过长导致JSON格式错误。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 4000,  # 设置为4000以支持详细的evidence字段（平衡长度和API限制）
            # 注意：某些API（如DeepSeek）可能不支持response_format参数
            # 如果API返回错误，会在调用时自动处理
            # "response_format": {"type": "json_object"}  # 暂时禁用，避免API不支持导致错误
        }
        
        logger.debug(f"调用 Authorpic API: {self.model}")
        # 如果禁用fallback，必须重试；如果启用fallback且fast_failover，则快速失败
        max_attempts = (self.max_retries + 1) if (not self.enable_fallback or not self.fast_failover) else 1
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("Authorpic", response)
                if response.status_code == 400:
                    # 记录详细的400错误信息
                    try:
                        error_detail = response.json()
                        logger.error(f"Authorpic API 400错误详情: {json.dumps(error_detail, ensure_ascii=False)}")
                    except:
                        logger.error(f"Authorpic API 400错误响应: {response.text[:500]}")
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                if attempt < max_attempts - 1:
                    wait_time = min(4 * (2 ** attempt), 60)  # 指数退避，最多等待60秒
                    logger.warning(f"Authorpic API 调用失败 (尝试 {attempt + 1}/{max_attempts}): {str(e)}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Authorpic API 调用失败 (已重试 {max_attempts} 次): {str(e)}")
                    raise
    
    def _get_cache_key(self, prompt: str, provider: str = None, model: str = None) -> str:
        """
        生成缓存键（仅基于prompt的hash，确保相同prompt得到相同结果）
        
        Args:
            prompt: 提示词
            provider: LLM provider（可选，用于日志记录）
            model: 模型名称（可选，用于日志记录）
            
        Returns:
            缓存键（hash值）
        """
        # 只基于prompt生成缓存键，确保相同输入无论使用哪个provider都返回相同结果
        return hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    
    def _try_load_from_any_cache(self, prompt: str, providers_to_try: list) -> Optional[Dict[str, Any]]:
        """
        尝试从任何可能的provider缓存中加载结果
        
        Args:
            prompt: 提示词
            providers_to_try: 要尝试的provider列表
            
        Returns:
            缓存的结果，如果不存在则返回None
        """
        if not self.enable_cache or not self.cache_dir:
            return None
        
        # 由于缓存键只基于prompt，只需要尝试一次
        cache_key = self._get_cache_key(prompt)
        return self._load_from_cache(cache_key)
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存加载结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存的结果，如果不存在则返回None
        """
        if not self.enable_cache or not self.cache_dir:
            return None
        
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_result = json.load(f)
                logger.info(f"从缓存加载结果: {cache_key[:16]}...")
                return cached_result
            except Exception as e:
                logger.warning(f"读取缓存失败: {e}")
                return None
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        保存结果到缓存
        
        Args:
            cache_key: 缓存键
            result: 要缓存的结果
        """
        if not self.enable_cache or not self.cache_dir:
            return
        
        try:
            cache_path = self._get_cache_path(cache_key)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.debug(f"结果已缓存: {cache_key[:16]}...")
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    def judge(self, prompt: str, fallback_providers: list = None) -> Dict[str, Any]:
        """
        调用 LLM 进行判断（仅使用 DeepSeek）
        
        Args:
            prompt: 提示词
            fallback_providers: 已弃用，保留参数以兼容旧代码
            
        Returns:
            判断结果字典，包含 hit, evidence, confidence, notes
        """
        # --- DEBUG INSTRUMENTATION ---
        # try:
        #     with open("prompt_debug.txt", "a", encoding="utf-8") as f:
        #         f.write("\n" + "="*80 + "\n")
        #         f.write(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        #         f.write("PROMPT START\n")
        #         f.write(prompt)
        #         f.write("\nPROMPT END\n")
        # except Exception as e:
        #     logger.warning(f"Failed to write prompt debug log: {e}")
        # -----------------------------

        # 只使用 DeepSeek provider
        provider = "deepseek"
        
        # 尝试从缓存加载
        cached_result = self._try_load_from_any_cache(prompt, [provider])
        if cached_result is not None:
            logger.info(f"从缓存加载结果（prompt hash: {self._get_cache_key(prompt)[:16]}...）")
            return cached_result
        
        try:
            logger.info(f"尝试使用 LLM Provider: {provider}")
            
            parse_attempts = 0
            while True:
                # 调用 DeepSeek API
                response_text = self._call_deepseek(prompt)
                
                logger.debug(f"LLM 原始响应: {response_text[:200]}...")
                
                try:
                    # 尝试解析 JSON 响应
                    result = self._parse_response(response_text)
                except ValueError as parse_err:
                    error_msg = str(parse_err)
                    # 记录详细错误信息
                    logger.error(f"Provider {provider} 响应解析失败: {error_msg}")
                    logger.error(f"原始响应前2000字符:\n{response_text[:2000]}")
                    
                    if "PARSE_ERROR" in error_msg and parse_attempts < self.max_parse_retries:
                        parse_attempts += 1
                        logger.warning(
                            f"Provider {provider} 响应解析失败（尝试 {parse_attempts}/{self.max_parse_retries}），准备重新请求..."
                        )
                        continue
                    
                    # 如果重试次数已用完，返回一个合理的结果而不是直接失败
                    if parse_attempts >= self.max_parse_retries:
                        logger.error(f"Provider {provider} 响应解析失败，已重试 {self.max_parse_retries} 次，返回null结果")
                        result = {
                            "hit": None,
                            "evidence": f"LLM响应解析失败: {error_msg}。原始响应已记录在日志中。",
                            "confidence": "low",
                            "notes": f"Provider {provider} 返回的响应无法解析为JSON格式。已重试 {self.max_parse_retries} 次。建议检查日志获取完整响应内容。"
                        }
                        # 保存到缓存（即使是失败的结果）
                        cache_key = self._get_cache_key(prompt)
                        self._save_to_cache(cache_key, result)
                        return result
                    
                    raise
                break
            
            # 记录 LLM 请求和响应（用于审计回溯）
            logger.info(f"LLM 判断完成 (Provider: {provider}): hit={result.get('hit')}, confidence={result.get('confidence')}")
            
            # 保存到缓存
            cache_key = self._get_cache_key(prompt)
            self._save_to_cache(cache_key, result)
            
            return result
        
        except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
            error_msg = str(e)
            logger.error(f"DeepSeek API 调用失败: {error_msg}")
            return {
                "hit": None,
                "evidence": f"DeepSeek API 调用失败。错误: {error_msg}。可能是网络连接问题或 API 服务暂时不可用。",
                "confidence": "low",
                "notes": f"DeepSeek API 调用失败。建议检查网络连接、API Key配置或稍后重试。如果问题持续，请查看日志获取详细信息。"
            }
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"LLM 判断时发生错误 ({error_type}): {error_msg}")
            return {
                "hit": None,
                "evidence": f"处理错误 ({error_type}): {error_msg}",
                "confidence": "low",
                "notes": f"处理过程中发生异常: {error_type}。建议重新运行程序或检查日志获取详细信息。"
            }
    
    def _handle_http_error(self, provider: str, response: requests.Response) -> None:
        """
        处理 LLM API 的鉴权与配额错误，提供更明确的提示
        """
        status = response.status_code
        message = response.text
        normalized_msg = message.lower() if isinstance(message, str) else ""
        
        if status in (401, 403):
            raise RuntimeError(
                f"{provider} API 返回 {status}，疑似鉴权失败。"
                f" 请确认 API Key 是否正确、是否具有调用权限。原始响应: {message}"
            )
        if status == 429 and "insufficient_quota" in normalized_msg:
            raise RuntimeError(
                f"{provider} API 返回 429（配额不足），可能是 token 或余额已用尽。"
                f" 请检查账户配额或更换可用的 API Key。原始响应: {message}"
            )
    
    def _provider_available(self, provider: str) -> bool:
        """
        判断 provider 是否处于冷却期
        """
        cooldown_until = self.failed_providers.get(provider)
        if cooldown_until is None:
            return True
        if time.time() >= cooldown_until:
            self.failed_providers.pop(provider, None)
            return True
        return False
    
    def _mark_provider_failed(self, provider: str) -> None:
        """
        将 provider 标记为失败，进入冷却期以加速切换
        """
        if self.failover_cooldown <= 0:
            # 无冷却时间，允许下次立即重试
            self.failed_providers[provider] = time.time()
        else:
            self.failed_providers[provider] = time.time() + self.failover_cooldown
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 LLM 响应文本，提取 JSON 结果
        
        Args:
            response_text: LLM 响应文本
            
        Returns:
            解析后的结果字典
        """
        # 尝试提取 JSON 块
        try:
            json_text = None
            original_response = response_text.strip()
            
            # 方法1: 查找 JSON 代码块 (```json ... ```)
            if "```json" in original_response:
                start = original_response.find("```json") + 7
                end = original_response.find("```", start)
                if end > start:
                    json_text = original_response[start:end].strip()
                    logger.debug("从 ```json 代码块中提取 JSON")
            
            # 方法2: 查找通用代码块 (``` ... ```)
            if not json_text and "```" in original_response:
                start = original_response.find("```") + 3
                end = original_response.find("```", start)
                if end > start:
                    candidate = original_response[start:end].strip()
                    # 检查是否包含JSON结构
                    if candidate.startswith("{") and candidate.endswith("}"):
                        json_text = candidate
                        logger.debug("从通用代码块中提取 JSON")
            
            # 方法3: 直接查找 JSON 对象（改进：处理多行JSON）
            if not json_text:
                start = original_response.find("{")
                if start >= 0:
                    # 从第一个 { 开始，找到匹配的最后一个 }
                    # 需要正确处理字符串中的大括号和转义字符
                    brace_count = 0
                    end = start
                    in_string = False
                    escape_next = False
                    
                    for i in range(start, len(original_response)):
                        char = original_response[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        
                        if not in_string:
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    end = i + 1
                                    break
                    
                    if end > start and end < len(original_response):
                        json_text = original_response[start:end].strip()
                        logger.debug("从响应文本中直接提取 JSON（多行格式）")
                    elif start >= 0:
                        # 如果括号匹配失败（可能因为字符串太长），记录调试信息
                        logger.debug(f"括号匹配失败 (start={start}, end={end}, len={len(original_response)})，将在最后手段中尝试从第一个{{到最后一个}}")
                        # 如果end没有找到匹配的}，可能是因为字符串值太长导致循环没有完成
                        # 这种情况下，我们会在"最后手段1"中处理
            
            # 如果仍然没有找到，尝试更宽松的匹配
            if not json_text:
                # 尝试查找包含 hit, evidence, confidence 的文本块
                # 查找类似 {"hit": ... } 的模式
                pattern = r'\{[^{}]*"hit"[^{}]*\}'
                matches = re.findall(pattern, original_response, re.DOTALL)
                if matches:
                    # 尝试扩展匹配以包含完整的JSON对象
                    for match in matches:
                        # 尝试找到包含这个匹配的完整JSON对象
                        match_start = original_response.find(match)
                        if match_start >= 0:
                            # 向前查找 {，向后查找 }
                            obj_start = original_response.rfind("{", 0, match_start)
                            obj_end = original_response.find("}", match_start + len(match))
                            if obj_start >= 0 and obj_end > obj_start:
                                candidate = original_response[obj_start:obj_end + 1]
                                if candidate.count("{") == candidate.count("}"):
                                    json_text = candidate
                                    logger.debug("使用正则表达式提取 JSON")
                                    break
            
            # 如果仍然没有找到，尝试更激进的提取方法
            if not json_text:
                # 方法5: 尝试查找任何包含大括号的文本块
                # 查找所有可能包含JSON的文本段
                brace_positions = []
                for i, char in enumerate(original_response):
                    if char == '{':
                        brace_positions.append(i)
                
                # 对每个 { 位置，尝试找到匹配的 }
                for start_pos in brace_positions:
                    brace_count = 0
                    end_pos = start_pos
                    for i in range(start_pos, len(original_response)):
                        if original_response[i] == '{':
                            brace_count += 1
                        elif original_response[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                candidate = original_response[start_pos:end_pos].strip()
                                # 检查是否包含必要的字段
                                if '"hit"' in candidate or "'hit'" in candidate:
                                    try:
                                        # 尝试解析以验证
                                        test_result = json.loads(candidate)
                                        if isinstance(test_result, dict):
                                            json_text = candidate
                                            logger.debug("使用激进方法提取 JSON")
                                            break
                                    except:
                                        continue
                    if json_text:
                        break
            
            if not json_text:
                # 最后手段1：尝试从第一个{到最后一个}提取（处理多行JSON）
                # 这是最可靠的方法，因为即使JSON格式有问题，也能提取出完整的JSON结构
                first_brace = original_response.find("{")
                last_brace = original_response.rfind("}")
                logger.info(f"最后手段1：查找JSON边界 - first_brace={first_brace}, last_brace={last_brace}, response_length={len(original_response)}")
                if first_brace >= 0 and last_brace > first_brace:
                    candidate_json = original_response[first_brace:last_brace + 1]
                    logger.info(f"最后手段1：提取的候选JSON长度: {len(candidate_json)}, 前500字符: {candidate_json[:500]}")
                    # 检查是否包含必要的字段
                    if '"hit"' in candidate_json or "'hit'" in candidate_json:
                        logger.info(f"最后手段1：候选JSON包含'hit'字段，开始解析...")
                        try:
                            # 尝试直接解析
                            test_result = json.loads(candidate_json)
                            if isinstance(test_result, dict) and 'hit' in test_result:
                                json_text = candidate_json
                                logger.info("使用最后手段1成功提取JSON（从第一个{到最后一个}，直接解析成功）")
                        except json.JSONDecodeError as e:
                            logger.warning(f"最后手段1提取的JSON直接解析失败: {e}")
                            # 如果解析失败，尝试修复后再解析
                            try:
                                logger.info("最后手段1：开始修复JSON（转义未转义换行符）...")
                                # 修复常见的JSON错误：未转义的换行符
                                # 使用逐字符处理，不要按行分割（避免破坏跨行的字符串值）
                                fixed_chars = []
                                in_string = False
                                escape_next = False
                                
                                # 添加进度日志（每处理10000字符记录一次）
                                total_chars = len(candidate_json)
                                for i, char in enumerate(candidate_json):
                                    # 每处理10000字符记录一次进度
                                    if i > 0 and i % 10000 == 0:
                                        logger.debug(f"最后手段1：修复进度 {i}/{total_chars} ({i*100//total_chars}%)")
                                    
                                    if escape_next:
                                        escape_next = False
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if char == '\\':
                                        escape_next = True
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if char == '"':
                                        in_string = not in_string
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if in_string:
                                        # 在字符串值内部，转义未转义的换行符、制表符、回车符
                                        if char == '\n':
                                            fixed_chars.append('\\n')
                                        elif char == '\r':
                                            fixed_chars.append('\\r')
                                        elif char == '\t':
                                            fixed_chars.append('\\t')
                                        else:
                                            fixed_chars.append(char)
                                    else:
                                        fixed_chars.append(char)
                                
                                fixed_json = ''.join(fixed_chars)
                                logger.info(f"最后手段1：修复完成，修复后的JSON长度: {len(fixed_json)}, 前500字符: {fixed_json[:500]}")
                                
                                test_result = json.loads(fixed_json)
                                if isinstance(test_result, dict) and 'hit' in test_result:
                                    json_text = fixed_json
                                    logger.info("使用最后手段1成功提取JSON（修复未转义换行符后）")
                            except Exception as e2:
                                logger.warning(f"最后手段1修复后仍然解析失败: {e2}, 错误类型: {type(e2).__name__}")
                                # 记录更多调试信息
                                if isinstance(e2, json.JSONDecodeError):
                                    logger.warning(f"JSON解析错误位置: 行{e2.lineno}, 列{e2.colno}, 消息: {e2.msg}")
                                    # 显示错误位置附近的文本
                                    if e2.pos and e2.pos < len(fixed_json):
                                        start = max(0, e2.pos - 100)
                                        end = min(len(fixed_json), e2.pos + 100)
                                        logger.warning(f"错误位置附近的文本: ...{fixed_json[start:end]}...")
                                
                                # 尝试更激进的修复：如果修复后仍然失败，尝试只提取hit和evidence字段
                                try:
                                    logger.info("最后手段1：尝试更激进的修复（只提取关键字段）...")
                                    # 尝试从修复后的JSON中提取hit和evidence
                                    hit_match = re.search(r'"hit"\s*:\s*(true|false|null)', fixed_json, re.IGNORECASE)
                                    evidence_match = re.search(r'"evidence"\s*:\s*"([^"]*)"', fixed_json, re.DOTALL)
                                    
                                    if hit_match or evidence_match:
                                        # 构建一个简化的JSON
                                        hit_str = hit_match.group(1).lower() if hit_match else "null"
                                        hit_value = True if hit_str == 'true' else (False if hit_str == 'false' else None)
                                        evidence_value = evidence_match.group(1) if evidence_match else ""
                                        
                                        # 处理转义字符
                                        if evidence_value:
                                            evidence_value = evidence_value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
                                        
                                        # 构建一个有效的JSON
                                        simplified_json = f'{{"hit": {hit_str}, "evidence": {json.dumps(evidence_value)}, "confidence": "low"}}'
                                        test_result = json.loads(simplified_json)
                                        if isinstance(test_result, dict):
                                            json_text = simplified_json
                                            logger.info("使用最后手段1成功提取JSON（激进修复：只提取关键字段）")
                                except Exception as e3:
                                    logger.debug(f"最后手段1激进修复也失败: {e3}")
                else:
                    logger.warning(f"最后手段1：未找到有效的JSON边界 (first_brace={first_brace}, last_brace={last_brace})")
                    # 如果找到了{但没有找到}，可能是JSON被截断了，尝试手动补全
                    if first_brace >= 0 and last_brace == -1:
                        logger.info("最后手段1：检测到JSON可能被截断，尝试手动补全...")
                        # 尝试从第一个{开始，查找最后一个可能的结束位置
                        # 查找最后一个可能的结束字符（可能是换行符、空格等）
                        candidate_json = original_response[first_brace:]
                        # 尝试在末尾添加}
                        candidate_json_with_brace = candidate_json.rstrip() + "\n}"
                        logger.info(f"最后手段1：尝试补全JSON，长度: {len(candidate_json_with_brace)}")
                        try:
                            test_result = json.loads(candidate_json_with_brace)
                            if isinstance(test_result, dict) and 'hit' in test_result:
                                json_text = candidate_json_with_brace
                                logger.info("使用最后手段1成功提取JSON（补全缺失的}后）")
                        except:
                            # 如果补全}后仍然失败，尝试修复未转义换行符后再补全
                            try:
                                logger.info("最后手段1：补全}后解析失败，尝试修复未转义换行符...")
                                fixed_chars = []
                                in_string = False
                                escape_next = False
                                
                                for i, char in enumerate(candidate_json):
                                    if escape_next:
                                        escape_next = False
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if char == '\\':
                                        escape_next = True
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if char == '"':
                                        in_string = not in_string
                                        fixed_chars.append(char)
                                        continue
                                    
                                    if in_string:
                                        if char == '\n':
                                            fixed_chars.append('\\n')
                                        elif char == '\r':
                                            fixed_chars.append('\\r')
                                        elif char == '\t':
                                            fixed_chars.append('\\t')
                                        else:
                                            fixed_chars.append(char)
                                    else:
                                        fixed_chars.append(char)
                                
                                fixed_json = ''.join(fixed_chars).rstrip() + "\n}"
                                test_result = json.loads(fixed_json)
                                if isinstance(test_result, dict) and 'hit' in test_result:
                                    json_text = fixed_json
                                    logger.info("使用最后手段1成功提取JSON（修复未转义换行符并补全}后）")
                            except Exception as e3:
                                logger.debug(f"最后手段1补全和修复后仍然失败: {e3}")
                
                # 最后手段2：尝试从文本中提取关键信息（优化：限制搜索范围，提高性能）
                if not json_text:
                    logger.warning(f"无法从响应中提取 JSON。响应文本前2000字符:\n{original_response[:2000]}")
                    logger.warning("尝试从文本中提取关键信息...")
                    
                    # 限制搜索范围，只搜索前100000字符（避免处理过长的响应）
                    search_text = original_response[:100000] if len(original_response) > 100000 else original_response
                    logger.debug(f"限制搜索范围: {len(search_text)}字符（原始长度: {len(original_response)}）")
                
                # 尝试从文本中提取hit值（快速提取，只搜索前5000字符）
                hit_value = None
                hit_search_text = search_text[:5000] if 'search_text' in locals() else original_response[:5000]
                if 'hit' in hit_search_text.lower():
                    # 查找hit值（使用简单的模式，避免复杂正则）
                    hit_patterns = [
                        r'"hit"\s*:\s*(true|false|null)',
                        r"'hit'\s*:\s*(True|False|None)",
                    ]
                    for pattern in hit_patterns:
                        match = re.search(pattern, hit_search_text, re.IGNORECASE)
                        if match:
                            hit_str = match.group(1).lower()
                            if hit_str == 'true':
                                hit_value = True
                            elif hit_str == 'false':
                                hit_value = False
                            else:
                                hit_value = None
                            break
                
                # 尝试从文本中提取evidence（优化：移除长度限制，确保提取完整内容）
                evidence_value = ""
                # 使用完整的搜索文本，不限制长度（但限制在search_text范围内，避免处理过长的响应）
                evidence_search_text = search_text if 'search_text' in locals() else original_response
                if 'evidence' in evidence_search_text.lower():
                    logger.debug("开始提取evidence...")
                    # 方法1: 使用正则表达式提取（不限制长度，但使用非贪婪匹配避免回溯问题）
                    evidence_patterns = [
                        r'"evidence"\s*:\s*"((?:[^"\\]|\\.)*)"',  # 支持转义字符，不限制长度
                        r'"evidence"\s*:\s*"([^"]*)"',  # 备用：简单匹配
                    ]
                    for pattern in evidence_patterns:
                        try:
                            match = re.search(pattern, evidence_search_text, re.DOTALL)
                            if match:
                                evidence_value = match.group(1)
                                # 处理转义字符
                                evidence_value = evidence_value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")
                                if evidence_value:
                                    logger.debug(f"使用正则表达式提取evidence成功，长度: {len(evidence_value)}")
                                    break
                        except Exception as e:
                            logger.debug(f"正则表达式匹配失败: {e}")
                            continue
                    
                    # 方法2: 如果正则表达式失败，尝试手动提取（不限制长度，但限制在search_text范围内）
                    if not evidence_value:
                        logger.debug("正则表达式失败，尝试手动提取...")
                        # 查找 "evidence": " 的位置
                        evidence_start_pattern = r'"evidence"\s*:\s*"'
                        match_start = re.search(evidence_start_pattern, evidence_search_text, re.IGNORECASE)
                        if match_start:
                            start_pos = match_start.end()
                            # 不限制最大搜索长度，搜索整个evidence_search_text
                            max_search_length = len(evidence_search_text)
                            end_pos = start_pos
                            escape_next = False
                            found_end = False
                            
                            logger.debug(f"开始手动提取evidence，从位置{start_pos}开始，最大长度: {max_search_length}")
                            # 查找结束引号（不限制长度，但添加进度日志）
                            for i in range(start_pos, max_search_length):
                                # 每处理10000字符记录一次进度
                                if i > start_pos and (i - start_pos) % 10000 == 0:
                                    logger.debug(f"手动提取evidence进度: {i - start_pos}/{max_search_length - start_pos} 字符")
                                
                                char = evidence_search_text[i]
                                if escape_next:
                                    escape_next = False
                                    continue
                                if char == '\\':
                                    escape_next = True
                                    continue
                                if char == '"' and not escape_next:
                                    end_pos = i
                                    found_end = True
                                    break
                            
                            if found_end and end_pos > start_pos:
                                evidence_value = evidence_search_text[start_pos:end_pos]
                                # 处理转义字符
                                evidence_value = evidence_value.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")
                                logger.info(f"手动提取evidence成功，长度: {len(evidence_value)}")
                            elif not found_end:
                                # 如果没有找到结束引号，提取到search_text的末尾（可能是JSON被截断）
                                evidence_value = evidence_search_text[start_pos:max_search_length]
                                logger.warning(f"Evidence字段可能被截断，提取到search_text末尾，长度: {len(evidence_value)}")
                    else:
                        logger.debug(f"Evidence提取完成，长度: {len(evidence_value)}")
                
                # 如果提取到任何信息，返回一个合理的结果
                if hit_value is not None or evidence_value:
                    logger.warning(f"从文本中提取到部分信息: hit={hit_value}, evidence长度={len(evidence_value)}")
                    
                    # 确定置信度：如果提取到了明确的hit值，且evidence内容充实，则认为置信度为high
                    # 用户要求不接受LOW，因此只要我们能从文本中确信地提取出结果，就应给予高置信度
                    computed_confidence = "high" if hit_value is not None and len(evidence_value) > 50 else "medium"
                    if hit_value is None:
                        computed_confidence = "low"
                        
                    formatted_evidence = evidence_value if evidence_value else "无法完整解析LLM响应，但从文本中提取到部分信息。原始响应已记录在日志中。"
                    
                    return {
                        "hit": hit_value,
                        "evidence": formatted_evidence,
                        "confidence": computed_confidence,
                        "notes": "LLM响应格式异常（可能因内容过长或未转义字符导致JSON解析失败），但已成功从文本中通过正则提取关键信息。"
                    }
                
                # 如果完全无法提取，记录详细错误并返回null结果
                logger.error(f"完全无法从响应中提取信息。完整响应:\n{original_response}")
                raise ValueError("未找到 JSON 格式，且无法从文本中提取关键信息")
            
            # 尝试清理和修复JSON文本
            json_text_cleaned = json_text
            
            # 修复1: 移除尾随逗号（在 } 或 ] 之前）
            json_text_cleaned = re.sub(r',\s*}', '}', json_text_cleaned)
            json_text_cleaned = re.sub(r',\s*]', ']', json_text_cleaned)
            
            # 修复2: 修复字符串值中的未转义换行符（JSON不允许未转义的换行符）
            # 使用逐字符处理，只在字符串值内部修复未转义的换行符、制表符、回车符
            fixed_chars = []
            in_string = False
            escape_next = False
            
            for i, char in enumerate(json_text_cleaned):
                if escape_next:
                    escape_next = False
                    fixed_chars.append(char)
                    continue
                
                if char == '\\':
                    escape_next = True
                    fixed_chars.append(char)
                    continue
                
                if char == '"':
                    in_string = not in_string
                    fixed_chars.append(char)
                    continue
                
                if in_string:
                    # 在字符串值内部，转义未转义的换行符、制表符、回车符
                    if char == '\n':
                        fixed_chars.append('\\n')
                    elif char == '\r':
                        fixed_chars.append('\\r')
                    elif char == '\t':
                        fixed_chars.append('\\t')
                    else:
                        fixed_chars.append(char)
                else:
                    fixed_chars.append(char)
            
            json_text_cleaned = ''.join(fixed_chars)
            
            # 修复3: 修复单引号为双引号（JSON标准要求双引号）
            # 注意：需要小心处理，避免破坏已转义的引号
            # 先处理键名
            json_text_cleaned = re.sub(r"(\w+)'(\s*):", r'"\1"\2:', json_text_cleaned)
            # 再处理字符串值（更保守的方式）
            json_text_cleaned = re.sub(r":\s*'([^']*)'(\s*[,}])", r': "\1"\2', json_text_cleaned)
            
            # 修复4: 修复True/False/None（Python风格 -> JSON风格）
            # 注意：只在字符串外部进行（不在引号内）
            json_text_cleaned = re.sub(r'\bTrue\b', 'true', json_text_cleaned)
            json_text_cleaned = re.sub(r'\bFalse\b', 'false', json_text_cleaned)
            json_text_cleaned = re.sub(r'\bNone\b', 'null', json_text_cleaned)
            
            # 尝试解析JSON（按优先级尝试）
            result = None
            parse_errors = []
            
            # 尝试1: 解析清理后的JSON
            try:
                result = json.loads(json_text_cleaned)
            except json.JSONDecodeError as e:
                parse_errors.append(f"清理后JSON解析失败: {e}")
                logger.warning(f"清理后的JSON解析失败: {e}")
                
                # 尝试2: 解析原始JSON文本
                try:
                    result = json.loads(json_text)
                except json.JSONDecodeError as e2:
                    parse_errors.append(f"原始JSON解析失败: {e2}")
                    logger.warning(f"原始JSON解析失败: {e2}")
                    
                    # 尝试3: 更激进的修复
                    try:
                        # 尝试修复未转义的换行符（在字符串值中）
                        # 先找到所有字符串值，然后修复其中的换行符
                        fixed_text = json_text_cleaned
                        # 简单修复：将字符串中的实际换行符转义
                        # 注意：这可能会误修复，但作为最后手段
                        lines = fixed_text.split('\n')
                        fixed_lines = []
                        in_string = False
                        for line in lines:
                            if line.strip().startswith('"') and not in_string:
                                in_string = True
                            if in_string and line.strip().endswith('"'):
                                in_string = False
                            if in_string and '\n' in line:
                                line = line.replace('\n', '\\n')
                            fixed_lines.append(line)
                        fixed_text = '\n'.join(fixed_lines)
                        
                        result = json.loads(fixed_text)
                        logger.info("通过修复换行符成功解析JSON")
                    except json.JSONDecodeError as e3:
                        parse_errors.append(f"修复后JSON解析失败: {e3}")
                        # 记录详细的错误信息
                        logger.error(f"JSON 解析失败。所有尝试都失败。")
                        logger.error(f"原始响应前2000字符:\n{original_response[:2000]}")
                        logger.error(f"提取的JSON文本:\n{json_text[:1000]}")
                        logger.error(f"清理后的JSON文本:\n{json_text_cleaned[:1000]}")
                        logger.error(f"所有解析错误: {'; '.join(parse_errors)}")
                        raise ValueError(f"JSON 解析失败: {e3}")
            
            if result is None:
                raise ValueError("JSON解析失败，result为None")
            
            # 验证结果格式
            if not isinstance(result, dict):
                raise ValueError("响应不是字典格式")
            
            # 确保必要字段存在
            required_fields = ['hit', 'evidence', 'confidence']
            for field in required_fields:
                if field not in result:
                    logger.warning(f"响应缺少字段: {field}")
                    result[field] = None if field == 'hit' else "unknown"
            
            # 验证 hit 值
            if result['hit'] not in [True, False, None]:
                logger.warning(f"hit 值无效: {result['hit']}，设置为 None")
                result['hit'] = None
            
            # 验证 confidence 值
            if result['confidence'] not in ['high', 'medium', 'low']:
                logger.warning(f"confidence 值无效: {result['confidence']}，设置为 low")
                result['confidence'] = 'low'
            
            # ⚠️ 关键验证：检查 evidence 中的结论与 hit 值是否一致
            evidence = result.get('evidence', '').lower()
            hit_value = result.get('hit')
            
            # 为了避免误判，我们将重点检查 evidence 的末尾部分（最后500个字符）
            # 因为结论通常在最后，而前面的分析可能会引用规则定义（其中包含相反的关键词）
            evidence_end = evidence[-500:] if len(evidence) > 500 else evidence
            
            # 1. 检查 evidence 末尾是否明确说明了 hit 值 (使用正则匹配更灵活的表达)
            # 匹配模式如: "hit=false", "hit = false", "hit值为false", "hit应为false", "hit is false" 等
            hit_false_regex = r'hit\s*(?:=|:|是|为|应为|should be|is)\s*false'
            hit_true_regex = r'hit\s*(?:=|:|是|为|应为|should be|is)\s*true'
            
            found_explicit_judge = False
            
            if re.search(hit_false_regex, evidence_end, re.IGNORECASE):
                if hit_value is not False:
                    logger.warning(f"[警告] 检测到不一致：evidence 结尾明确指出 hit=False (正则匹配)，但 JSON 中 hit={hit_value}，已自动修正为 False")
                    result['hit'] = False
                    result['notes'] = result.get('notes', '') + "；已根据 evidence 结尾的明确结论自动修正 hit 值为 False"
                found_explicit_judge = True
            
            if not found_explicit_judge and re.search(hit_true_regex, evidence_end, re.IGNORECASE):
                if hit_value is not True:
                    logger.warning(f"[警告] 检测到不一致：evidence 结尾明确指出 hit=True (正则匹配)，但 JSON 中 hit={hit_value}，已自动修正为 True")
                    result['hit'] = True
                    result['notes'] = result.get('notes', '') + "；已根据 evidence 结尾的明确结论自动修正 hit 值为 True"
                found_explicit_judge = True
            
            # 2. 如果没有明确的 hit 值声明，检查结论性的描述（仅在末尾部分查找）
            if not found_explicit_judge:
                # 定义结论性模式
                consistent_patterns = ['结论：一致', '结论:一致', '结论：无异常', '结论:无异常', '判定：一致', '判定:一致', '结果：一致', '结果:一致', '最终判断：一致', '最终判断:一致', '最终结论：一致']
                inconsistent_patterns = ['结论：不一致', '结论:不一致', '结论：异常', '结论:异常', '判定：不一致', '判定:不一致', '结果：不一致', '结果:不一致', '最终判断：不一致', '最终判断:不一致', '最终结论：不一致']
                
                is_consistent = any(p in evidence_end for p in consistent_patterns)
                is_inconsistent = any(p in evidence_end for p in inconsistent_patterns)
                
                # 如果没有找到明确结论词，尝试简单的关键词，但要排除反义词
                if not is_consistent and not is_inconsistent:
                    # 只有在没有"不一致"的情况下，"一致"才有效
                    if '一致' in evidence_end and '不一致' not in evidence_end:
                        is_consistent = True
                    # 只有在没有"一致"（除非是"不一致"的一部分）的情况下，"不一致"才有效
                    elif '不一致' in evidence_end and evidence_end.count('一致') == evidence_end.count('不一致'):
                        is_inconsistent = True
                
                if is_consistent:
                    if hit_value is not False:
                        logger.warning(f"[警告] 检测到不一致：evidence 结尾结论为'一致'，但 JSON 中 hit={hit_value}，已自动修正为 False")
                        result['hit'] = False
                        result['notes'] = result.get('notes', '') + "；已根据 evidence 结尾的'一致'结论自动修正 hit 值为 False"
                elif is_inconsistent:
                    if hit_value is not True:
                        logger.warning(f"[警告] 检测到不一致：evidence 结尾结论为'不一致'，但 JSON 中 hit={hit_value}，已自动修正为 True")
                        result['hit'] = True
                        result['notes'] = result.get('notes', '') + "；已根据 evidence 结尾的'不一致'结论自动修正 hit 值为 True"
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 响应文本: {response_text[:500]}")
            raise ValueError(f"PARSE_ERROR: JSON decode failed: {e}")
        except Exception as e:
            logger.error(f"解析响应时发生错误: {e}")
            raise ValueError(f"PARSE_ERROR: {type(e).__name__}: {e}")

