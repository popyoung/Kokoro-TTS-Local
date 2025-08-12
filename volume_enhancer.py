#!/usr/bin/env python3
"""
音量增强工具
为Kokoro TTS提供音量调节功能
"""

import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pathlib import Path
import tempfile
import io

class VolumeEnhancer:
    """音频音量增强器"""
    
    def __init__(self):
        """初始化音量增强器"""
        pass
    
    def enhance_volume_file(self, input_file: str, output_file: str, volume_gain: float = 6.0) -> bool:
        """
        增强音频文件音量
        
        Args:
            input_file: 输入音频文件路径
            output_file: 输出音频文件路径
            volume_gain: 音量增益(dB)
            
        Returns:
            bool: 是否成功
        """
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(input_file)
            
            # 转换为numpy数组
            samples = np.array(audio.get_array_of_samples())
            
            # 根据采样宽度调整
            if audio.sample_width == 2:
                # int16 -> float32
                samples = samples.astype(np.float32) / 32768.0
            elif audio.sample_width == 4:
                # int32 -> float32
                samples = samples.astype(np.float32) / 2147483648.0
            elif audio.sample_width == 1:
                # int8 -> float32
                samples = samples.astype(np.float32) / 128.0
            
            # 应用线性增益
            linear_gain = 10 ** (volume_gain / 20.0)
            enhanced_samples = samples * linear_gain
            
            # 限制范围
            enhanced_samples = np.clip(enhanced_samples, -1.0, 1.0)
            
            # 转换回原始格式
            if audio.sample_width == 2:
                enhanced_samples = (enhanced_samples * 32767).astype(np.int16)
            elif audio.sample_width == 4:
                enhanced_samples = (enhanced_samples * 2147483647).astype(np.int32)
            elif audio.sample_width == 1:
                enhanced_samples = (enhanced_samples * 127).astype(np.int8)
            
            # 创建新的AudioSegment
            enhanced_audio = audio._spawn(enhanced_samples)
            
            # 导出增强后的音频
            enhanced_audio.export(output_file, format="wav")
            
            return True
            
        except Exception as e:
            print(f"音频文件音量增强失败: {e}")
            return False
    
    def enhance_volume_data(self, audio_data: np.ndarray, sample_rate: int, volume_gain: float = 6.0) -> np.ndarray:
        """
        增强音频数据音量
        
        Args:
            audio_data: 输入音频数据(numpy数组)
            sample_rate: 音频采样率
            volume_gain: 音量增益(dB)
            
        Returns:
            np.ndarray: 增强后的音频数据
        """
        try:
            # 将dB转换为线性增益
            linear_gain = 10 ** (volume_gain / 20.0)
            
            # 直接应用线性增益到音频数据
            enhanced_data = audio_data * linear_gain
            
            # 防止削波：限制在有效范围内
            if audio_data.dtype == np.float32:
                # float32范围通常是[-1.0, 1.0]
                enhanced_data = np.clip(enhanced_data, -1.0, 1.0)
            elif audio_data.dtype == np.int16:
                # int16范围是[-32768, 32767]
                enhanced_data = np.clip(enhanced_data, -32768, 32767)
            elif audio_data.dtype == np.int32:
                # int32范围是[-2147483648, 2147483647]
                enhanced_data = np.clip(enhanced_data, -2147483648, 2147483647)
            else:
                # 其他类型，使用原始范围
                max_val = np.iinfo(audio_data.dtype).max if np.issubdtype(audio_data.dtype, np.integer) else 1.0
                min_val = np.iinfo(audio_data.dtype).min if np.issubdtype(audio_data.dtype, np.integer) else -1.0
                enhanced_data = np.clip(enhanced_data, min_val, max_val)
            
            return enhanced_data.astype(audio_data.dtype)
            
        except Exception as e:
            print(f"音频数据音量增强失败: {e}")
            return audio_data
    
    def normalize_volume(self, audio_data: np.ndarray, target_db: float = -3.0) -> np.ndarray:
        """
        标准化音频音量到目标dB
        
        Args:
            audio_data: 输入音频数据
            target_db: 目标音量(dB)
            
        Returns:
            np.ndarray: 标准化后的音频数据
        """
        try:
            # 计算当前音频的RMS值
            if audio_data.dtype == np.float32:
                # float32音频数据
                current_rms = np.sqrt(np.mean(audio_data ** 2))
                # 计算目标RMS值（-3dB对应约0.707）
                target_rms = 10 ** (target_db / 20.0)
                
                if current_rms > 0:
                    gain_factor = target_rms / current_rms
                    normalized_data = audio_data * gain_factor
                    # 限制在有效范围内
                    normalized_data = np.clip(normalized_data, -1.0, 1.0)
                else:
                    normalized_data = audio_data
                    
            else:
                # 整数类型音频数据
                max_val = np.iinfo(audio_data.dtype).max
                audio_float = audio_data.astype(np.float32) / max_val
                current_rms = np.sqrt(np.mean(audio_float ** 2))
                target_rms = 10 ** (target_db / 20.0)
                
                if current_rms > 0:
                    gain_factor = target_rms / current_rms
                    normalized_float = audio_float * gain_factor
                    normalized_float = np.clip(normalized_float, -1.0, 1.0)
                    normalized_data = (normalized_float * max_val).astype(audio_data.dtype)
                else:
                    normalized_data = audio_data
            
            return normalized_data
            
        except Exception as e:
            print(f"音量标准化失败: {e}")
            return audio_data

# 全局音量增强器实例
volume_enhancer = VolumeEnhancer()

def enhance_tts_audio(audio_data: np.ndarray, volume_gain: float = 6.0) -> np.ndarray:
    """
    增强TTS生成的音频音量
    
    Args:
        audio_data: TTS生成的音频数据
        volume_gain: 音量增益(dB)
        
    Returns:
        np.ndarray: 增强后的音频数据
    """
    return volume_enhancer.enhance_volume_data(audio_data, 24000, volume_gain)

if __name__ == "__main__":
    # 测试音量增强功能
    enhancer = VolumeEnhancer()
    
    # 测试文件增强
    test_input = "test_input.wav"
    test_output = "test_output_enhanced.wav"
    
    if Path(test_input).exists():
        success = enhancer.enhance_volume_file(test_input, test_output, 10.0)
        if success:
            print(f"音量增强完成: {test_output}")
        else:
            print("音量增强失败")
    else:
        print("测试文件不存在，创建示例用法")