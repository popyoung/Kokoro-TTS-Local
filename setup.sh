#!/bin/bash

echo "Setting up Kokoro TTS Local..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies using uv
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install FFmpeg if needed
if [ "$(uname)" == "Linux" ]; then
    echo "Installing FFmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
elif [ "$(uname)" == "Darwin" ]; then
    echo "Installing FFmpeg..."
    brew install ffmpeg
fi

echo "Setup complete! Run 'source venv/bin/activate' to activate the virtual environment." 