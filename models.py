"""Models module for Kokoro TTS Local"""
from typing import Optional, Tuple, List
import torch
from kokoro import KPipeline
import os
import locale
import json
from pathlib import Path

# Set environment variables for proper encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
# Disable symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Set locale for better encoding support
try:
    locale.setlocale(locale.LC_ALL, '.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass  # Fall back to system default

# Initialize pipeline globally
_pipeline = None

def read_json_utf8(file_path: str) -> dict:
    """Read JSON file with UTF-8 encoding"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def build_model(model_path: str, device: str) -> KPipeline:
    """Build and return the Kokoro pipeline"""
    global _pipeline
    if _pipeline is None:
        try:
            # Monkey patch KPipeline's json loading
            import kokoro.pipeline
            kokoro.pipeline.json.load = lambda f: json.loads(f.read().encode('cp1252').decode('utf-8'))
            _pipeline = KPipeline(device=device)
        except Exception as e:
            print(f"Error initializing pipeline: {e}")
            raise
    return _pipeline

def list_available_voices() -> List[str]:
    """List all available voice models"""
    pipeline = build_model(None, 'cpu')
    return pipeline.list_voices()

def load_voice(voice_name: str, device: str) -> torch.Tensor:
    """Load a voice model"""
    pipeline = build_model(None, device)
    return pipeline.load_voice(voice_name)

def generate_speech(
    model: KPipeline,
    text: str,
    voice: torch.Tensor,
    lang: str = 'a',
    device: str = 'cpu'
) -> Tuple[Optional[torch.Tensor], Optional[str]]:
    """Generate speech using the Kokoro pipeline"""
    try:
        generator = model(text, voice=voice, lang=lang)
        for gs, ps, audio in generator:
            return audio, ps  # Return first generated segment
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None, None