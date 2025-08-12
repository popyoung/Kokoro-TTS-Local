# JavaScript 调用示例文档

本文档提供了使用JavaScript调用Kokoro TTS API的完整示例。

## 文件说明

### 1. `js_demo.html` - 完整的Web演示页面
- **功能**：提供图形化界面，支持所有API功能
- **特点**：
  - 获取语音列表
  - 单个朗读者选择
  - 多朗读者随机选择
  - 实时音频播放
  - 错误处理和状态显示

### 2. `js_demo.js` - 简洁的JavaScript类库
- **功能**：提供封装好的API调用类
- **特点**：
  - 面向对象设计
  - Promise支持
  - 支持Node.js和浏览器环境
  - 简洁的API接口

## 使用方法

### 方法1：使用Web演示页面

1. **启动API服务器**
   ```bash
   python tts_api.py
   ```

2. **打开浏览器**
   - 直接双击 `js_demo.html` 文件
   - 或使用本地服务器：
     ```bash
     # 使用Python内置服务器
     python -m http.server 8080
     # 然后访问 http://localhost:8080/js_demo.html
     ```

3. **使用界面**
   - 点击"获取语音列表"
   - 输入要转换的文本
   - 选择朗读者和参数
   - 点击生成按钮

### 方法2：使用JavaScript类库

#### 浏览器环境
```html
<!DOCTYPE html>
<html>
<head>
    <script src="js_demo.js"></script>
</head>
<body>
    <script>
        const tts = new KokoroTTS();
        
        // 使用示例
        tts.generateSpeech({
            text: 'Hello world',
            voice: 'af_bella'
        }).then(audioUrl => {
            const audio = new Audio(audioUrl);
            audio.play();
        });
    </script>
</body>
</html>
```

#### Node.js环境
```javascript
const KokoroTTS = require('./js_demo.js');

async function test() {
    const tts = new KokoroTTS('http://localhost:8000');
    
    try {
        // 获取语音列表
        const voices = await tts.getVoices();
        console.log('可用语音:', voices.length);
        
        // 生成语音文件
        await tts.generateSpeechFile({
            text: 'Hello from Node.js',
            voices: ['af_bella', 'am_adam'],
            filename: 'output.wav'
        });
        
    } catch (error) {
        console.error('错误:', error);
    }
}

test();
```

## API方法说明

### KokoroTTS类

#### 构造函数
```javascript
const tts = new KokoroTTS(baseUrl);
// baseUrl: API服务器地址，默认 http://localhost:8000
```

#### 方法

1. **getVoices()**
   - 获取可用语音列表
   - 返回：Promise<Array>

2. **generateSpeech(options)**
   - 生成语音并返回音频URL
   - 参数：
     - text: 要转换的文本（必填）
     - voice: 单个语音名称
     - voices: 多个语音名称数组（随机选择）
     - speed: 语速（0.1-3.0，默认1.0）
     - format: 音频格式（wav, mp3, flac，默认wav）
     - sampleRate: 采样率（默认24000）
   - 返回：Promise<string> 音频URL

3. **generateSpeechFile(options)**
   - 生成语音并自动下载文件
   - 参数同上，额外支持：
     - filename: 下载文件名
   - 返回：Promise<Blob>

4. **healthCheck()**
   - 检查API服务器状态
   - 返回：Promise<Object>

## 使用示例

### 基础使用
```javascript
// 单个朗读者
await tts.generateSpeech({
    text: 'Hello world',
    voice: 'af_bella'
});

// 多朗读者随机选择
await tts.generateSpeech({
    text: 'Hello world',
    voices: ['af_bella', 'am_adam', 'af_nicole']
});
```

### 完整流程
```javascript
async function completeExample() {
    const tts = new KokoroTTS();
    
    try {
        // 1. 检查API状态
        const health = await tts.healthCheck();
        console.log('API状态:', health.status);
        
        // 2. 获取语音列表
        const voices = await tts.getVoices();
        console.log('可用语音:', voices.map(v => v.name));
        
        // 3. 生成语音
        const audioUrl = await tts.generateSpeech({
            text: '欢迎使用Kokoro TTS API',
            voices: ['af_bella', 'am_adam'],
            speed: 1.2,
            format: 'wav'
        });
        
        // 4. 播放音频
        const audio = new Audio(audioUrl);
        await audio.play();
        
    } catch (error) {
        console.error('操作失败:', error.message);
    }
}
```

## 注意事项

1. **CORS问题**：确保API服务器已启用CORS支持
2. **网络连接**：确保API服务器正在运行
3. **浏览器兼容性**：现代浏览器都支持
4. **音频格式**：不同浏览器支持的格式不同
5. **文件大小**：大文件可能需要较长时间加载

## 错误处理

所有方法都返回Promise，使用try-catch处理错误：

```javascript
try {
    const result = await tts.generateSpeech({...});
} catch (error) {
    console.error('错误:', error.message);
}
```

## 测试

1. 确保 `tts_api.py` 正在运行
2. 打开 `js_demo.html` 测试完整功能
3. 或使用 `js_demo.js` 进行程序化测试