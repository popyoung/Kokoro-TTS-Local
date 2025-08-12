"""
API测试脚本
用于验证TTS API的各项功能是否正常
"""

import requests
import json
import time
import os

def test_api_health():
    """测试API健康检查"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API健康检查通过")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_get_voices():
    """测试获取语音列表"""
    try:
        response = requests.get("http://localhost:8000/voices")
        if response.status_code == 200:
            voices = response.json()
            print(f"✅ 获取语音列表成功，共{len(voices)}个语音")
            
            # 显示前5个语音
            for i, voice in enumerate(voices[:5]):
                print(f"   {i+1}. {voice['name']} ({voice['language']} - {voice['gender']})")
            
            if len(voices) > 5:
                print(f"   ... 还有{len(voices)-5}个语音")
                
            return voices
        else:
            print(f"❌ 获取语音列表失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 获取语音列表失败: {e}")
        return None

def test_tts_file():
    """测试生成音频文件"""
    test_text = "你好，这是API测试。"
    
    data = {
        "text": test_text,
        "voice": "af_bella",
        "speed": 1.0,
        "format": "wav"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/tts/file",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            filename = "test_output.wav"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ 音频文件生成成功: {filename}")
            return True
        else:
            print(f"❌ 音频文件生成失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 音频文件生成失败: {e}")
        return False

def test_tts_data():
    """测试生成音频数据流"""
    test_text = "Hello, this is a streaming test."
    
    data = {
        "text": test_text,
        "voice": "am_adam",
        "speed": 1.2,
        "format": "mp3"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/tts/data",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            filename = "test_stream.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ 音频数据流生成成功: {filename}")
            return True
        else:
            print(f"❌ 音频数据流生成失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 音频数据流生成失败: {e}")
        return False

def test_tts_save():
    """测试保存到指定路径"""
    test_text = "这是保存到指定路径的测试。"
    
    data = {
        "text": test_text,
        "voice": "zf_xiaoxiao",
        "speed": 0.9,
        "format": "wav",
        "output_path": "test_save.wav"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/tts/save",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 保存到指定路径成功: {result['path']}")
            print(f"   音频时长: {result['duration']:.2f}秒")
            return True
        else:
            print(f"❌ 保存到指定路径失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 保存到指定路径失败: {e}")
        return False

def test_error_cases():
    """测试错误情况"""
    print("\n🧪 测试错误情况...")
    
    # 测试不存在的语音
    data = {
        "text": "测试",
        "voice": "non_existent_voice"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/tts/file",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ 错误处理正常：检测到不存在的语音")
        else:
            print(f"❌ 错误处理异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始API测试...")
    
    # 检查API是否运行
    if not test_api_health():
        print("\n❗ 请确保API服务已启动: python tts_api.py")
        return
    
    # 获取语音列表
    voices = test_get_voices()
    if not voices:
        return
    
    # 运行功能测试
    print("\n🎯 运行功能测试...")
    
    test_results = []
    test_results.append(test_tts_file())
    test_results.append(test_tts_data())
    test_results.append(test_tts_save())
    
    # 测试错误情况
    test_error_cases()
    
    # 总结测试结果
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n📊 测试结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！API运行正常")
    else:
        print("⚠️  部分测试失败，请检查API日志")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n测试已取消")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        # 清理测试文件
        test_files = ["test_output.wav", "test_stream.mp3", "test_save.wav"]
        for file in test_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"清理测试文件: {file}")
                except:
                    pass