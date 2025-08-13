#!/usr/bin/env python3
"""
AutoGen Chat API 测试脚本
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

# API配置
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_root_endpoint():
    """测试根路径"""
    print("🔍 测试根路径...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根路径正常: {data}")
            return True
        else:
            print(f"❌ 根路径失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 根路径异常: {e}")
        return False

def test_chat_endpoint():
    """测试非流式聊天接口"""
    print("🔍 测试非流式聊天接口...")
    try:
        payload = {
            "message": "你好，请简单介绍一下你自己",
            "system_message": "你是一个友好的助手"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 聊天接口正常 (耗时: {end_time - start_time:.2f}秒)")
            print(f"📝 回复: {data['response'][:100]}...")
            return True
        else:
            print(f"❌ 聊天接口失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 聊天接口异常: {e}")
        return False

def test_stream_chat_endpoint():
    """测试流式聊天接口"""
    print("🔍 测试流式聊天接口...")
    try:
        payload = {
            "message": "请写一个简单的Python Hello World程序",
            "system_message": "你是一个编程助手"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/chat/stream", 
            json=payload, 
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        if response.status_code == 200:
            print("✅ 流式聊天接口连接成功")
            content_parts = []
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data['type'] == 'content':
                            content_parts.append(data['content'])
                            print(data['content'], end='', flush=True)
                        elif data['type'] == 'end':
                            break
                        elif data['type'] == 'error':
                            print(f"\n❌ 流式错误: {data['content']}")
                            return False
                    except json.JSONDecodeError:
                        continue
            
            end_time = time.time()
            full_content = ''.join(content_parts)
            print(f"\n✅ 流式聊天完成 (耗时: {end_time - start_time:.2f}秒)")
            print(f"📝 完整回复长度: {len(full_content)} 字符")
            return True
        else:
            print(f"❌ 流式聊天接口失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 流式聊天接口异常: {e}")
        return False

def test_stats_endpoint():
    """测试统计信息接口"""
    print("🔍 测试统计信息接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计信息正常: {data}")
            return True
        else:
            print(f"❌ 统计信息失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计信息异常: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行 AutoGen Chat API 测试套件")
    print("=" * 50)
    
    tests = [
        ("根路径", test_root_endpoint),
        ("健康检查", test_health_check),
        ("统计信息", test_stats_endpoint),
        ("非流式聊天", test_chat_endpoint),
        ("流式聊天", test_stream_chat_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 测试:")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # 间隔1秒
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(tests)} 测试通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过！API 运行正常。")
    else:
        print("⚠️  部分测试失败，请检查后端服务。")
    
    return passed == len(tests)

if __name__ == "__main__":
    print("AutoGen Chat API 测试工具")
    print("请确保后端服务已启动 (python backend/start.py)")
    print()
    
    # 等待用户确认
    input("按 Enter 键开始测试...")
    
    success = run_all_tests()
    exit(0 if success else 1)
