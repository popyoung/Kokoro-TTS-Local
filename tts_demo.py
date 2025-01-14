import torch
from models import build_model, load_voice, generate_speech

def main():
    try:
        # Set up device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        # Build model and load voice
        model = build_model('kokoro-v0_19.pth', device)  # Fixed filename with underscore
        voice = load_voice('af', device)
        
        # Generate speech
        text = "Hello, welcome to this text-to-speech test."
        audio, phonemes = generate_speech(model, text, voice, lang='a', device=device)
        
        if audio is not None:
            print(f"Generated phonemes: {phonemes}")
            import soundfile as sf
            sf.write('output.wav', audio, 22050)
            print("Audio saved to output.wav")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 