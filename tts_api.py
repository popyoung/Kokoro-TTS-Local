"""
Kokoro TTS API Server
提供RESTful API接口供其他项目调用文本转语音功能
"""

import os
import io
import tempfile
import asyncio
import random
from typing import Optional, List
from pathlib import Path
import torch
import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import uvicorn
import logging
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from models import build_model, generate_speech, list_available_voices
from config import TTSConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting Kokoro TTS API server...")
    try:
        await get_model()
        logger.info("Model preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload model: {e}")
    
    yield
    
    # 关闭时执行
    global model
    if model is not None:
        try:
            del model
            model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Model resources cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# 初始化FastAPI应用
app = FastAPI(
    title="Kokoro TTS API",
    description="文本转语音API服务，支持多种语音和语言",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应设置为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局配置
config = TTSConfig()
model = None
model_lock = asyncio.Lock()

# 请求模型
class TTSRequest(BaseModel):
    text: str = Field(..., description="要转换的文本", max_length=10000)
    voices: List[str] = Field(..., description="语音选择列表，随机选择一个使用")
    speed: float = Field(default=1.0, ge=0.1, le=3.0, description="语速 (0.1-3.0)")
    format: str = Field(default="wav", description="输出音频格式")
    sample_rate: int = Field(default=24000, description="采样率")

class VoiceInfo(BaseModel):
    name: str
    language: str
    gender: str

# 辅助函数
async def get_model():
    """获取或初始化模型"""
    global model
    if model is None:
        async with model_lock:
            if model is None:  # 双重检查
                try:
                    device = 'cuda' if torch.cuda.is_available() else 'cpu'
                    logger.info(f"Initializing model on device: {device}")
                    model = build_model(config.get("model.default_model_path"), device)
                    logger.info("Model initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize model: {e}")
                    raise HTTPException(status_code=500, detail=f"模型初始化失败: {str(e)}")
    return model

def validate_voice(voice_name: str) -> bool:
    """验证语音文件是否存在"""
    voices_dir = Path(config.get("paths.voices_dir"))
    voice_path = voices_dir / f"{voice_name}.pt"
    return voice_path.exists()

def select_voice_from_request(request: TTSRequest) -> str:
    """根据请求选择语音"""
    if not request.voices or len(request.voices) == 0:
        raise HTTPException(
            status_code=400,
            detail="必须提供至少一个语音选择"
        )
    
    # 从提供的语音列表中随机选择一个
    valid_voices = [v for v in request.voices if validate_voice(v)]
    if not valid_voices:
        available_voices = list_available_voices()
        raise HTTPException(
            status_code=400,
            detail=f"提供的语音列表中的语音都不存在。可用语音: {', '.join(available_voices)}"
        )
    selected_voice = random.choice(valid_voices)
    logger.info(f"随机选择了语音: {selected_voice} 从列表: {valid_voices}")
    return selected_voice

async def generate_audio(text: str, voice: str, speed: float, sample_rate: int) -> np.ndarray:
    """生成音频数据"""
    model_instance = await get_model()
    
    voices_dir = Path(config.get("paths.voices_dir"))
    voice_path = voices_dir / f"{voice}.pt"
    
    try:
        # 生成语音
        all_audio = []
        generator = model_instance(text, voice=str(voice_path), speed=speed, split_pattern=r'\n+')
        
        for gs, ps, audio in generator:
            if audio is not None:
                audio_tensor = audio if isinstance(audio, torch.Tensor) else torch.from_numpy(audio).float()
                all_audio.append(audio_tensor)
        
        if not all_audio:
            raise HTTPException(status_code=500, detail="音频生成失败")
        
        # 合并音频片段
        if len(all_audio) == 1:
            final_audio = all_audio[0]
        else:
            final_audio = torch.cat(all_audio, dim=0)
        
        return final_audio.numpy()
        
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"音频生成失败: {str(e)}")

# API路由
@app.get("/", response_model=dict)
async def root():
    """API根路径"""
    return {
        "message": "Kokoro TTS API 服务已启动",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/voices", response_model=List[VoiceInfo])
async def get_voices():
    """获取可用语音列表"""
    try:
        voices = list_available_voices()
        voice_info_list = []
        
        for voice in voices:
            # 解析语音名称格式
            parts = voice.split('_')
            if len(parts) >= 2:
                lang_code = parts[0][0]  # 第一个字母
                gender = parts[0][1]     # 第二个字母
                
                language_map = {
                    'a': 'American English',
                    'b': 'British English',
                    'j': 'Japanese',
                    'z': 'Mandarin Chinese',
                    'e': 'Spanish',
                    'f': 'French',
                    'h': 'Hindi',
                    'i': 'Italian',
                    'p': 'Brazilian Portuguese'
                }
                
                gender_map = {'f': 'Female', 'm': 'Male'}
                
                voice_info = VoiceInfo(
                    name=voice,
                    language=language_map.get(lang_code, 'Unknown'),
                    gender=gender_map.get(gender, 'Unknown')
                )
                voice_info_list.append(voice_info)
        
        return voice_info_list
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(status_code=500, detail="获取语音列表失败")

@app.post("/tts/file")
async def text_to_speech_file(request: TTSRequest):
    """文本转语音，返回音频文件"""
    # 选择语音
    selected_voice = select_voice_from_request(request)
    
    # 生成音频数据
    audio_data = await generate_audio(request.text, selected_voice, request.speed, request.sample_rate)
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{request.format}") as tmp_file:
        tmp_path = Path(tmp_file.name)
    
    try:
        # 保存音频到临时文件
        sf.write(str(tmp_path), audio_data, request.sample_rate, format=request.format)
        
        # 返回文件响应
        return FileResponse(
            path=str(tmp_path),
            media_type=f"audio/{request.format}",
            filename=f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}",
            headers={"Content-Disposition": f"attachment; filename=tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"}
        )
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        logger.error(f"Error saving audio file: {e}")
        raise HTTPException(status_code=500, detail="保存音频文件失败")

@app.post("/tts/data")
async def text_to_speech_data(request: TTSRequest):
    """文本转语音，返回音频数据流"""
    # 选择语音
    selected_voice = select_voice_from_request(request)
    
    # 生成音频数据
    audio_data = await generate_audio(request.text, selected_voice, request.speed, request.sample_rate)
    
    try:
        # 将音频数据写入内存缓冲区
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, request.sample_rate, format=request.format)
        buffer.seek(0)
        
        # 返回流响应
        return StreamingResponse(
            buffer,
            media_type=f"audio/{request.format}",
            headers={"Content-Disposition": f"inline; filename=tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.format}"}
        )
    except Exception as e:
        logger.error(f"Error generating audio stream: {e}")
        raise HTTPException(status_code=500, detail="生成音频流失败")

@app.post("/tts/save")
async def text_to_speech_save(request: TTSRequest, output_path: str):
    """文本转语音，保存到指定路径"""
    # 选择语音
    selected_voice = select_voice_from_request(request)
    
    # 生成音频数据
    audio_data = await generate_audio(request.text, selected_voice, request.speed, request.sample_rate)
    
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存音频文件
        sf.write(str(output_file), audio_data, request.sample_rate, format=request.format)
        
        return {
            "message": "音频文件已保存",
            "path": str(output_file),
            "format": request.format,
            "duration": len(audio_data) / request.sample_rate
        }
    except Exception as e:
        logger.error(f"Error saving audio to path: {e}")
        raise HTTPException(status_code=500, detail=f"保存音频到指定路径失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查模型是否可用
        await get_model()
        return {"status": "healthy", "model": "loaded"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}



if __name__ == "__main__":
    uvicorn.run(
        "tts_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )