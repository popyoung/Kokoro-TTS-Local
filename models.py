import torch
import torch.nn as nn
import os
import numpy as np
from huggingface_hub import hf_hub_download
import subprocess
import sys
import shutil

def find_espeak():
    # First check the current directory since we can see the files are here
    current_dir = os.getcwd()
    espeak_exe = os.path.join(current_dir, 'espeak-ng.exe')
    espeak_dll = os.path.join(current_dir, 'libespeak-ng.dll')
    espeak_data = os.path.join(current_dir, 'espeak-ng-data')
    
    if os.path.exists(espeak_exe) and os.path.exists(espeak_dll) and os.path.exists(espeak_data):
        return current_dir
        
    # Fallback to standard installation paths
    espeak_paths = [
        'C:\\Program Files\\eSpeak NG',
        'C:\\Program Files (x86)\\eSpeak NG',
        os.path.expanduser('~\\AppData\\Local\\Programs\\eSpeak NG')
    ]
    
    for path in espeak_paths:
        espeak_exe = os.path.join(path, 'espeak-ng.exe')
        if os.path.exists(espeak_exe):
            return path
    return None

def setup_espeak_environment():
    espeak_dir = find_espeak()
    if not espeak_dir:
        raise RuntimeError("espeak-ng not found. Please ensure espeak-ng.exe, libespeak-ng.dll, and espeak-ng-data are in the current directory")
    
    # Add espeak directory to PATH if not already there
    if espeak_dir not in os.environ['PATH']:
        os.environ['PATH'] = espeak_dir + os.pathsep + os.environ['PATH']
    
    # Set environment variables for phonemizer
    os.environ['PHONEMIZER_ESPEAK_PATH'] = os.path.join(espeak_dir, 'espeak-ng.exe')
    os.environ['PHONEMIZER_ESPEAK_LIBRARY'] = espeak_dir
    os.environ['PHONEMIZER_ESPEAK_DATA'] = os.path.join(espeak_dir, 'espeak-ng-data')
    
    # Print directory contents for debugging
    print(f"Contents of espeak directory:")
    for item in os.listdir(espeak_dir):
        print(f"  {item}")
    
    data_dir = os.path.join(espeak_dir, 'espeak-ng-data')
    if os.path.exists(data_dir):
        print(f"Contents of espeak-ng-data directory:")
        for item in os.listdir(data_dir):
            print(f"  {item}")
    
    # Verify espeak-ng works
    try:
        result = subprocess.run([os.path.join(espeak_dir, 'espeak-ng.exe'), '--version'], 
                              capture_output=True, text=True)
        print(f"espeak-ng version: {result.stdout.strip()}")
    except Exception as e:
        print(f"Warning: Could not verify espeak-ng version: {e}")
    
    return espeak_dir

class TextToSpeech(nn.Module):
    def __init__(self):
        super().__init__()
        # Setup espeak environment
        espeak_dir = setup_espeak_environment()
        print(f"Using espeak-ng from: {espeak_dir}")
        print(f"espeak-ng-data directory: {os.environ['PHONEMIZER_ESPEAK_DATA']}")
            
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
                print(f"Current environment:")
                print(f"PATH: {os.environ['PATH']}")
                print(f"PHONEMIZER_ESPEAK_PATH: {os.environ.get('PHONEMIZER_ESPEAK_PATH')}")
                print(f"PHONEMIZER_ESPEAK_LIBRARY: {os.environ.get('PHONEMIZER_ESPEAK_LIBRARY')}")
                print(f"PHONEMIZER_ESPEAK_DATA: {os.environ.get('PHONEMIZER_ESPEAK_DATA')}")
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