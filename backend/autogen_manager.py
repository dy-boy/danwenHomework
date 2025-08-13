"""
AutoGen 代理管理器
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from datetime import datetime

from autogen_core.models import UserMessage, SystemMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import ModelClientStreamingChunkEvent

from config import Config

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL), format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class AutoGenManager:
    """AutoGen 代理管理器"""
    
    def __init__(self):
        self.model_client = None
        self.agents: Dict[str, AssistantAgent] = {}
        self._initialize_model_client()
    
    def _initialize_model_client(self):
        """初始化模型客户端"""
        try:
            self.model_client = OpenAIChatCompletionClient(
                **Config.get_model_config()
            )
            logger.info(f"Model client initialized with model: {Config.MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize model client: {e}")
            raise
    
    def create_agent(self, 
                    name: str = "chat_assistant",
                    system_message: Optional[str] = None,
                    enable_stream: bool = True) -> AssistantAgent:
        """创建AutoGen代理"""
        if not system_message:
            system_message = Config.DEFAULT_SYSTEM_MESSAGE
        
        try:
            agent = AssistantAgent(
                name=name,
                model_client=self.model_client,
                system_message=system_message,
                model_client_stream=enable_stream
            )
            
            # 缓存代理
            agent_key = f"{name}_{hash(system_message)}"
            self.agents[agent_key] = agent
            
            logger.info(f"Created agent: {name}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent {name}: {e}")
            raise
    
    def get_or_create_agent(self, 
                           name: str = "chat_assistant",
                           system_message: Optional[str] = None) -> AssistantAgent:
        """获取或创建代理"""
        if not system_message:
            system_message = Config.DEFAULT_SYSTEM_MESSAGE
            
        agent_key = f"{name}_{hash(system_message)}"
        
        if agent_key in self.agents:
            return self.agents[agent_key]
        
        return self.create_agent(name, system_message)
    
    async def chat_completion(self, 
                             message: str, 
                             system_message: Optional[str] = None) -> str:
        """非流式聊天完成"""
        try:
            if not system_message:
                system_message = Config.DEFAULT_SYSTEM_MESSAGE
            
            messages = [
                SystemMessage(content=system_message),
                UserMessage(content=message, source="user")
            ]
            
            result = await self.model_client.create(messages)
            logger.info(f"Chat completion successful for message: {message[:50]}...")
            return result.content
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def chat_stream(self, 
                         message: str, 
                         system_message: Optional[str] = None,
                         agent_name: str = "chat_assistant") -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天"""
        try:
            agent = self.get_or_create_agent(agent_name, system_message)
            
            logger.info(f"Starting stream chat for message: {message[:50]}...")
            
            # 获取流式结果
            result_stream = agent.run_stream(task=message)
            
            async for chunk in result_stream:
                if isinstance(chunk, ModelClientStreamingChunkEvent):
                    if chunk.content:
                        yield {
                            "type": "content",
                            "content": chunk.content,
                            "timestamp": datetime.now().isoformat()
                        }
            
            # 发送结束信号
            yield {
                "type": "end",
                "content": "",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Stream chat completed successfully")
            
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield {
                "type": "error",
                "content": f"流式聊天出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 简单的健康检查 - 发送一个测试消息
            test_message = "Hello"
            result = await self.chat_completion(test_message, "You are a helpful assistant. Reply with 'OK'.")
            
            return {
                "status": "healthy",
                "model": Config.MODEL_NAME,
                "base_url": Config.BASE_URL,
                "test_response": result[:50] if result else "No response",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_agents_cache(self):
        """清空代理缓存"""
        self.agents.clear()
        logger.info("Agents cache cleared")
    
    def get_agent_count(self) -> int:
        """获取缓存的代理数量"""
        return len(self.agents)

# 全局AutoGen管理器实例
autogen_manager = AutoGenManager()
