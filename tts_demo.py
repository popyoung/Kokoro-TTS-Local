import torch
import soundfile as sf
import os
from models import TextToSpeech

def setup_model():
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    try:
        # Load model
        model = TextToSpeech().to(device)
        model.eval()  # Set to evaluation mode
        return model, device
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, device

def generate_speech(text, model, device, style=0, speed=1.0):
    try:
        # Generate audio
        with torch.no_grad():
            audio = model.generate(text, style=style, speed=speed)
        return audio
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def main():
    # Setup
    model, device = setup_model()
    if model is None:
        return

    # Test with a short text first
    text = "Hello"
    
    # Try with default settings first
    audio = generate_speech(text, model, device)
    
    if audio is not None:
        output_file = "output_test.wav"
        sample_rate = 24000
        sf.write(output_file, audio, sample_rate)
        print(f"Audio saved to {output_file}")
    else:
        print("Failed to generate audio")

if __name__ == "__main__":
    main() 