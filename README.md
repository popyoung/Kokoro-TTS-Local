# Kokoro TTS

⚠️ **CURRENT STATUS: NOT WORKING - HELP NEEDED** ⚠️

This project is currently experiencing issues with the espeak-ng integration and phonemizer library. We're looking for contributors who can help fix these problems.

A local implementation of the Kokoro Text-to-Speech system, based on the [Kokoro-82M model](https://huggingface.co/hexgrad/Kokoro-82M).

## Known Issues

- Phonemizer library fails to detect espeak-ng even when properly installed
- Integration between Python phonemizer and espeak-ng needs fixing
- Model loading process needs debugging

## Features (When Working)

- High-quality English text-to-speech synthesis
- Multiple voice styles
- Adjustable speech speed
- Local inference without internet dependency (after initial model download)

## Prerequisites

- Python 3.8 or higher
- espeak-ng (text-to-speech engine)
- Git LFS (for model download)

## Installation

1. Install espeak-ng:
   - Download from [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases)
   - Install for all users
   - Ensure espeak-ng-data directory is properly set up

2. Set up Python environment:
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

- `tts_demo.py` - Demo script showing basic usage
- `models.py` - Model implementation and utilities
- `requirements.txt` - Python dependencies

## How to Contribute

If you have experience with:
- Python text-to-speech systems
- espeak-ng integration
- phonemizer library
- PyTorch model deployment

Please consider contributing to fix the current issues. You can:
1. Fork the repository
2. Create a branch for your fixes
3. Submit a pull request

## Credits

- Original model: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
- Based on papers:
  - [arxiv: 2306.07691](https://arxiv.org/abs/2306.07691)
  - [arxiv: 2203.02395](https://arxiv.org/abs/2203.02395)

## License

Apache-2.0 License (following the original model's license) 