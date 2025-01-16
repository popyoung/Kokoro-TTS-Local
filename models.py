import torch
import os
import sys
import platform
import glob
from huggingface_hub import hf_hub_download, list_repo_files
import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

__all__ = ['list_available_voices', 'build_model', 'load_voice', 'generate_speech']

def get_voices_path():
    """Get the path where voice files are stored."""
    system = platform.system().lower()
    if system == "windows":
        base = os.getenv("APPDATA", os.path.expanduser("~"))
    else:  # Linux and macOS
        base = str(Path.home() / ".cache")
    
    return str(Path(base) / "huggingface" / "hub" / "models--hexgrad--Kokoro-82M" / "snapshots" / "main" / "voices")

def list_available_voices():
    """List all available voices from the official voicepacks."""
    voices_path = get_voices_path()
    try:
        # Download voices if they don't exist
        if not os.path.exists(voices_path):
            print("Downloading voice files...")
            repo_id = "hexgrad/Kokoro-82M"
            for voice in ["af", "af_bella", "af_sarah", "am_adam", "am_michael"]:
                try:
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=f"voices/{voice}.pt",
                        local_dir=str(Path(voices_path).parent.parent.parent)
                    )
                except Exception as e:
                    print(f"Error downloading voice {voice}: {e}")
        
        # List available voice files
        if os.path.exists(voices_path):
            voices = [os.path.splitext(f)[0] for f in os.listdir(voices_path) if f.endswith('.pt')]
            return sorted(voices)
    except Exception as e:
        print(f"Error accessing voices: {e}")
    
    # Fallback to default voices if download fails
    return ["af", "af_bella", "af_sarah", "am_adam", "am_michael"]

def get_platform_paths():
    """Get platform-specific paths for espeak-ng"""
    system = platform.system().lower()
    
    if system == "windows":
        lib_path = os.path.join(os.getenv("ProgramFiles"), "eSpeak NG", "libespeak-ng.dll")
        data_path = os.path.join(os.getenv("ProgramFiles"), "eSpeak NG", "espeak-ng-data")
    
    elif system == "darwin":  # macOS
        lib_path = "/opt/homebrew/lib/libespeak-ng.dylib"
        brew_data = "/opt/homebrew/share/espeak-ng-data"
        sys_lib = "/usr/local/lib/libespeak-ng.dylib"
        sys_data = "/usr/local/share/espeak-ng-data"
        lib_path = lib_path if os.path.exists(lib_path) else sys_lib
        data_path = brew_data if os.path.exists(brew_data) else sys_data
    
    else:  # Linux
        data_path = "/usr/lib/x86_64-linux-gnu/espeak-ng-data"
        lib_paths = [
            "/lib/x86_64-linux-gnu/libespeak-ng.so.1",
            "/usr/lib/x86_64-linux-gnu/libespeak-ng.so",
            "/usr/lib/libespeak-ng.so",
            "/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1",
            "/usr/lib/aarch64-linux-gnu/libespeak-ng.so",
            "/usr/lib64/libespeak-ng.so"
        ]
        
        lib_path = None
        for path in lib_paths:
            if os.path.exists(path):
                lib_path = path
                break
        
        if lib_path is None:
            lib_path = lib_paths[0]  # Default for error message
    
    return lib_path, data_path

def setup_espeak():
    """Set up espeak library paths for phonemizer."""
    try:
        lib_path, data_path = get_platform_paths()
        
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"espeak-ng library not found at {lib_path}")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"espeak-ng data not found at {data_path}")
            
        EspeakWrapper.set_library(lib_path)
        EspeakWrapper.data_path = data_path
        print("espeak-ng library paths set up successfully")
        
    except Exception as e:
        print(f"Error setting up espeak: {e}")
        print("\nPlease ensure espeak-ng is installed:")
        print("- Windows: Download from https://github.com/espeak-ng/espeak-ng/releases")
        print("- macOS: brew install espeak-ng")
        print("- Linux: sudo apt install espeak-ng")
        raise e

def import_module_from_path(module_name, module_path):
    """Import a module from file path."""
    try:
        spec = spec_from_file_location(module_name, module_path)
        module = module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error importing module {module_name}: {e}")
        raise e

def build_model(model_file, device='cpu'):
    """Build the Kokoro model following official implementation."""
    try:
        setup_espeak()
        
        repo_id = "hexgrad/Kokoro-82M"
        model_path = hf_hub_download(repo_id=repo_id, filename="kokoro-v0_19.pth")
        kokoro_py = hf_hub_download(repo_id=repo_id, filename="kokoro.py")
        models_py = hf_hub_download(repo_id=repo_id, filename="models.py")
        istftnet_py = hf_hub_download(repo_id=repo_id, filename="istftnet.py")
        plbert_py = hf_hub_download(repo_id=repo_id, filename="plbert.py")
        
        print("Importing plbert module...")
        plbert_module = import_module_from_path("plbert", plbert_py)
        print("Importing istftnet module...")
        istftnet_module = import_module_from_path("istftnet", istftnet_py)
        print("Importing models module...")
        models_module = import_module_from_path("models", models_py)
        print("Importing kokoro module...")
        kokoro_module = import_module_from_path("kokoro", kokoro_py)
        
        from phonemizer import phonemize
        test_phonemes = phonemize("Hello")
        print(f"Phonemizer test successful: 'Hello' -> {test_phonemes}")
        
        print("Building model...")
        model = models_module.build_model(model_path, device)
        print(f"Model loaded successfully on {device}")
        return model
        
    except Exception as e:
        print(f"Error building model: {e}")
        import traceback
        traceback.print_exc()
        raise e

def load_voice(voice_name='af', device='cpu'):
    """Load a voice from the official voicepacks."""
    try:
        repo_id = "hexgrad/Kokoro-82M"
        voice_path = hf_hub_download(repo_id=repo_id, filename=f"voices/{voice_name}.pt")
        voice = torch.load(voice_path, weights_only=True).to(device)
        print(f"Loaded voice: {voice_name}")
        return voice
    except Exception as e:
        print(f"Error loading voice: {e}")
        raise e

def generate_speech(model, text, voice=None, lang='a', device='cpu'):
    """Generate speech using the Kokoro model."""
    try:
        from kokoro import generate
        audio, phonemes = generate(model, text, voice, lang=lang)
        return audio, phonemes
    except Exception as e:
        print(f"Error generating speech: {e}")
        import traceback
        traceback.print_exc()
        return None, None