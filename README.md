# Kokoro TTS Local

A local implementation of the Kokoro Text-to-Speech model, featuring dynamic module loading, automatic dependency management, and a web interface.

## Current Status

✅ **WORKING - v1.0 READY** ✅

The project has been updated with:
- Support for Kokoro v1.0 model
- Official kokoro and misaki libraries
- 24kHz sample rate support
- 26+ voice models
- American and British English support
- All previous features

## Features

- Local text-to-speech synthesis using the Kokoro model
- Automatic espeak-ng setup using kokoro
- Multiple voice support with easy voice selection
- Phoneme output support and visualization
- Interactive CLI for custom text input
- Voice listing functionality
- Comprehensive error handling and logging
- Cross-platform support (Windows, Linux, macOS)
- **NEW: Web Interface Features**
  - Modern, user-friendly UI
  - Real-time generation progress
  - Multiple output formats (WAV, MP3, AAC)
  - Network sharing capabilities
  - Audio playback and download
  - Voice selection dropdown
  - Detailed process logging

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection (for initial model download)
- FFmpeg (required for MP3/AAC conversion):
  - Windows: Manual installation (see setup instructions)
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

### Windows-Specific Requirements
For optimal performance on Windows, you should either:
1. Enable Developer Mode:
   - Open Windows Settings
   - Navigate to System > Developer settings
   - Turn on Developer Mode
   
OR

2. Run Python as Administrator:
   - Right-click your terminal (PowerShell/Command Prompt)
   - Select "Run as administrator"
   - Run the commands from there

Additionally:
- Use PowerShell or Command Prompt with UTF-8 encoding:
  ```powershell
  # Set console to UTF-8 mode
  chcp 65001
  ```
- Or set system-wide UTF-8 encoding:
  1. Open Windows Settings
  2. Go to Time & Language > Language & Region
  3. Click "Administrative language settings"
  4. Click "Change system locale"
  5. Check "Beta: Use Unicode UTF-8 for worldwide language support"
  6. Restart your computer

This ensures proper handling of international characters and model files.

## Dependencies

Core Python packages:
```txt
kokoro  # Official Kokoro TTS library
misaki  # G2P library for Kokoro
torch   # PyTorch for model inference
soundfile  # Audio file handling
huggingface-hub  # Model downloads
gradio>=4.0.0  # Web interface
pydub  # Audio format conversion
```

System dependencies:
- FFmpeg: Required for MP3/AAC conversion
- Python 3.8+: Required for running the application

## Setup

We use Python's built-in virtual environment for dependency management.

### Windows
```powershell
# Clone the repository
git clone https://github.com/PierrunoYT/Kokoro-TTS-Local.git
cd Kokoro-TTS-Local

# Run the setup script
.\setup.ps1

# If you get a security error, try:
powershell -ExecutionPolicy Bypass -File setup.ps1

# Install FFmpeg manually:
# 1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# 2. Extract to a folder
# 3. Add the bin folder to your system PATH

# When returning to the project later, always activate with:
.\venv\Scripts\ActivateUTF8.ps1
```

### Linux/macOS
```bash
# Clone the repository
git clone https://github.com/PierrunoYT/Kokoro-TTS-Local.git
cd Kokoro-TTS-Local

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup scripts will:
1. Create a Python virtual environment
2. Install all required dependencies
3. Guide you through FFmpeg installation if needed

## Usage

After setup, simply run:
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