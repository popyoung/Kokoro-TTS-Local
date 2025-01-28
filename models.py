"""Models module for Kokoro TTS Local"""
from typing import Optional, Tuple, List
import torch
from kokoro import KPipeline
import os
import json
import codecs
from pathlib import Path

# Set environment variables for proper encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
# Disable symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def patch_json_load():
    """Patch json.load to handle UTF-8 encoded files with special characters"""
    original_load = json.load
    
    def custom_load(fp, *args, **kwargs):
        try:
            # Try reading with UTF-8 encoding
            if hasattr(fp, 'buffer'):
                content = fp.buffer.read().decode('utf-8')
            else:
                content = fp.read()
            return json.loads(content)
        except UnicodeDecodeError:
            # If UTF-8 fails, try with utf-8-sig for files with BOM
            fp.seek(0)
            content = fp.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8-sig', errors='replace')
            return json.loads(content)
    
    json.load = custom_load

def load_config(config_path: str) -> dict:
    """Load configuration file with proper encoding handling"""
    try:
        with codecs.open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        # Fallback to utf-8-sig if regular utf-8 fails
        with codecs.open(config_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

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

except ImportError as e:
    print(f"Warning: Required packages not found: {e}")
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call(["pip", "install", "espeakng-loader", "phonemizer-fork"])
    
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

def build_model(model_path: str, device: str) -> KPipeline:
    """Build and return the Kokoro pipeline with proper encoding configuration"""
    global _pipeline
    if _pipeline is None:
        try:
            # Patch json loading before initializing pipeline
            patch_json_load()
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