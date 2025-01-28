# Kokoro TTS Local

A local implementation of the Kokoro Text-to-Speech model, featuring dynamic module loading, automatic dependency management, and a web interface.

## Features

- Local text-to-speech synthesis using the Kokoro-82M model
- Multiple voice support with easy voice selection
- Automatic model and voice downloading
- Phoneme output support and visualization
- Interactive CLI for custom text input
- Voice listing functionality
- Cross-platform support (Windows, Linux, macOS)
- Web interface with real-time generation progress

## Prerequisites

- Python 3.8 or higher
- FFmpeg (optional, for MP3/AAC conversion)

## Installation

1. Create a Python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

You can use either the command-line interface or the web interface:

### Command Line Interface

1. List available voices:
```bash
python tts_demo.py --list-voices
```

2. Generate speech with default settings:
```bash
python tts_demo.py
```

3. Generate speech with specific voice and text:
```bash
python tts_demo.py --voice af_bella --text "Hello, world!"
```

4. Change speech speed:
```bash
python tts_demo.py --voice af_bella --speed 1.2
```

### Web Interface

For a more user-friendly experience, you can use the web interface:

```bash
python gradio_interface.py
```

Then open your browser to the URL shown in the console (typically http://localhost:7860).

The web interface provides:
- Easy voice selection from a dropdown menu
- Text input field with examples
- Real-time generation progress
- Audio playback in the browser
- Download options for generated audio

## Available Voices

The system includes various voices with different characteristics:
- American Female voices (af_*): bella, jessica, nicole, etc.
- American Male voices (am_*): adam, eric, michael, etc.
- British Female voices (bf_*): alice, emma, etc.
- British Male voices (bm_*): daniel, george, etc.

## Troubleshooting

The application should work out of the box. If you encounter any issues:

1. Make sure you're using a Python virtual environment
2. Verify all dependencies are installed correctly
3. Check if your system meets the prerequisites
4. If the issue persists, please open an issue on GitHub with:
   - Your system information
   - Complete error message
   - Steps to reproduce the problem

## Project Structure

```
.
├── .cache/                 # Cache directory for downloaded models
│   └── huggingface/       # Hugging Face model cache
├── .git/                   # Git repository data
├── .gitignore             # Git ignore rules
├── __pycache__/           # Python cache files
├── voices/                # Voice model files (downloaded on demand)
│   └── ...               # Voice files are downloaded when needed
├── venv/                  # Python virtual environment
├── LICENSE                # Apache 2.0 License file
├── README.md             # Project documentation
├── models.py             # Core TTS model implementation
├── gradio_interface.py   # Web interface implementation
├── requirements.txt      # Python dependencies
└── tts_demo.py          # CLI implementation
```

## Model Information

The project uses the latest Kokoro model from Hugging Face:
- Repository: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
- Model file: `kokoro-v1_0.pth`
- Sample rate: 24kHz
- Voice files: Located in the `voices/` directory (downloaded automatically)
- Available voices: 26+ voices (see [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md))
- Languages: American English ('a'), British English ('b')

## Contributing

Feel free to contribute by:
1. Opening issues for bugs or feature requests
2. Submitting pull requests with improvements
3. Helping with documentation
4. Testing different voices and reporting issues
5. Suggesting new features or optimizations
6. Testing on different platforms and reporting results

## License

Apache 2.0 - See LICENSE file for details 