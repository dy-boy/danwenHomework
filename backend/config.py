"""
AutoGen Chat 配置文件
"""

import os
from typing import Dict, Any
from autogen_core.models import ModelFamily

class Config:
    """应用配置类"""
    
    # API 配置
    API_KEY = "sk-dc3c24db09fe4fd383c0a198dda84e0e"
    BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    MODEL_NAME = "deepseek-r1"
    
    # 服务器配置
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = True
    RELOAD = True
    
    # CORS 配置
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # AutoGen 模型配置
    MODEL_INFO = {
        "vision": True,
        "function_calling": True,
        "json_output": True,
        "family": ModelFamily.UNKNOWN,
        "structured_output": False,
        "multiple_system_messages": False,
    }
    
    # 默认系统消息
    DEFAULT_SYSTEM_MESSAGE = """你是一个智能助手，能够帮助用户解答各种问题。
请遵循以下原则：
1. 用中文回答问题
2. 回答要详细且有帮助
3. 如果不确定答案，请诚实说明
4. 保持友好和专业的语调
5. 对于编程问题，提供清晰的代码示例
6. 对于复杂问题，分步骤解释"""
    
    # 流式输出配置
    STREAM_CHUNK_SIZE = 1024
    STREAM_TIMEOUT = 30
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            "model": cls.MODEL_NAME,
            "base_url": cls.BASE_URL,
            "api_key": cls.API_KEY,
            "model_info": cls.MODEL_INFO
        }
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "reload": cls.RELOAD,
            "log_level": cls.LOG_LEVEL
        }
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """获取CORS配置"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": cls.CORS_CREDENTIALS,
            "allow_methods": cls.CORS_METHODS,
            "allow_headers": cls.CORS_HEADERS
        }

# 环境变量配置（可选）
def load_env_config():
    """从环境变量加载配置"""
    Config.API_KEY = os.getenv("AUTOGEN_API_KEY", Config.API_KEY)
    Config.BASE_URL = os.getenv("AUTOGEN_BASE_URL", Config.BASE_URL)
    Config.MODEL_NAME = os.getenv("AUTOGEN_MODEL_NAME", Config.MODEL_NAME)
    Config.HOST = os.getenv("SERVER_HOST", Config.HOST)
    Config.PORT = int(os.getenv("SERVER_PORT", Config.PORT))
    Config.DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# 加载环境变量配置
load_env_config()
