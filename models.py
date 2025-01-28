"""Models module for Kokoro TTS Local"""
from typing import Optional, Tuple, List
import torch
from kokoro import KPipeline
import os
import json
from pathlib import Path

# Set environment variables for proper encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
# Disable symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Initialize espeak-ng
try:
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    from phonemizer import phonemize
    import espeakng_loader
    
    # Make library available first
    library_path = espeakng_loader.get_library_path()
    data_path = espeakng_loader.get_data_path()
    espeakng_loader.make_library_available()
    
    # Set up espeak-ng paths
    EspeakWrapper.library_path = library_path
    EspeakWrapper.data_path = data_path
    
    # Verify espeak-ng is working
    try:
        test_phonemes = phonemize('test', language='en-us')
        if not test_phonemes:
            raise Exception("Phonemization returned empty result")
    except Exception as e:
        print(f"Warning: espeak-ng test failed: {e}")
        print("Some functionality may be limited")

except ImportError:
    print("Warning: Required packages not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "espeakng-loader>=0.1.6", "phonemizer-fork>=3.0.2"])
    
    # Try again after installation
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    from phonemizer import phonemize
    import espeakng_loader
    
    library_path = espeakng_loader.get_library_path()
    data_path = espeakng_loader.get_data_path()
    espeakng_loader.make_library_available()
    EspeakWrapper.library_path = library_path
    EspeakWrapper.data_path = data_path

# Initialize pipeline globally
_pipeline = None

def patch_json_load():
    """Patch json.load to handle the specific encoding of config file"""
    original_load = json.load
    
    def custom_load(fp, *args, **kwargs):
        try:
            # Try UTF-8 first
            content = fp.read()
            return json.loads(content)
        except UnicodeDecodeError:
            # If UTF-8 fails, try reading as bytes and decode manually
            fp.seek(0)
            content = fp.buffer.read() if hasattr(fp, 'buffer') else fp.read()
            text = content.decode('utf-8', errors='replace')
            return json.loads(text)
    
    json.load = custom_load

def build_model(model_path: str, device: str) -> KPipeline:
    """Build and return the Kokoro pipeline"""
    global _pipeline
    if _pipeline is None:
        try:
            # Initialize pipeline with American English by default
            _pipeline = KPipeline(device=device, lang_code='a')
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
    lang: str = 'a',  # 'a' for American English, 'b' for British English
    device: str = 'cpu',
    speed: float = 1.0
) -> Tuple[Optional[torch.Tensor], Optional[str]]:
    """Generate speech using the Kokoro pipeline
    
    Args:
        model: KPipeline instance
        text: Text to synthesize
        voice: Voice tensor from load_voice()
        lang: Language code ('a' for American English, 'b' for British English)
        device: Device to use ('cuda' or 'cpu')
        speed: Speech speed multiplier (default: 1.0)
        
    Returns:
        Tuple of (audio tensor, phonemes string) or (None, None) on error
    """
    try:
        # Generate speech with the new API
        generator = model(
            text, 
            voice=voice, 
            speed=speed,
            split_pattern=r'\n+'  # Split on newlines for better handling
        )
        
        # Get first generated segment
        for gs, ps, audio in generator:
            return audio, ps
            
        return None, None
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None, None