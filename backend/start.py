#!/usr/bin/env python3
"""
AutoGen Chat Backend 启动脚本
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 启动 AutoGen Chat Backend...")
    print("📡 API文档: http://localhost:8000/docs")
    print("🔗 健康检查: http://localhost:8000/health")
    print("💬 聊天接口: http://localhost:8000/chat")
    print("🌊 流式聊天: http://localhost:8000/chat/stream")
    
    uvicorn.run(
        "main:app",  # 使用字符串形式的应用程序导入路径
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
