# Kokoro TTS API 使用说明

## 简介
Kokoro TTS API 是一个基于FastAPI的RESTful接口，提供文本转语音功能。支持多种语言和语音选择，可以输出音频文件或音频数据流。

## 快速开始

### 1. 启动API服务
```bash
# 安装依赖
pip install fastapi uvicorn

# 启动服务
python tts_api.py

# 或使用uvicorn命令
uvicorn tts_api:app --host 0.0.0.0 --port 8000
```

服务启动后，访问 http://localhost:8000/docs 查看交互式API文档。

### 2. 获取可用语音列表
```bash
curl -X GET "http://localhost:8000/voices"
```

响应示例：
```json
[
  {
    "name": "af_bella",
    "language": "American English",
    "gender": "Female"
  },
  {
    "name": "am_adam",
    "language": "American English",
    "gender": "Male"
  }
]
```

### 3. 文本转语音 - 返回音频文件
```bash
curl -X POST "http://localhost:8000/tts/file" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试。",
    "voice": "af_bella",
    "speed": 1.0,
    "format": "wav"
  }' \
  --output output.wav
```

### 4. 文本转语音 - 返回音频数据流
```bash
curl -X POST "http://localhost:8000/tts/data" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice": "am_adam",
    "speed": 1.2,
    "format": "mp3"
  }' \
  --output output.mp3
```

### 5. 文本转语音 - 保存到指定路径
```bash
curl -X POST "http://localhost:8000/tts/save" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一个保存到指定路径的测试。",
    "voice": "zf_xiaoxiao",
    "speed": 0.9,
    "format": "wav",
    "output_path": "/tmp/test_output.wav"
  }'
```

### 6. 使用多个朗读者随机选择
```bash
# 从多个朗读者中随机选择一个
curl -X POST "http://localhost:8000/tts/file" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test with multiple voice selection.",
    "voices": ["af_bella", "af_nicole", "am_adam"],
    "speed": 1.0,
    "format": "wav"
  }' \
  --output random_voice_test.wav
```

## Python调用示例

### 使用requests库
```python
import requests
import json

# 获取语音列表
response = requests.get("http://localhost:8000/voices")
voice_list = response.json()
print("可用语音:", voice_list)

# 生成语音并保存文件
data = {
    "text": "你好，欢迎使用Kokoro TTS API！",
    "voice": "af_bella",
    "speed": 1.0,
    "format": "wav"
}

response = requests.post(
    "http://localhost:8000/tts/file",
    json=data,
    headers={"Content-Type": "application/json"}
)

with open("output.wav", "wb") as f:
    f.write(response.content)

print("音频文件已保存为 output.wav")
```

### 使用aiohttp库（异步）
```python
import aiohttp
import asyncio

async def generate_speech():
    async with aiohttp.ClientSession() as session:
        data = {
            "text": "这是异步调用示例",
            "voice": "am_adam",
            "speed": 1.1,
            "format": "mp3"
        }
        
        async with session.post(
            "http://localhost:8000/tts/data",
            json=data,
            headers={"Content-Type": "application/json"}
        ) as response:
            audio_data = await response.read()
            
            with open("async_output.mp3", "wb") as f:
                f.write(audio_data)
            
            print("异步音频文件已保存")

# 运行异步函数
asyncio.run(generate_speech())
```

## 参数说明

### TTSRequest参数

| 参数名 | 类型 | 默认值 | 说明 | 限制 |
|--------|------|--------|------|------|
| text | string | 必填 | 要转换的文本 | 最大长度10000字符 |
| voice | string | "af_bella" | 单个语音选择 | 需为可用语音名称 |
| voices | array | - | 多个语音选择列表，随机选择一个使用。优先级高于voice参数 | 需为可用语音名称列表 |
| speed | float | 1.0 | 语速 | 0.1-3.0 |
| format | string | "wav" | 输出格式 | "wav", "mp3", "aac" |
| sample_rate | int | 24000 | 采样率 | 16000, 22050, 24000, 44100, 48000 |

### 可用语音

#### 美式英语
- **女性**: af_heart, af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky
- **男性**: am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa

#### 英式英语
- **女性**: bf_alice, bf_emma, bf_isabella, bf_lily
- **男性**: bm_daniel, bm_fable, bm_george, bm_lewis

#### 日语
- **女性**: jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro
- **男性**: jm_kumo

#### 中文
- **女性**: zf_xiaobei, zf_xiaoni, zf_xiaoxiao, zf_xiaoyi
- **男性**: zm_yunjian, zm_yunxi, zm_yunxia, zm_yunyang

#### 其他语言
- **西班牙语**: ef_dora, em_alex, em_santa
- **法语**: ff_siwis
- **印地语**: hf_alpha, hf_beta, hm_omega, hm_psi
- **意大利语**: if_sara, im_nicola
- **巴西葡萄牙语**: pf_dora, pm_alex, pm_santa

## 错误处理

### 常见错误码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 400 | 参数错误 | 语音不存在、文本过长 |
| 500 | 服务器错误 | 模型加载失败、音频生成失败 |

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

## 性能优化建议

1. **批量处理**: 对于大量文本，建议分段处理
2. **缓存**: 可以缓存常用文本的生成结果
3. **异步调用**: 使用异步客户端提高并发性能
4. **资源监控**: 监控GPU/CPU使用情况

## 部署建议

### 生产环境配置
```bash
# 使用gunicorn + uvicorn工作进程
gunicorn tts_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "tts_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 健康检查

```bash
curl -X GET "http://localhost:8000/health"
```

响应示例：
```json
{
  "status": "healthy",
  "model": "loaded"
}
```

## 注意事项

1. **内存要求**: 首次加载模型需要约2-4GB内存
2. **首次启动**: 首次启动时会预加载模型，可能需要一些时间
3. **并发限制**: 当前版本为单线程处理，高并发场景需要额外配置
4. **文件清理**: 临时文件会自动清理，但建议定期监控磁盘空间