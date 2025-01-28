# Kokoro TTS Local

A local implementation of the Kokoro Text-to-Speech model, featuring dynamic module loading, automatic dependency management, and a web interface.

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

3. Run the program:
```bash
python run.py
```

## Features

- Local text-to-speech synthesis using the Kokoro model
- Multiple voice support with easy voice selection
- Phoneme output support and visualization
- Interactive CLI for custom text input
- Voice listing functionality
- Cross-platform support (Windows, Linux, macOS)
- Web interface with real-time generation progress

## Prerequisites

- Python 3.8 or higher
- FFmpeg (optional, for MP3/AAC conversion)

## Usage

After installation, run:
```bash
python run.py
```

This will show an interactive menu where you can choose:
1. TTS Demo - Command line interface for direct text-to-speech conversion
2. Web Interface - Browser-based interface with additional features

Both interfaces are interactive and will guide you through the process.

### TTS Demo Features
- Voice selection
- Text input
- Phoneme visualization
- WAV file output

### Web Interface Features
- Modern, user-friendly UI
- Real-time generation progress
- Multiple output formats (WAV/MP3/AAC)
- Network sharing capabilities
- Audio playback and download
- Voice selection dropdown
- Detailed process logging

Note: If port 7860 is already in use for the web interface, Gradio will automatically try the next available port (7861, 7862, etc.).
Check the terminal output for the correct URL.

## Project Structure

```
.
├── .cache/                 # Cache directory for downloaded models
│   └── huggingface/       # Hugging Face model cache
├── .git/                   # Git repository data
├── .gitignore             # Git ignore rules
├── .gradio/               # Gradio cache and configuration
│   ├── certificate.pem    # SSL certificate for Gradio
│   └── ...               # Other Gradio config files
├── __pycache__/           # Python cache files
├── outputs/               # Generated audio output files
│   ├── output.wav        # Default output file
│   ├── output.mp3        # MP3 converted files
│   └── output.aac        # AAC converted files
├── voices/                # Voice model files (downloaded on demand)
│   └── ...               # Voice files are downloaded when needed
├── venv/                  # Python virtual environment
├── LICENSE                # Apache 2.0 License file
├── README.md             # Project documentation
├── gradio_interface.py    # Web interface implementation
├── models.py             # Core TTS model implementation
├── requirements.txt      # Python dependencies
├── setup.ps1             # Windows setup script
├── setup.sh              # Linux/macOS setup script
└── tts_demo.py          # CLI demo implementation
```

## Model Information

The project uses the latest Kokoro model from Hugging Face:
- Repository: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
- Model file: `kokoro-v1_0.pth`
- Sample rate: 24kHz (upgraded from 22.05kHz)
- Voice files: Located in the `voices/` directory (downloaded automatically)
- Available voices: 26+ voices (see [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md))
- Languages: American English ('a'), British English ('b')

## Technical Details

- Sample rate: 24kHz (upgraded from 22.05kHz)
- Input: Text in any language (English recommended)
- Output: WAV/MP3/AAC audio file
- Dependencies managed by kokoro library
- Automatic espeak-ng installation via kokoro
- Error handling includes stack traces for debugging
- Cross-platform compatibility through setup scripts

## Contributing

Feel free to contribute by:
1. Opening issues for bugs or feature requests
2. Submitting pull requests with improvements
3. Helping with documentation
4. Testing different voices and reporting issues
5. Suggesting new features or optimizations
6. Testing on different platforms and reporting results

## License

This project is licensed under the Apache 2.0 License. 