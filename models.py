"""Models module for Kokoro TTS Local"""
from typing import Optional, Tuple, List
import torch
from kokoro import KPipeline

# Initialize pipeline globally
_pipeline = None

def build_model(model_path: str, device: str) -> KPipeline:
    """Build and return the Kokoro pipeline"""
    global _pipeline
    if _pipeline is None:
        _pipeline = KPipeline(device=device)
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