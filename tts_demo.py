import torch
import soundfile as sf
from models import build_model, load_voice, generate_speech

def main():
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    try:
        # Build model and load voice
        model = build_model('kokoro-v0_19.pth', device)
        voice = load_voice('af', device)  # Default voice (Bella & Sarah mix)
        
        # Test text
        text = "Hello, welcome to this text-to-speech test."
        
        # Generate speech
        audio, phonemes = generate_speech(model, text, voice, lang='a', device=device)
        
        if audio is not None:
            # Save audio
            output_file = "output.wav"
            sample_rate = 24000
            sf.write(output_file, audio, sample_rate)
            print(f"Audio saved to {output_file}")
            print(f"Phonemes: {phonemes}")
        else:
            print("Failed to generate audio")

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 