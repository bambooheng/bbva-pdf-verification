"""
LLM 判断模块：调用大模型进行语义级匹配与推理
"""
import json
import logging
import requests
from typing import Dict, Any, Optional
import time
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
        
        if not self.api_key:
            raise ValueError(f"未配置 {self.provider.upper()} API Key")
        
        logger.info(f"初始化 LLM 判断器: Provider={self.provider}, Model={self.model}")
    
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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        logger.debug(f"调用 OpenAI API: {self.model}")
        # 使用配置的重试次数，初始尝试 + 重试次数
        max_attempts = 1 if self.fast_failover else (self.max_retries + 1)
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("OpenAI", response)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                last_exception = e
                if attempt < max_attempts - 1 and not self.fast_failover:
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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        logger.debug(f"调用 DeepSeek API: {self.model}")
        # 使用配置的重试次数，初始尝试 + 重试次数
        max_attempts = 1 if self.fast_failover else (self.max_retries + 1)
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("DeepSeek", response)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                last_exception = e
                if attempt < max_attempts - 1 and not self.fast_failover:
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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        logger.debug(f"调用 Authorpic API: {self.model}")
        # 使用配置的重试次数，初始尝试 + 重试次数
        max_attempts = 1 if self.fast_failover else (self.max_retries + 1)
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
                if response.status_code in (401, 403, 429):
                    self._handle_http_error("Authorpic", response)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                if attempt < max_attempts - 1 and not self.fast_failover:
                    wait_time = min(4 * (2 ** attempt), 60)  # 指数退避，最多等待60秒
                    logger.warning(f"Authorpic API 调用失败 (尝试 {attempt + 1}/{max_attempts}): {str(e)}，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Authorpic API 调用失败 (已重试 {max_attempts} 次): {str(e)}")
                    raise
    
    def judge(self, prompt: str, fallback_providers: list = None) -> Dict[str, Any]:
        """
        调用 LLM 进行判断，支持备用 provider
        
        Args:
            prompt: 提示词
            fallback_providers: 备用 provider 列表，如果主 provider 失败，将依次尝试
            
        Returns:
            判断结果字典，包含 hit, evidence, confidence, notes
        """
        # 默认备用 provider 顺序：openai -> deepseek -> authorpic
        if fallback_providers is None:
            fallback_providers = ["openai", "deepseek", "authorpic"]
        
        providers_to_try = [self.provider] + [p for p in fallback_providers if p != self.provider]
        last_exception = None
        original_provider = self.provider
        original_api_key = self.api_key
        original_model = self.model
        
        for provider in providers_to_try:
            if self.fast_failover and not self._provider_available(provider):
                logger.info(f"跳过 Provider {provider}（处于冷却期，加速降级）")
                continue
            try:
                logger.info(f"尝试使用 LLM Provider: {provider}")
                
                # 临时切换到备用 provider
                if provider != original_provider:
                    self.provider = provider
                    self.api_key = Config.get_api_key_for_provider(provider)
                    self.model = Config.get_model_name_for_provider(provider)
                    if not self.api_key:
                        logger.warning(f"备用 Provider {provider} 未配置 API Key，跳过")
                        continue
                    logger.info(f"切换到备用 Provider: {provider}, Model: {self.model}")
                
                parse_attempts = 0
                while True:
                    # 根据 provider 选择对应的 API
                    if provider == "openai":
                        response_text = self._call_openai(prompt)
                    elif provider == "deepseek":
                        response_text = self._call_deepseek(prompt)
                    elif provider == "authorpic":
                        response_text = self._call_authorpic(prompt)
                    else:
                        raise ValueError(f"不支持的 LLM Provider: {provider}")
                    
                    logger.debug(f"LLM 原始响应: {response_text[:200]}...")
                    
                    try:
                        # 尝试解析 JSON 响应
                        result = self._parse_response(response_text)
                    except ValueError as parse_err:
                        error_msg = str(parse_err)
                        if "PARSE_ERROR" in error_msg and parse_attempts < self.max_parse_retries:
                            parse_attempts += 1
                            logger.warning(
                                f"Provider {provider} 响应解析失败（尝试 {parse_attempts}/{self.max_parse_retries}），准备重新请求..."
                            )
                            continue
                        raise
                    break
                
                # 恢复原始 provider（如果使用了备用）
                if provider != original_provider:
                    self.provider = original_provider
                    self.api_key = original_api_key
                    self.model = original_model
                    if result.get('notes'):
                        result['notes'] += f"；使用了备用 Provider: {provider}"
                    else:
                        result['notes'] = f"使用了备用 Provider: {provider}"
                # 成功后移除冷却状态
                if provider in self.failed_providers:
                    self.failed_providers.pop(provider, None)
                
                # 记录 LLM 请求和响应（用于审计回溯）
                logger.info(f"LLM 判断完成 (Provider: {provider}): hit={result.get('hit')}, confidence={result.get('confidence')}")
                
                return result
            
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError) as e:
                last_exception = e
                error_msg = str(e)
                logger.warning(f"Provider {provider} 调用失败: {error_msg}")
                if self.fast_failover:
                    self._mark_provider_failed(provider)
                # 恢复原始 provider
                self.provider = original_provider
                self.api_key = original_api_key
                self.model = original_model
                # 如果还有备用 provider，继续尝试
                if provider != providers_to_try[-1]:
                    logger.info(f"尝试下一个备用 Provider...")
                    continue
                # 所有 provider 都失败了
                logger.error(f"所有 LLM Provider 都调用失败 (已重试 {self.max_retries + 1} 次)")
                return {
                    "hit": None,
                    "evidence": f"所有 LLM Provider 调用失败。最后错误: {error_msg}。可能是网络连接问题或所有 API 服务暂时不可用。",
                    "confidence": "low",
                    "notes": f"已尝试所有可用的 LLM Provider ({', '.join(providers_to_try)})，均已失败。建议检查网络连接或稍后重试。"
                }
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                error_type = type(e).__name__
                logger.error(f"LLM 判断时发生错误 ({error_type}): {error_msg}")
                if self.fast_failover:
                    self._mark_provider_failed(provider)
                # 恢复原始 provider
                self.provider = original_provider
                self.api_key = original_api_key
                self.model = original_model
                # 如果还有备用 provider，继续尝试
                if provider != providers_to_try[-1]:
                    logger.info(f"尝试下一个备用 Provider...")
                    continue
                # 所有 provider 都失败了
                return {
                    "hit": None,
                    "evidence": f"处理错误 ({error_type}): {error_msg}",
                    "confidence": "low",
                    "notes": f"处理过程中发生异常: {error_type}。已尝试所有可用的 LLM Provider。建议重新运行程序或检查日志获取详细信息。"
                }
        
        # 理论上不会到达这里，但为了安全起见
        return {
            "hit": None,
            "evidence": f"无法调用任何 LLM Provider",
            "confidence": "low",
            "notes": "所有 LLM Provider 调用均失败"
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
            # 查找 JSON 代码块
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            else:
                # 尝试直接查找 JSON 对象
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_text = response_text[start:end]
                else:
                    raise ValueError("未找到 JSON 格式")
            
            result = json.loads(json_text)
            
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
            
            # 检查 evidence 中是否明确说明了 hit 值
            if '对应的 hit 值：false' in evidence or 'hit 值：false' in evidence or 'hit=false' in evidence:
                if hit_value is not False:
                    logger.warning(f"[警告] 检测到不一致：evidence 中说 hit=False，但 JSON 中 hit={hit_value}，已自动修正为 False")
                    result['hit'] = False
                    if 'notes' not in result or not result['notes']:
                        result['notes'] = "已根据 evidence 中的结论自动修正 hit 值"
                    elif "已根据 evidence" not in result['notes']:
                        result['notes'] += "；已根据 evidence 中的结论自动修正 hit 值"
            elif '对应的 hit 值：true' in evidence or 'hit 值：true' in evidence or 'hit=true' in evidence:
                if hit_value is not True:
                    logger.warning(f"[警告] 检测到不一致：evidence 中说 hit=True，但 JSON 中 hit={hit_value}，已自动修正为 True")
                    result['hit'] = True
                    if 'notes' not in result or not result['notes']:
                        result['notes'] = "已根据 evidence 中的结论自动修正 hit 值"
                    elif "已根据 evidence" not in result['notes']:
                        result['notes'] += "；已根据 evidence 中的结论自动修正 hit 值"
            
            # 检查 evidence 中是否说"一致"或"不一致"
            if '一致' in evidence and '不一致' not in evidence:
                # 如果 evidence 中说"一致"，hit 应该是 False
                if hit_value is not False:
                    logger.warning(f"[警告] 检测到不一致：evidence 中说'一致'，但 JSON 中 hit={hit_value}，已自动修正为 False")
                    result['hit'] = False
                    if 'notes' not in result or not result['notes']:
                        result['notes'] = "已根据 evidence 中的'一致'结论自动修正 hit 值为 False"
                    elif "已根据 evidence" not in result['notes']:
                        result['notes'] += "；已根据 evidence 中的'一致'结论自动修正 hit 值为 False"
            elif '不一致' in evidence and '一致' not in evidence:
                # 如果 evidence 中说"不一致"，hit 应该是 True
                if hit_value is not True:
                    logger.warning(f"[警告] 检测到不一致：evidence 中说'不一致'，但 JSON 中 hit={hit_value}，已自动修正为 True")
                    result['hit'] = True
                    if 'notes' not in result or not result['notes']:
                        result['notes'] = "已根据 evidence 中的'不一致'结论自动修正 hit 值为 True"
                    elif "已根据 evidence" not in result['notes']:
                        result['notes'] += "；已根据 evidence 中的'不一致'结论自动修正 hit 值为 True"
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 响应文本: {response_text[:500]}")
            raise ValueError(f"PARSE_ERROR: JSON decode failed: {e}")
        except Exception as e:
            logger.error(f"解析响应时发生错误: {e}")
            raise ValueError(f"PARSE_ERROR: {type(e).__name__}: {e}")

