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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式，不要添加任何其他内容。"},
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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式，不要添加任何其他内容。"},
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
                {"role": "system", "content": "你是一个专业的银行审计系统，擅长分析银行流水数据并执行合规性检查。你必须严格按照要求返回JSON格式，不要添加任何其他内容。"},
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
        调用 LLM 进行判断，支持备用 provider 和缓存
        
        Args:
            prompt: 提示词
            fallback_providers: 备用 provider 列表，如果主 provider 失败，将依次尝试（如果启用fallback）
            
        Returns:
            判断结果字典，包含 hit, evidence, confidence, notes
        """
        # 如果禁用fallback，只使用配置的provider
        if not self.enable_fallback:
            providers_to_try = [self.provider]
        else:
            # 默认备用 provider 顺序：openai -> deepseek -> authorpic
            if fallback_providers is None:
                fallback_providers = ["openai", "deepseek", "authorpic"]
            providers_to_try = [self.provider] + [p for p in fallback_providers if p != self.provider]
        last_exception = None
        original_provider = self.provider
        original_api_key = self.api_key
        original_model = self.model
        
        # 尝试从缓存加载（缓存键只基于prompt，不依赖provider）
        cached_result = self._try_load_from_any_cache(prompt, providers_to_try)
        if cached_result is not None:
            logger.info(f"从缓存加载结果（prompt hash: {self._get_cache_key(prompt)[:16]}...）")
            return cached_result
        
        # 记录已尝试的provider，确保至少尝试一次每个provider
        attempted_providers = set()
        providers_skipped_due_to_cooldown = []
        
        for provider in providers_to_try:
            # 如果fast_failover启用且provider在冷却期，先跳过但记录
            if self.fast_failover and not self._provider_available(provider):
                providers_skipped_due_to_cooldown.append(provider)
                logger.info(f"Provider {provider} 处于冷却期，稍后重试")
                continue
            
            attempted_providers.add(provider)
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
                
                # 保存到缓存（缓存键只基于prompt）
                cache_key = self._get_cache_key(prompt)
                self._save_to_cache(cache_key, result)
                
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
                
                # 如果禁用fallback，只重试当前provider（在_call_xxx方法中已经处理了重试）
                if not self.enable_fallback:
                    logger.error(f"Provider {provider} 调用失败（已重试 {self.max_retries + 1} 次）: {error_msg}")
                    return {
                        "hit": None,
                        "evidence": f"LLM Provider {provider} 调用失败（已重试 {self.max_retries + 1} 次）。最后错误: {error_msg}。可能是网络连接问题或 API 服务暂时不可用。",
                        "confidence": "low",
                        "notes": f"Provider {provider} 调用失败。建议检查网络连接、API Key配置或稍后重试。如果问题持续，请查看日志获取详细信息。"
                    }
                
                # 如果还有备用 provider，继续尝试
                if provider != providers_to_try[-1]:
                    logger.info(f"尝试下一个备用 Provider...")
                    continue
                # 如果还有在冷却期的provider，强制尝试一次（仅在启用fallback时）
                if self.enable_fallback and providers_skipped_due_to_cooldown and provider == providers_to_try[-1]:
                    logger.warning(f"所有正常provider都失败，强制尝试冷却期中的provider: {providers_skipped_due_to_cooldown}")
                    for skipped_provider in providers_skipped_due_to_cooldown:
                        if skipped_provider in attempted_providers:
                            continue
                        try:
                            logger.info(f"强制尝试 Provider {skipped_provider}（即使处于冷却期）")
                            # 临时切换到该provider
                            self.provider = skipped_provider
                            self.api_key = Config.get_api_key_for_provider(skipped_provider)
                            self.model = Config.get_model_name_for_provider(skipped_provider)
                            if not self.api_key:
                                continue
                            
                            # 调用API
                            if skipped_provider == "openai":
                                response_text = self._call_openai(prompt)
                            elif skipped_provider == "deepseek":
                                response_text = self._call_deepseek(prompt)
                            elif skipped_provider == "authorpic":
                                response_text = self._call_authorpic(prompt)
                            else:
                                continue
                            
                            # 解析响应
                            result = self._parse_response(response_text)
                            
                            # 恢复原始provider
                            self.provider = original_provider
                            self.api_key = original_api_key
                            self.model = original_model
                            
                            # 保存到缓存
                            cache_key = self._get_cache_key(prompt)
                            self._save_to_cache(cache_key, result)
                            
                            logger.info(f"强制尝试成功 (Provider: {skipped_provider}): hit={result.get('hit')}")
                            return result
                        except Exception as e:
                            logger.warning(f"强制尝试 Provider {skipped_provider} 也失败: {e}")
                            # 恢复原始provider
                            self.provider = original_provider
                            self.api_key = original_api_key
                            self.model = original_model
                            continue
                
                # 所有 provider 都失败了
                attempted_list = ', '.join(attempted_providers) if attempted_providers else "无"
                logger.error(f"所有 LLM Provider 都调用失败。已尝试: {attempted_list}")
                return {
                    "hit": None,
                    "evidence": f"所有 LLM Provider 调用失败。最后错误: {error_msg}。可能是网络连接问题或所有 API 服务暂时不可用。",
                    "confidence": "low",
                    "notes": f"已尝试所有可用的 LLM Provider ({attempted_list})，均已失败。建议检查网络连接、API Key配置或稍后重试。"
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
                
                # 如果禁用fallback，直接返回错误
                if not self.enable_fallback:
                    logger.error(f"Provider {provider} 处理错误: {error_type}: {error_msg}")
                    return {
                        "hit": None,
                        "evidence": f"处理错误 ({error_type}): {error_msg}",
                        "confidence": "low",
                        "notes": f"处理过程中发生异常: {error_type}。Provider {provider} 调用失败。建议重新运行程序或检查日志获取详细信息。"
                    }
                
                # 如果还有备用 provider，继续尝试
                if provider != providers_to_try[-1]:
                    logger.info(f"尝试下一个备用 Provider...")
                    continue
                # 如果还有在冷却期的provider，强制尝试一次
                if providers_skipped_due_to_cooldown and provider == providers_to_try[-1]:
                    logger.warning(f"所有正常provider都失败，强制尝试冷却期中的provider: {providers_skipped_due_to_cooldown}")
                    for skipped_provider in providers_skipped_due_to_cooldown:
                        if skipped_provider in attempted_providers:
                            continue
                        try:
                            logger.info(f"强制尝试 Provider {skipped_provider}（即使处于冷却期）")
                            # 临时切换到该provider
                            self.provider = skipped_provider
                            self.api_key = Config.get_api_key_for_provider(skipped_provider)
                            self.model = Config.get_model_name_for_provider(skipped_provider)
                            if not self.api_key:
                                continue
                            
                            # 调用API
                            if skipped_provider == "openai":
                                response_text = self._call_openai(prompt)
                            elif skipped_provider == "deepseek":
                                response_text = self._call_deepseek(prompt)
                            elif skipped_provider == "authorpic":
                                response_text = self._call_authorpic(prompt)
                            else:
                                continue
                            
                            # 解析响应
                            result = self._parse_response(response_text)
                            
                            # 恢复原始provider
                            self.provider = original_provider
                            self.api_key = original_api_key
                            self.model = original_model
                            
                            # 保存到缓存
                            cache_key = self._get_cache_key(prompt)
                            self._save_to_cache(cache_key, result)
                            
                            logger.info(f"强制尝试成功 (Provider: {skipped_provider}): hit={result.get('hit')}")
                            return result
                        except Exception as e:
                            logger.warning(f"强制尝试 Provider {skipped_provider} 也失败: {e}")
                            # 恢复原始provider
                            self.provider = original_provider
                            self.api_key = original_api_key
                            self.model = original_model
                            continue
                
                # 所有 provider 都失败了
                attempted_list = ', '.join(attempted_providers) if attempted_providers else "无"
                logger.error(f"所有 LLM Provider 都调用失败。已尝试: {attempted_list}")
                return {
                    "hit": None,
                    "evidence": f"处理错误 ({error_type}): {error_msg}",
                    "confidence": "low",
                    "notes": f"处理过程中发生异常: {error_type}。已尝试所有可用的 LLM Provider ({attempted_list})。建议重新运行程序或检查日志获取详细信息。"
                }
        
        # 如果所有provider都被跳过（都在冷却期且fast_failover启用），强制尝试一次
        if providers_skipped_due_to_cooldown and not attempted_providers:
            logger.warning(f"所有provider都在冷却期，强制尝试一次: {providers_skipped_due_to_cooldown}")
            for provider in providers_skipped_due_to_cooldown:
                try:
                    logger.info(f"强制尝试 Provider {provider}（即使处于冷却期）")
                    # 临时切换到该provider
                    self.provider = provider
                    self.api_key = Config.get_api_key_for_provider(provider)
                    self.model = Config.get_model_name_for_provider(provider)
                    if not self.api_key:
                        continue
                    
                    # 调用API
                    if provider == "openai":
                        response_text = self._call_openai(prompt)
                    elif provider == "deepseek":
                        response_text = self._call_deepseek(prompt)
                    elif provider == "authorpic":
                        response_text = self._call_authorpic(prompt)
                    else:
                        continue
                    
                    # 解析响应
                    result = self._parse_response(response_text)
                    
                    # 恢复原始provider
                    self.provider = original_provider
                    self.api_key = original_api_key
                    self.model = original_model
                    
                    # 保存到缓存
                    cache_key = self._get_cache_key(prompt)
                    self._save_to_cache(cache_key, result)
                    
                    logger.info(f"强制尝试成功 (Provider: {provider}): hit={result.get('hit')}")
                    return result
                except Exception as e:
                    logger.warning(f"强制尝试 Provider {provider} 失败: {e}")
                    # 恢复原始provider
                    self.provider = original_provider
                    self.api_key = original_api_key
                    self.model = original_model
                    continue
        
        # 理论上不会到达这里，但为了安全起见
        attempted_list = ', '.join(attempted_providers) if attempted_providers else "无"
        logger.error(f"无法调用任何 LLM Provider。已尝试: {attempted_list}")
        return {
            "hit": None,
            "evidence": f"无法调用任何 LLM Provider。已尝试的provider: {attempted_list}",
            "confidence": "low",
            "notes": f"所有 LLM Provider 调用均失败。请检查网络连接、API Key配置或稍后重试。如果问题持续，请查看日志获取详细信息。"
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
                
                # 尝试从文本中提取 confidence
                confidence_value = "low"  # 默认值
                confidence_search_text = search_text[:10000] if 'search_text' in locals() else original_response[:10000] 
                # 通常 confidence 在 evidence 之后，或者在 JSON 结尾。搜索整个文本可能较慢，但对于 regex 还可以。
                # 优先匹配明确的 JSON 字段格式
                confidence_patterns = [
                    r'"confidence"\s*:\s*"(high|medium|low)"',
                    r"'confidence'\s*:\s*'(high|medium|low)'",
                ]
                for pattern in confidence_patterns:
                    match = re.search(pattern, original_response, re.IGNORECASE) # 搜索全文，因为 confidence 可能在最后
                    if match:
                        confidence_value = match.group(1).lower()
                        logger.debug(f"从文本中提取到 confidence: {confidence_value}")
                        break
                
                # 如果没有找到明确的 confidence 字段，但 evidence 很长且 hit 明确，可以提升置信度
                if confidence_value == "low" and hit_value is not None and len(evidence_value) > 1000:
                    logger.debug("Evidence 详实且 hit 明确，提升 fallback 置信度为 medium")
                    confidence_value = "medium"

                # 如果提取到任何信息，返回一个合理的结果
                if hit_value is not None or evidence_value:
                    logger.warning(f"从文本中提取到部分信息: hit={hit_value}, evidence长度={len(evidence_value)}, confidence={confidence_value}")
                    # 确保evidence格式正确（保留换行符等格式）
                    formatted_evidence = evidence_value if evidence_value else "无法完整解析LLM响应，但从文本中提取到部分信息。原始响应已记录在日志中。"
                    
                    return {
                        "hit": hit_value,
                        "evidence": formatted_evidence,
                        "confidence": confidence_value,
                        "notes": "LLM响应包含个别格式问题（如未转义字符），但通过文本分析成功提取了核心结论。"
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
            
            # ⚠️ 关键验证及自动修正：检查 evidence 中的结论与 hit 值是否一致
            # 采用"最后匹配原则" (Last Match Wins)，因为 LLM 通常会在开头复述规则定义 (包含关键词)，而在结尾给出结论
            
            evidence_lower = result.get('evidence', '').lower()
            # 移除 markdown 干扰 (**, `)
            evidence_clean = re.sub(r"[\*`]", "", evidence_lower)
            
            hit_value = result.get('hit')
            detected_hit = None
            
            # 1. 提取明确的 hit=xxx 指令
            # 匹配 hit=true, hit: true, hit is true 等
            # 使用 findall 获取所有匹配，取最后一个作为结论
            hit_patterns = re.findall(r"hit\s*(?:=|:|is)\s*(true|false)", evidence_clean)
            if hit_patterns:
                last_match = hit_patterns[-1]
                if last_match == 'true':
                    detected_hit = True
                elif last_match == 'false':
                    detected_hit = False
            
            # 2. 如果没有明确的 hit=xxx，尝试提取 output/decision 结论
            # 匹配 "输出：不一致", "Result: Inconsistent", "决策结果：异常"
            if detected_hit is None:
                # 扩展关键词映射
                # True (违规): 不一致, inconsistent, 异常, abnormal, 违规
                # False (合规): 一致, consistent, 正常, normal, 合规
                
                # 构建正则：查找 "输出" 或 "结果" 后面紧跟的关键词
                # 允许冒号前后有空格，允许中间有简短的连接词
                conclusion_pattern = re.compile(r"(?:输出|output|result|decision|结果|结论)\s*[:：]\s*.*?(不一致|inconsistent|异常|abnormal|违规|violation|一致|consistent|正常|normal|合规|compliant)")
                
                matches = conclusion_pattern.findall(evidence_clean)
                if matches:
                    last_keyword = matches[-1]
                    if last_keyword in ['不一致', 'inconsistent', '异常', 'abnormal', '违规', 'violation']:
                        detected_hit = True
                    elif last_keyword in ['一致', 'consistent', '正常', 'normal', '合规', 'compliant']:
                        detected_hit = False

            # 3. 执行修正
            if detected_hit is not None and detected_hit != hit_value:
                # 只有当 hit_value 真的不匹配时才修正 (注意区分 None)
                if hit_value is not detected_hit:
                    action = "修正为 True (违规)" if detected_hit else "修正为 False (合规)"
                    logger.warning(f"[系统自动修正] 检测到 Result 不一致: Evidence 结论为 {detected_hit}, 但 JSON hit={hit_value}。正在{action}")
                    
                    result['hit'] = detected_hit
                    note_msg = f"[系统自动修正: 根据Evidence结论 ({'违规' if detected_hit else '合规'}) 强制调整]"
                    
                    if 'notes' not in result or not result['notes']:
                        result['notes'] = note_msg
                    elif note_msg not in result['notes']:
                        result['notes'] += f" {note_msg}"
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 响应文本: {response_text[:500]}")
            raise ValueError(f"PARSE_ERROR: JSON decode failed: {e}")
        except Exception as e:
            logger.error(f"解析响应时发生错误: {e}")
            raise ValueError(f"PARSE_ERROR: {type(e).__name__}: {e}")

