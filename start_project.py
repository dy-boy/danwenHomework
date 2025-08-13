#!/usr/bin/env python3
"""
AutoGen Chat 项目启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 AutoGen Chat 项目                      ║
    ║                                                              ║
    ║  基于 AutoGen 0.5.7 的智能对话应用                           ║
    ║  前端: 炫酷的 Gemini 风格界面                                ║
    ║  后端: FastAPI + SSE 流式输出                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """检查依赖"""
    print("🔍 检查项目依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 检查必要的包
    required_packages = [
        'fastapi',
        'uvicorn',
        'autogen_agentchat',
        'autogen_core',
        'autogen_ext'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend 目录不存在")
        return None
    
    try:
        # 启动后端服务
        process = subprocess.Popen(
            [sys.executable, "start.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("✅ 后端服务启动中...")
        print("📡 API 地址: http://localhost:8000")
        print("📚 API 文档: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ 启动后端失败: {e}")
        return None

def wait_for_backend():
    """等待后端服务启动"""
    print("\n⏳ 等待后端服务启动...")
    
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ 后端服务已就绪")
                return True
        except:
            pass
        
        print(f"⏳ 等待中... ({i+1}/{max_attempts})")
        time.sleep(1)
    
    print("❌ 后端服务启动超时")
    return False

def open_frontend():
    """打开前端界面"""
    print("\n🌐 打开前端界面...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend 目录不存在")
        return False
    
    index_file = frontend_dir / "index.html"
    test_file = frontend_dir / "test.html"
    
    if index_file.exists():
        file_url = f"file://{index_file.absolute()}"
        print(f"🎨 主界面: {file_url}")
        webbrowser.open(file_url)
    
    if test_file.exists():
        test_url = f"file://{test_file.absolute()}"
        print(f"🧪 测试页面: {test_url}")
        # webbrowser.open(test_url)  # 可选择是否自动打开测试页面
    
    return True

def run_tests():
    """运行测试"""
    print("\n🧪 是否运行API测试? (y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes', '是']:
        test_script = Path("backend/test_api.py")
        if test_script.exists():
            try:
                subprocess.run([sys.executable, str(test_script)], check=True)
            except subprocess.CalledProcessError:
                print("❌ 测试失败")
        else:
            print("❌ 测试脚本不存在")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的包后重试")
        return
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ 后端启动失败")
        return
    
    try:
        # 等待后端就绪
        if not wait_for_backend():
            print("\n❌ 后端服务未能正常启动")
            return
        
        # 打开前端
        open_frontend()
        
        print("\n" + "="*60)
        print("🎉 项目启动成功!")
        print("📱 前端界面已在浏览器中打开")
        print("🔗 后端API: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("🧪 测试页面: frontend/test.html")
        print("="*60)
        
        # 可选运行测试
        run_tests()
        
        print("\n💡 提示:")
        print("- 按 Ctrl+C 停止服务")
        print("- 查看 README.md 了解更多信息")
        print("- 如有问题，请检查后端日志")
        
        # 保持运行
        print("\n🔄 服务运行中，按 Ctrl+C 停止...")
        backend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ 服务已停止")
    
    except Exception as e:
        print(f"\n❌ 运行时错误: {e}")
        backend_process.terminate()

if __name__ == "__main__":
    main()
