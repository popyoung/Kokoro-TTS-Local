import torch
from models import build_model, load_voice, generate_speech
import argparse

def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Kokoro TTS Demo')
        parser.add_argument('--text', type=str, help='Text to synthesize (optional)')
        parser.add_argument('--voice', type=str, default='af', help='Voice to use (default: af)')
        args = parser.parse_args()

        # Set up device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {device}")
        
        # Build model and load voice
        model = build_model('kokoro-v0_19.pth', device)
        voice = load_voice(args.voice, device)
        
        # Get text input
        if args.text:
            text = args.text
        else:
            print("\nEnter the text you want to convert to speech (or press Enter for default text):")
            text = input("> ").strip()
            if not text:
                text = "Hello, welcome to this text-to-speech test."
        
        print(f"\nGenerating speech for: '{text}'")
        audio, phonemes = generate_speech(model, text, voice, lang='a', device=device)
        
        if audio is not None:
            print(f"Generated phonemes: {phonemes}")
            import soundfile as sf
            output_file = 'output.wav'
            sf.write(output_file, audio, 22050)
            print(f"\nAudio saved to {output_file}")
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 