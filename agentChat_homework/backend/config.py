"""
配置文件 - 包含所有系统配置
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """应用配置类"""
    
    # API配置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # 模型配置
    MODEL_NAME: str = os.getenv("MODEL_NAME", "qwen-plus")
    BASE_URL: str = os.getenv("BASE_URL", "https://api-inference.modelscope.cn/v1/")
    API_KEY: str = os.getenv("API_KEY", "")
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    # AutoGen模型信息配置
    MODEL_INFO = {
        "vision": False,
        "function_calling": True,
        "family": "unknown",
        "json_output": True,
        "structured_output": False
    }


# 全局配置实例
config = Config()
