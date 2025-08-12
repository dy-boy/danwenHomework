"""
AutoGen服务模块 - 处理与AutoGen agent的交互
"""
import asyncio
from typing import AsyncGenerator, Dict, Any
from autogen_core.models import SystemMessage, ModelFamily
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from config import config
from ollama_client import OllamaClient
import logging

logger = logging.getLogger(__name__)


class AutoGenService:
    """AutoGen聊天服务"""

    def __init__(self):
        """初始化AutoGen服务"""
        self.model_client = None
        self.agent = None
        self.ollama_client = None
        self.use_ollama = False
        self._initialize_agent()
    
    def _initialize_agent(self):
        """初始化AutoGen agent"""
        try:
            # 检查是否使用本地Ollama
            if "localhost:11434" in config.BASE_URL:
                self.use_ollama = True
                self.ollama_client = OllamaClient(
                    base_url=config.BASE_URL,
                    model=config.MODEL_NAME
                )
                logger.info(f"Using Ollama native API: {config.MODEL_NAME}")
            else:
                # 使用OpenAI兼容的API
                self.model_client = OpenAIChatCompletionClient(
                    model=config.MODEL_NAME,
                    base_url=config.BASE_URL,
                    api_key=config.API_KEY,
                    model_info=config.MODEL_INFO
                )

                # 创建助手agent
                self.agent = AssistantAgent(
                    name="chat_assistant",
                    model_client=self.model_client,
                    system_message="你是一个智能助手，能够帮助用户解答各种问题。请用中文回答，保持友好和专业的语调。",
                    model_client_stream=True,  # 启用流式输出
                )
                logger.info(f"Using OpenAI-compatible API: {config.MODEL_NAME}")

            logger.info("Service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize service: {e}")
            raise
    
    async def chat_stream(self, message: str, conversation_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式聊天方法

        Args:
            message: 用户消息
            conversation_id: 会话ID（可选）

        Yields:
            Dict: 包含消息内容的字典
        """
        try:
            # 发送开始信号
            yield {
                "type": "start",
                "message": "开始处理您的请求...",
                "conversation_id": conversation_id
            }

            if self.use_ollama:
                # 使用Ollama原生API
                full_response = ""
                async for chunk in self.ollama_client.chat_stream(message):
                    full_response += chunk
                    yield {
                        "type": "message",
                        "content": full_response,
                        "conversation_id": conversation_id
                    }
            else:
                # 使用AutoGen agent进行流式对话
                if not self.agent:
                    raise Exception("AutoGen agent not initialized")

                stream = self.agent.run_stream(task=message)

                async for chunk in stream:
                    # 处理不同类型的消息
                    if hasattr(chunk, 'messages') and chunk.messages:
                        latest_message = chunk.messages[-1]
                        if hasattr(latest_message, 'content') and latest_message.content:
                            yield {
                                "type": "message",
                                "content": latest_message.content,
                                "conversation_id": conversation_id
                            }
                    elif hasattr(chunk, 'content') and chunk.content:
                        yield {
                            "type": "message",
                            "content": chunk.content,
                            "conversation_id": conversation_id
                        }

            # 发送结束信号
            yield {
                "type": "end",
                "message": "回答完成",
                "conversation_id": conversation_id
            }

        except Exception as e:
            logger.error(f"Error in chat_stream: {e}")
            yield {
                "type": "error",
                "message": f"处理请求时发生错误: {str(e)}",
                "conversation_id": conversation_id
            }
    
    async def chat(self, message: str) -> str:
        """
        非流式聊天方法

        Args:
            message: 用户消息

        Returns:
            str: AI回复
        """
        try:
            if self.use_ollama:
                # 使用Ollama原生API
                return await self.ollama_client.chat(message)
            else:
                # 使用AutoGen agent
                if not self.agent:
                    raise Exception("AutoGen agent not initialized")

                result = await self.agent.run(task=message)

                # 提取回复内容
                if hasattr(result, 'messages') and result.messages:
                    return result.messages[-1].content
                elif hasattr(result, 'content'):
                    return result.content
                else:
                    return str(result)

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"抱歉，处理您的请求时发生了错误: {str(e)}"
    
    async def close(self):
        """关闭服务，清理资源"""
        try:
            if self.ollama_client:
                await self.ollama_client.close()
            if self.model_client:
                await self.model_client.close()
            logger.info("Service closed successfully")
        except Exception as e:
            logger.error(f"Error closing service: {e}")


# 全局服务实例
autogen_service = AutoGenService()
