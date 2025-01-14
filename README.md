# Kokoro TTS Local

A local implementation of the Kokoro Text-to-Speech model.

## Current Status

⚠️ **WORK IN PROGRESS** ⚠️

The project is currently being updated to use better dependency management and improved module loading.

## Features

- Local text-to-speech synthesis using the Kokoro model
- Automatic espeak-ng setup using espeakng-loader
- Multiple voice support with easy voice selection
- Phoneme output support
- Interactive CLI for custom text input
- Voice listing functionality

## Dependencies

```txt
torch
phonemizer-fork
transformers
scipy
munch
soundfile
huggingface-hub
espeakng-loader
```

## Setup

1. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Usage

### List Available Voices
To see all available voices:
```powershell
python tts_demo.py --list-voices
```

### Basic Usage
Run the demo script with default text and voice:
```powershell
python tts_demo.py
```

### Custom Text
Specify your own text:
```powershell
python tts_demo.py --text "Your custom text here"
```

### Voice Selection
Choose a different voice:
```powershell
python tts_demo.py --voice "af" --text "Custom text with specific voice"
```

### Interactive Mode
If you run without any arguments, you'll be prompted to enter text interactively:
```powershell
python tts_demo.py
```

The script will:
1. Download necessary model files from Hugging Face
2. Set up espeak-ng automatically
3. Generate speech from your text
4. Save the output as 'output.wav'

## Project Structure

- `models.py`: Core model loading and speech generation functionality
  - Model building and initialization
  - Voice loading and management
  - Speech generation
  - Voice listing functionality
- `tts_demo.py`: Demo script showing basic usage
  - Command-line interface
  - Interactive text input
  - Voice selection
- `requirements.txt`: Project dependencies

## Model Information

The project uses the Kokoro-82M model from Hugging Face:
- Repository: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
- Model file: `kokoro-v0_19.pth`
- Voice files: Located in the `voices/` directory
- Supports multiple voice styles (use `--list-voices` to see available options)

## Contributing

Feel free to contribute by:
1. Opening issues for bugs or feature requests
2. Submitting pull requests with improvements
3. Helping with documentation
4. Testing different voices and reporting issues

## License

This project is licensed under the Apache 2.0 License. 