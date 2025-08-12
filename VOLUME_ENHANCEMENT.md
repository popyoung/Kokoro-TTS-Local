# 音量增强功能使用指南

## 概述
Kokoro TTS现在支持音量增强功能，允许用户通过API参数调节生成音频的音量大小。

## 使用方法

### API参数
在TTS请求中添加`volume_gain`参数：

```json
{
  "text": "需要增大音量的文本",
  "voice": "am_adam",
  "volume_gain": 6.0,
  "format": "wav"
}
```

### 参数说明
- **volume_gain**: 音量增益值，单位为分贝(dB)
  - 范围：-20.0 到 20.0 dB
  - 默认值：0.0 dB（不调整）
  - 正值：增大音量
  - 负值：减小音量

### 推荐设置
| 使用场景 | 推荐增益值 | 说明 |
|----------|------------|------|
| 轻微增强 | 3-6 dB | 适合大多数情况 |
| 明显增强 | 8-12 dB | 适合音量过小的音频 |
| 最大增强 | 15-20 dB | 谨慎使用，可能产生失真 |
| 音量减小 | -5到-10 dB | 适合音量过大的音频 |

## 使用示例

### curl命令示例
```bash
# 增大音量6dB
curl -X POST "http://localhost:8000/tts/file" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一段需要增大音量的文本",
    "voice": "am_adam",
    "volume_gain": 6.0,
    "format": "wav"
  }' \
  --output enhanced_audio.wav

# 减小音量5dB
curl -X POST "http://localhost:8000/tts/data" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "这是一段需要减小音量的文本",
    "voice": "af_bella",
    "volume_gain": -5.0,
    "format": "mp3"
  }' \
  --output quiet_audio.mp3
```

### Python示例
```python
import requests

# 增大音量示例
data = {
    "text": "你好，这是音量增强后的语音！",
    "voice": "am_adam",
    "speed": 1.0,
    "volume_gain": 8.0,  # 增加8dB音量
    "format": "wav"
}

response = requests.post(
    "http://localhost:8000/tts/file",
    json=data,
    headers={"Content-Type": "application/json"}
)

with open("enhanced_speech.wav", "wb") as f:
    f.write(response.content)

print("音量增强后的音频已保存")
```

### JavaScript示例
```javascript
// 使用TTS客户端
const tts = new TTSClient('http://localhost:8000');

const audioUrl = await tts.generateSpeech({
    text: "这是音量增强的语音",
    voices: ["am_adam"],
    volumeGain: 6.0,  // 增加6dB
    format: 'wav'
});

// 播放音频
const audio = new Audio(audioUrl);
audio.play();
```

## 技术实现

音量增强功能基于以下技术实现：

1. **音频后处理**: 在TTS生成音频后应用音量增益
2. **pydub库**: 使用pydub的AudioSegment进行音量调节
3. **标准化处理**: 防止音频削波失真
4. **实时处理**: 不增加额外的处理延迟

## 注意事项

1. **避免过度增强**: 增益值超过15dB可能导致音频失真
2. **动态范围**: 过大的增益可能超出音频的动态范围
3. **兼容性**: 所有现有API端点都支持音量增益参数
4. **向后兼容**: 不指定volume_gain参数时保持原有行为

## 故障排除

### 常见问题

1. **音频失真**: 降低volume_gain值
2. **音量仍然太小**: 检查原始音频质量，可能需要多次调整
3. **API报错**: 确保volume_gain在-20到20范围内

### 调试建议
```python
# 测试不同增益值的效果
test_gains = [0, 3, 6, 9, 12]  # 测试不同增益值

for gain in test_gains:
    data = {
        "text": "测试音量增益",
        "voice": "am_adam",
        "volume_gain": gain,
        "format": "wav"
    }
    
    response = requests.post(
        "http://localhost:8000/tts/file",
        json=data
    )
    
    with open(f"test_gain_{gain}db.wav", "wb") as f:
        f.write(response.content)
```

## 更新日志
- v1.1.0: 添加音量增强功能
- v1.0.0: 初始版本发布