/**
 * Kokoro TTS API JavaScript 调用示例
 * 提供简洁的API调用方法
 */

class KokoroTTS {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    /**
     * 获取可用语音列表
     * @returns {Promise<Array>} 语音列表
     */
    async getVoices() {
        try {
            const response = await fetch(`${this.baseUrl}/voices`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('获取语音列表失败:', error);
            throw error;
        }
    }

    /**
         * 生成语音并返回音频URL
         * @param {Object} options - 配置选项
         * @param {string} options.text - 要转换的文本
         * @param {Array} options.voices - 多个语音名称（随机选择）
         * @param {number} options.speed - 语速 (0.1-3.0)
         * @param {string} options.format - 音频格式 (wav, mp3, flac)
         * @param {number} options.sampleRate - 采样率
         * @param {number} options.volumeGain - 音量增益(dB)，范围-10到20
         * @returns {Promise<string>} 音频URL - 可直接用于<audio>标签的src属性
         */
        async generateSpeech(options = {}) {
            const {
                text,
                voice,
                speed = 1.0,
                format = 'wav',
                sampleRate = 24000,
                volumeGain = 0.0
            } = options;

            // 参数验证
            if (!text) throw new Error('文本不能为空');
            if (!voice) throw new Error('必须提供语音选择');

            // 构建请求负载
            const payload = {
                text,
                voice,
                speed,
                format,
                sampleRate,
                volumeGain
            };

            try {
                // 发送POST请求到TTS API
                const response = await fetch(`${this.baseUrl}/tts/data`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                // 检查HTTP响应状态
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || `HTTP ${response.status}`);
                }

                // 关键步骤：将HTTP响应转换为Blob对象
                // response.blob() 将响应体（音频文件数据）读取为二进制Blob对象
                // Blob对象是浏览器中处理二进制数据的标准方式
                const blob = await response.blob();
                
                // 创建临时的URL对象，格式如: blob:http://localhost:8000/unique-id
                // 这个URL可以直接用于<audio>标签的src属性进行播放
                // 注意：这个URL在页面刷新后会失效，需要重新生成
                return URL.createObjectURL(blob);
            } catch (error) {
                console.error('语音生成失败:', error);
                throw error;
            }
        }

    /**
     * 生成语音并保存为文件
     * 调用API生成语音，并自动触发浏览器下载保存
     * @param {Object} options - 配置选项
     * @param {string} options.text - 要转换的文本
     * @param {Array} options.voices - 语音名称列表
     * @param {number} options.speed - 语速 (0.1-3.0)
     * @param {string} options.format - 音频格式 (wav, mp3, flac)
     * @param {number} options.sampleRate - 采样率
     * @param {string} options.filename - 保存的文件名，默认为时间戳
     * @returns {Promise<Blob>} 音频文件Blob对象，可用于进一步处理
     */
    async generateSpeechFile(options = {}) {
        const {
                text,
                voice,
                speed = 1.0,
                format = 'wav',
                sampleRate = 24000,
                volumeGain = 0.0,
                filename = `tts_${Date.now()}.${format}`  // 默认文件名包含时间戳
            } = options;

        // 参数验证
        if (!text) throw new Error('文本不能为空');
        if (!voice) throw new Error('必须提供语音选择');

        // 构建请求负载
            const payload = {
                text,
                voice,
                speed,
                format,
                sampleRate,
                volumeGain
            };

        try {
            // 发送POST请求到文件端点
            const response = await fetch(`${this.baseUrl}/tts/file`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            // 检查响应状态
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            // 获取音频Blob数据
            const blob = await response.blob();
            
            // 创建下载链接并触发浏览器下载
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');  // 创建隐藏的下载链接
            a.href = url;
            a.download = filename;  // 设置下载文件名
            document.body.appendChild(a);  // 临时添加到DOM
            a.click();  // 触发点击下载
            document.body.removeChild(a);  // 下载后移除
            URL.revokeObjectURL(url);  // 释放内存

            return blob;  // 返回Blob供后续使用
        } catch (error) {
            console.error('语音文件生成失败:', error);
            throw error;
        }
    }

    /**
     * 健康检查
     * 检查TTS API服务是否正常运行
     * @returns {Promise<Object>} 健康状态对象，包含服务状态信息
     */
    async healthCheck() {
        try {
            // 发送GET请求到健康检查端点
            const response = await fetch(`${this.baseUrl}/health`);
            
            // 解析并返回健康状态
            return await response.json();
        } catch (error) {
            console.error('健康检查失败:', error);
            throw error;
        }
    }
}

/**
 * 使用示例函数
 * 展示了如何使用KokoroTTS类的各种功能
 * 可以直接在浏览器控制台中运行此函数进行测试
 */
async function demo() {
    const tts = new KokoroTTS();  // 创建TTS实例

    try {
        // 步骤1: 健康检查 - 确认API服务可用
        const health = await tts.healthCheck();
        console.log('API状态:', health);

        // 步骤2: 获取语音列表 - 查看所有可用的语音
        const voices = await tts.getVoices();
        console.log(`找到 ${voices.length} 个语音`);
        console.log('前3个语音:', voices.slice(0, 3));

        // 步骤3: 生成单个语音 - 使用指定语音
        const audioUrl1 = await tts.generateSpeech({
            text: 'Hello, this is a single voice test.',
            voice: 'af_bella',
            speed: 1.2
        });
        console.log('单个语音URL:', audioUrl1);
        // 可以设置: audioPlayer.src = audioUrl1; 来播放

        // 步骤4: 使用特定语音生成
        const audioUrl2 = await tts.generateSpeech({
            text: 'Hello, this is a specific voice test.',
            voice: 'am_adam',
            speed: 1.0
        });
        console.log('特定语音URL:', audioUrl2);

    } catch (error) {
        console.error('演示失败:', error);
    }
}

/**
 * 模块导出设置
 * 支持在不同的环境中使用：Node.js和浏览器
 */

// Node.js环境导出 - 用于服务器端JavaScript
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KokoroTTS;
}

// 浏览器环境全局变量 - 使KokoroTTS在全局作用域中可用
if (typeof window !== 'undefined') {
    window.KokoroTTS = KokoroTTS;
}