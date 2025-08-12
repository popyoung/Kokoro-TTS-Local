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
     * @returns {Promise<string>} 音频URL
     */
    async generateSpeech(options = {}) {
        const {
            text,
            voices,
            speed = 1.0,
            format = 'wav',
            sampleRate = 24000
        } = options;

        if (!text) throw new Error('文本不能为空');
        if (!voices || voices.length === 0) throw new Error('必须提供至少一个语音');

        const payload = {
            text,
            voices,
            speed,
            format,
            sampleRate
        };

        try {
            const response = await fetch(`${this.baseUrl}/tts/data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const blob = await response.blob();
            return URL.createObjectURL(blob);
        } catch (error) {
            console.error('语音生成失败:', error);
            throw error;
        }
    }

    /**
     * 生成语音并保存为文件
     * @param {Object} options - 配置选项
     * @param {string} options.filename - 文件名
     * @returns {Promise<Blob>} 音频文件Blob
     */
    async generateSpeechFile(options = {}) {
        const {
            text,
            voices,
            speed = 1.0,
            format = 'wav',
            sampleRate = 24000,
            filename = `tts_${Date.now()}.${format}`
        } = options;

        if (!text) throw new Error('文本不能为空');
        if (!voices || voices.length === 0) throw new Error('必须提供至少一个语音');

        const payload = {
            text,
            voices,
            speed,
            format,
            sampleRate
        };

        try {
            const response = await fetch(`${this.baseUrl}/tts/file`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const blob = await response.blob();
            
            // 触发下载
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            return blob;
        } catch (error) {
            console.error('语音文件生成失败:', error);
            throw error;
        }
    }

    /**
     * 健康检查
     * @returns {Promise<Object>} 健康状态
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            console.error('健康检查失败:', error);
            throw error;
        }
    }
}

// 使用示例
async function demo() {
    const tts = new KokoroTTS();

    try {
        // 1. 健康检查
        const health = await tts.healthCheck();
        console.log('API状态:', health);

        // 2. 获取语音列表
        const voices = await tts.getVoices();
        console.log(`找到 ${voices.length} 个语音`);
        console.log('前3个语音:', voices.slice(0, 3));

        // 3. 生成单个语音
        const audioUrl1 = await tts.generateSpeech({
            text: 'Hello, this is a single voice test.',
            voice: 'af_bella',
            speed: 1.2
        });
        console.log('单个语音URL:', audioUrl1);

        // 4. 生成随机语音
        const audioUrl2 = await tts.generateSpeech({
            text: 'Hello, this is a random voice test.',
            voices: ['af_bella', 'am_adam', 'af_nicole'],
            speed: 1.0
        });
        console.log('随机语音URL:', audioUrl2);

    } catch (error) {
        console.error('演示失败:', error);
    }
}

// Node.js环境导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KokoroTTS;
}

// 浏览器环境全局变量
if (typeof window !== 'undefined') {
    window.KokoroTTS = KokoroTTS;
}