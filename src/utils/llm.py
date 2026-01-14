"""
LLM 多模型客户端

支持 OpenAI、Anthropic、Google 三大协议，
请求随机分配到模型，失败自动降级。

使用示例：
    from src.utils.llm import llm_chat
    
    # 简单调用
    response = await llm_chat("你好，请介绍一下自己")
    
    # 带系统提示
    response = await llm_chat(
        "帮我查一下唐门在电五的奇遇", 
        system="你是一个游戏助手"
    )
    
    # 完整消息列表
    response = await llm_chat([
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ])
"""

from dataclasses import dataclass
from typing import Any
from nonebot.log import logger

import random
import time
import httpx

from src.config import Config, LLMProvider, LLMModelRef


@dataclass
class ResolvedModel:
    """解析后的模型配置，合并了 Provider 信息"""
    name: str
    protocol: str
    api_key: str
    base_url: str
    timeout: int


class LLMClient:
    """多模型 LLM 客户端，支持随机分配和降级"""
    
    # 各协议的默认端点
    DEFAULT_ENDPOINTS = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "anthropic": "https://api.anthropic.com/v1/messages",
        "google": "https://generativelanguage.googleapis.com/v1beta",
    }
    
    def __init__(
        self, 
        providers: list[LLMProvider], 
        models: list[LLMModelRef], 
        max_timeout: int = 300
    ):
        self.max_timeout = max_timeout
        
        # 构建 provider 查找表
        self._providers: dict[str, LLMProvider] = {p.name: p for p in providers}
        
        # 解析并验证 models
        self._models: list[ResolvedModel] = []
        for model in models:
            provider = self._providers.get(model.provider)
            if provider and provider.api_key:
                self._models.append(ResolvedModel(
                    name=model.name,
                    protocol=provider.protocol,
                    api_key=provider.api_key,
                    base_url=provider.base_url,
                    timeout=model.timeout
                ))
    
    @property
    def available(self) -> bool:
        """是否有可用模型"""
        return len(self._models) > 0
    
    async def chat(
        self, 
        messages: list[dict[str, str]] | str, 
        system: str | None = None,
        **kwargs
    ) -> str:
        """
        发起 LLM 请求，随机分配模型，失败自动降级
        
        Args:
            messages: 消息列表或单条用户消息字符串
            system: 系统提示（可选）
            **kwargs: 额外参数传递给 API
        
        Returns:
            LLM 生成的回复文本
        
        Raises:
            RuntimeError: 所有模型均请求失败
            TimeoutError: 超过最大超时时间
        """
        if not self.available:
            raise RuntimeError("没有可用的 LLM 模型，请检查配置")
        
        # 标准化消息格式
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        if system:
            messages = [{"role": "system", "content": system}] + messages
        
        # 随机打乱模型顺序
        shuffled = random.sample(self._models, len(self._models))
        start_time = time.time()
        last_error: Exception | None = None
        
        for model in shuffled:
            elapsed = time.time() - start_time
            if elapsed >= self.max_timeout:
                raise TimeoutError(f"所有模型请求超时（累计 {elapsed:.1f}s）")
            
            remaining = min(model.timeout, self.max_timeout - elapsed)
            if remaining <= 0:
                continue
            
            try:
                logger.debug(f"尝试使用模型 {model.name} ({model.protocol})")
                result = await self._call(model, messages, timeout=remaining, **kwargs)
                logger.debug(f"模型 {model.name} 请求成功")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"模型 {model.name} 请求失败: {e}")
                continue
        
        raise RuntimeError(f"所有模型均请求失败，最后错误: {last_error}")
    
    async def _call(
        self, 
        model: ResolvedModel, 
        messages: list[dict[str, str]], 
        timeout: float,
        **kwargs
    ) -> str:
        """根据协议调用对应 API"""
        match model.protocol:
            case "openai":
                return await self._call_openai(model, messages, timeout, **kwargs)
            case "anthropic":
                return await self._call_anthropic(model, messages, timeout, **kwargs)
            case "google":
                return await self._call_google(model, messages, timeout, **kwargs)
            case _:
                raise ValueError(f"不支持的协议: {model.protocol}")
    
    async def _call_openai(
        self, 
        model: ResolvedModel, 
        messages: list[dict[str, str]], 
        timeout: float,
        **kwargs
    ) -> str:
        """OpenAI 协议调用"""
        url = model.base_url or self.DEFAULT_ENDPOINTS["openai"]
        if not url.endswith("/chat/completions"):
            url = url.rstrip("/") + "/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model.name,
            "messages": messages,
            **kwargs
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_anthropic(
        self, 
        model: ResolvedModel, 
        messages: list[dict[str, str]], 
        timeout: float,
        **kwargs
    ) -> str:
        """Anthropic 协议调用"""
        url = model.base_url or self.DEFAULT_ENDPOINTS["anthropic"]
        if not url.endswith("/messages"):
            url = url.rstrip("/") + "/messages"
        
        headers = {
            "x-api-key": model.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        
        # Anthropic 的 system 消息需要单独传递
        system_content = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"
            else:
                filtered_messages.append(msg)
        
        payload: dict[str, Any] = {
            "model": model.name,
            "messages": filtered_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            **kwargs
        }
        
        if system_content:
            payload["system"] = system_content.strip()
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    async def _call_google(
        self, 
        model: ResolvedModel, 
        messages: list[dict[str, str]], 
        timeout: float,
        **kwargs
    ) -> str:
        """Google Generative AI 协议调用"""
        base_url = model.base_url or self.DEFAULT_ENDPOINTS["google"]
        url = f"{base_url.rstrip('/')}/models/{model.name}:generateContent?key={model.api_key}"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # 转换消息格式为 Google 格式
        contents = []
        system_instruction = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = {"parts": [{"text": msg["content"]}]}
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        
        payload: dict[str, Any] = {
            "contents": contents,
            **kwargs
        }
        
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


# 全局客户端实例（延迟初始化）
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端实例"""
    global _client
    if _client is None:
        _client = LLMClient(
            providers=Config.llm.providers,
            models=Config.llm.models,
            max_timeout=Config.llm.max_timeout
        )
    return _client


async def llm_chat(
    messages: list[dict[str, str]] | str,
    system: str | None = None,
    **kwargs
) -> str:
    """
    便捷的 LLM 调用函数
    
    使用示例:
        # 简单调用
        response = await llm_chat("你好")
        
        # 带系统提示
        response = await llm_chat("帮我写代码", system="你是编程助手")
    
    Args:
        messages: 消息列表或单条用户消息
        system: 系统提示
        **kwargs: 额外参数
    
    Returns:
        LLM 回复文本
    """
    if not Config.llm.enable:
        raise RuntimeError("LLM 功能未启用，请在配置文件中设置 llm.enable: True")
    
    client = get_llm_client()
    return await client.chat(messages, system=system, **kwargs)
