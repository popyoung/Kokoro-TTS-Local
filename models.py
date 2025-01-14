import torch
import torch.nn as nn
import os
import numpy as np
from huggingface_hub import hf_hub_download
import sys
from espeakng_loader import install_espeak

class TextToSpeech(nn.Module):
    def __init__(self):
        super().__init__()
        # Install espeak-ng using the loader
        try:
            install_espeak()
            print("espeak-ng installed successfully")
        except Exception as e:
            print(f"Error installing espeak-ng: {e}")
            raise
            
        # Download model files from Hugging Face
        model_path = "hexgrad/Kokoro-82M"
        try:
            # Download all necessary files
            self.model_file = hf_hub_download(repo_id=model_path, filename="kokoro-v0_19.pth")
            self.kokoro_py = hf_hub_download(repo_id=model_path, filename="kokoro.py")
            self.models_py = hf_hub_download(repo_id=model_path, filename="models.py")
            self.istftnet_py = hf_hub_download(repo_id=model_path, filename="istftnet.py")
            
            # Add the directory containing the downloaded files to Python path
            model_dir = os.path.dirname(self.kokoro_py)
            if model_dir not in sys.path:
                sys.path.insert(0, model_dir)
            
            print(f"Model directory: {model_dir}")
            
            # Test phonemizer before importing kokoro
            try:
                import phonemizer
                from phonemizer.backend import EspeakBackend
                print("Testing phonemizer with espeak backend...")
                backend = EspeakBackend(language='en-us', preserve_punctuation=True)
                test_text = "Hello"
                phonemes = backend.phonemize([test_text])
                print(f"Phonemizer test successful: {test_text} -> {phonemes}")
                
                # Now import kokoro
                from kokoro import TextToSpeech as KokoroTTS
                print("Successfully imported KokoroTTS")
            except Exception as e:
                print(f"Error testing phonemizer: {e}")
                raise
            
            # Initialize the model using original implementation
            self.model = KokoroTTS()
            self.model.load_state_dict(torch.load(self.model_file, map_location='cpu'))
            self.model.eval()
            
            print("Model loaded successfully")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def forward(self, x):
        return self.model(x)
    
    def generate(self, text, style=0, speed=1.0):
        try:
            with torch.no_grad():
                # Use the model's native generate method
                audio = self.model.generate(text, style=style, speed=speed)
                return audio
        except Exception as e:
            print(f"Error in generation: {e}")
            import traceback
            traceback.print_exc()
            return None 