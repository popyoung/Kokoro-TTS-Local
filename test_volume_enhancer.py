#!/usr/bin/env python3
"""
测试音量增强器的正确性
"""
import numpy as np
import soundfile as sf
from volume_enhancer import VolumeEnhancer
import tempfile
import os

def test_volume_enhancer():
    """测试音量增强器"""
    print("=== 测试音量增强器 ===")
    
    # 创建测试音频（1秒，440Hz正弦波，float32格式）
    sample_rate = 24000
    duration = 1.0
    frequency = 440
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    test_audio = 0.5 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    print(f"原始音频数据类型: {test_audio.dtype}")
    print(f"原始音频范围: [{test_audio.min():.4f}, {test_audio.max():.4f}]")
    
    # 测试数据增强
    enhancer = VolumeEnhancer()
    
    # 测试不同增益
    gains = [1.0, 3.0, 6.0, -3.0]
    
    for gain in gains:
        print(f"\n--- 测试增益: {gain} dB ---")
        
        # 增强音频数据
        enhanced = enhancer.enhance_volume_data(test_audio, sample_rate, gain)
        
        print(f"增强后音频数据类型: {enhanced.dtype}")
        print(f"增强后音频范围: [{enhanced.min():.4f}, {enhanced.max():.4f}]")
        
        # 检查是否有削波
        if enhanced.dtype == np.float32:
            clipped = np.any(np.abs(enhanced) >= 1.0)
        else:
            clipped = False
        
        print(f"是否削波: {clipped}")
        
        # 保存测试文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
            
        try:
            sf.write(temp_path, enhanced, sample_rate)
            print(f"测试文件已保存: {temp_path}")
        except Exception as e:
            print(f"保存文件失败: {e}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

if __name__ == "__main__":
    test_volume_enhancer()