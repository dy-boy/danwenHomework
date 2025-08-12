"""
Ollama原生API客户端 - 用于直接调用Ollama API
"""
import asyncio
import json
import httpx
from typing import AsyncGenerator, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama原生API客户端"""
    
    def __init__(self, base_url: str, model: str):
        """
        初始化Ollama客户端
        
        Args:
            base_url: Ollama服务地址，如 http://localhost:11434
            model: 模型名称，如 qwen2.5vl:7B
        """
        self.base_url = base_url.rstrip('/v1').rstrip('/')  # 移除/v1后缀
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat(self, message: str) -> str:
        """
        非流式聊天
        
        Args:
            message: 用户消息
            
        Returns:
            str: AI回复
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": message,
                "stream": False
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """
        流式聊天
        
        Args:
            message: 用户消息
            
        Yields:
            str: 流式回复片段
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": message,
                "stream": True
            }
            
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Ollama stream chat error: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
