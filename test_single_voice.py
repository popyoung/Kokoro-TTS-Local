#!/usr/bin/env python3
"""
测试单个朗读者功能的测试脚本
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path

# API服务器地址
API_BASE_URL = "http://localhost:8000"

async def test_multiple_single_voices():
    """测试多个单个朗读者轮流使用功能"""
    
    async with aiohttp.ClientSession() as session:
        print("=== 测试多个朗读者轮流使用功能 ===")
        
        # 测试文本
        text = "Hello, this is a test of multiple voice selection."
        
        # 定义多个朗读者
        voices = ["af_bella", "af_nicole", "am_adam"]
        
        print(f"测试文本: {text}")
        print(f"朗读者列表: {voices}")
        print("注意: 朗读者选择现在由前端JS完成，这里模拟前端随机选择")
        print()
        
        # 测试多次调用，使用不同的朗读者
        for i, voice in enumerate(voices):
            print(f"测试 {i+1} - 使用朗读者: {voice}:")
            
            # 准备请求数据（单个voice）
            payload = {
                "text": text,
                "voice": voice,
                "speed": 1.0,
                "format": "wav"
            }
            
            try:
                # 调用API
                async with session.post(f"{API_BASE_URL}/tts/data", json=payload) as response:
                    if response.status == 200:
                        # 获取响应头中的信息
                        content_disposition = response.headers.get('Content-Disposition', '')
                        print(f"  响应状态: 200 OK")
                        print(f"  Content-Disposition: {content_disposition}")
                        
                        # 保存音频文件
                        filename = f"test_multi_voices_{i+1}.wav"
                        with open(filename, 'wb') as f:
                            f.write(await response.read())
                        print(f"  音频已保存: {filename}")
                        
                    else:
                        error_text = await response.text()
                        print(f"  响应状态: {response.status}")
                        print(f"  错误信息: {error_text}")
                        
            except Exception as e:
                print(f"  错误: {str(e)}")
            
            print()

async def test_single_voice():
    """测试单个朗读者（向后兼容）"""
    
    async with aiohttp.ClientSession() as session:
        print("=== 测试单个朗读者（向后兼容） ===")
        
        payload = {
            "text": "This is a test with single voice selection.",
            "voice": "af_bella",  # 使用单个voice参数
            "speed": 1.0,
            "format": "wav"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/tts/data", json=payload) as response:
                if response.status == 200:
                    filename = "test_single_voice.wav"
                    with open(filename, 'wb') as f:
                        f.write(await response.read())
                    print(f"音频已保存: {filename}")
                else:
                    error_text = await response.text()
                    print(f"错误: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"错误: {str(e)}")
        
        print()

async def test_invalid_voice():
    """测试无效朗读者处理"""
    
    async with aiohttp.ClientSession() as session:
        print("=== 测试无效朗读者处理 ===")
        
        payload = {
            "text": "Test with invalid voice.",
            "voice": "invalid_voice",
            "speed": 1.0,
            "format": "wav"
        }
        
        try:
            async with session.post(f"{API_BASE_URL}/tts/data", json=payload) as response:
                error_text = await response.text()
                print(f"响应状态: {response.status}")
                print(f"错误信息: {error_text}")
                
        except Exception as e:
            print(f"错误: {str(e)}")
        
        print()



async def main():
    """主测试函数"""
    
    # 检查API服务器是否运行
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status != 200:
                    print("警告: API服务器可能未运行，请确保 tts_api.py 正在运行")
                    return
    except Exception as e:
        print(f"错误: 无法连接到API服务器，请确保 tts_api.py 正在运行")
        print(f"错误详情: {str(e)}")
        return
    
    # 运行所有测试
    await test_multiple_single_voices()
    await test_single_voice()
    await test_invalid_voice()
    
    print("所有测试完成！")
    print("生成的测试文件:")
    
    # 列出生成的文件
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.wav')]
    for file in test_files:
        print(f"  - {file}")

if __name__ == "__main__":
    asyncio.run(main())