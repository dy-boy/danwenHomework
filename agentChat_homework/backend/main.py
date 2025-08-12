"""
FastAPI主应用 - AutoGen聊天后端服务
"""
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import logging

from config import config
from autogen_service import autogen_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AutoGen Chat API",
    description="基于AutoGen 0.5.7的智能聊天API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有来源，用于调试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    conversation_id: str


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AutoGen Chat API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "autogen-chat-api"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    非流式聊天接口
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
        
        # 生成会话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # 调用AutoGen服务
        response = await autogen_service.chat(request.message)
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求时发生错误: {str(e)}")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口 - 使用SSE协议
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
        
        # 生成会话ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        async def event_generator():
            """SSE事件生成器"""
            try:
                async for chunk in autogen_service.chat_stream(request.message, conversation_id):
                    # 将数据转换为SSE格式
                    data = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    
                # 发送结束信号
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Stream error: {e}")
                error_data = json.dumps({
                    "type": "error",
                    "message": f"流式处理错误: {str(e)}",
                    "conversation_id": conversation_id
                }, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
        
        return EventSourceResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"Stream chat error: {e}")
        raise HTTPException(status_code=500, detail=f"处理流式聊天请求时发生错误: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("AutoGen Chat API starting up...")
    logger.info(f"Model: {config.MODEL_NAME}")
    logger.info(f"Base URL: {config.BASE_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("AutoGen Chat API shutting down...")
    await autogen_service.close()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG,
        log_level="info"
    )
