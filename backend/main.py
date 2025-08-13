import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import Config
from autogen_manager import autogen_manager

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL), format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGen Chat API",
    version="1.0.0",
    description="基于AutoGen 0.5.7的智能对话API"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    **Config.get_cors_config()
)

class ChatRequest(BaseModel):
    message: str
    system_message: str = Config.DEFAULT_SYSTEM_MESSAGE

class ChatResponse(BaseModel):
    response: str

async def generate_stream_response(message: str, system_message: str) -> AsyncGenerator[str, None]:
    """生成流式响应"""
    try:
        logger.info(f"Starting stream response for message: {message[:50]}...")

        async for chunk in autogen_manager.chat_stream(message, system_message):
            # 格式化为SSE格式
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        logger.info("Stream response completed")

    except Exception as e:
        logger.error(f"Stream response error: {e}")
        error_data = {"type": "error", "content": f"错误: {str(e)}"}
        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AutoGen Chat API is running!",
        "version": "1.0.0",
        "model": Config.MODEL_NAME,
        "docs": "/docs"
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """非流式聊天接口"""
    try:
        logger.info(f"Chat request: {request.message[:50]}...")
        result = await autogen_manager.chat_completion(request.message, request.system_message)
        return ChatResponse(response=result)
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """流式聊天接口"""
    logger.info(f"Stream chat request: {request.message[:50]}...")
    return StreamingResponse(
        generate_stream_response(request.message, request.system_message),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        health_info = await autogen_manager.health_check()
        return health_info
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/stats")
async def get_stats():
    """获取统计信息"""
    return {
        "agent_count": autogen_manager.get_agent_count(),
        "model": Config.MODEL_NAME,
        "base_url": Config.BASE_URL
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting AutoGen Chat API server...")
    # 使用字符串形式的应用程序导入路径以支持热重载
    uvicorn.run("main:app", **Config.get_server_config())
