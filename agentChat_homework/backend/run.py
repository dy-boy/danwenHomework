"""
启动脚本 - 运行AutoGen聊天后端服务
"""
import uvicorn
from config import config

if __name__ == "__main__":
    print("🚀 Starting AutoGen Chat Backend...")
    print(f"📡 Server: http://{config.API_HOST}:{config.API_PORT}")
    print(f"📚 API Docs: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"🤖 Model: {config.MODEL_NAME}")
    
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG,
        log_level="info"
    )
