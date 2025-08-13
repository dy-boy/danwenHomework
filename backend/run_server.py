#!/usr/bin/env python3
"""
简单的服务器启动脚本（不使用热重载）
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 启动 AutoGen Chat Backend...")
    print("📡 API文档: http://localhost:8000/docs")
    print("🔗 健康检查: http://localhost:8000/health")
    print("💬 聊天接口: http://localhost:8000/chat")
    print("🌊 流式聊天: http://localhost:8000/chat/stream")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        exit(1)
