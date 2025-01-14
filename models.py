import torch
import os
from huggingface_hub import hf_hub_download

def build_model(model_file, device='cpu'):
    """Build the Kokoro model following official implementation."""
    try:
        # Download necessary files from Hugging Face
        repo_id = "hexgrad/Kokoro-82M"
        model_path = hf_hub_download(repo_id=repo_id, filename=model_file)
        kokoro_py = hf_hub_download(repo_id=repo_id, filename="kokoro.py")
        models_py = hf_hub_download(repo_id=repo_id, filename="models.py")
        istftnet_py = hf_hub_download(repo_id=repo_id, filename="istftnet.py")
        
        # Add model directory to Python path
        model_dir = os.path.dirname(kokoro_py)
        if model_dir not in os.path.sys.path:
            os.path.sys.path.insert(0, model_dir)
        
        # Import the model builder
        from models import build_model as kokoro_build_model
        
        # Build and load the model
        model = kokoro_build_model(model_path, device)
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