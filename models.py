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
    import espeakng_loader
    
    # Make library available first
    espeakng_loader.make_library_available()
    
    # Set up espeak-ng paths using espeakng-loader
    EspeakWrapper.library_path = espeakng_loader.get_library_path()
    EspeakWrapper.data_path = espeakng_loader.get_data_path()
    
    # Verify espeak-ng is working
    try:
        from phonemizer import phonemize
        phonemize('test', language='en-us')
    except Exception as e:
        print(f"Warning: espeak-ng test failed: {e}")
        print("Some functionality may be limited")
except ImportError:
    print("Warning: espeakng-loader not found. Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "espeakng-loader>=0.1.6", "phonemizer-fork>=3.0.2"])
    
    # Try again after installation
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    import espeakng_loader
    espeakng_loader.make_library_available()
    EspeakWrapper.library_path = espeakng_loader.get_library_path()
    EspeakWrapper.data_path = espeakng_loader.get_data_path()

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
            # Patch json.load before creating pipeline
            patch_json_load()
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
    lang: str = 'a',  # Not used anymore since it's handled by the pipeline
    device: str = 'cpu'
) -> Tuple[Optional[torch.Tensor], Optional[str]]:
    """Generate speech using the Kokoro pipeline"""
    try:
        generator = model(text, voice=voice)
        for gs, ps, audio in generator:
            return audio, ps  # Return first generated segment
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None, None