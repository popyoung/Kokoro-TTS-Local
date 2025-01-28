#!/bin/bash

echo "Setting up Kokoro TTS Local..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install espeak-ng if not present
if ! command -v espeak-ng &> /dev/null; then
    echo "Installing espeak-ng..."
    if [ "$(uname)" == "Linux" ]; then
        sudo apt-get update
        sudo apt-get install -y espeak-ng
    elif [ "$(uname)" == "Darwin" ]; then
        brew install espeak-ng
    else
        echo "Please install espeak-ng manually if not already installed."
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Create UTF-8 activation script
cat > venv/bin/activate_utf8 << 'EOL'
# Source original activate script
. "$(dirname "${BASH_SOURCE[0]}")/activate"

# Set UTF-8 encoding for Python
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Update prompt to show UTF-8
PS1="(venv-utf8) ${PS1-}"
EOL

# Make the activation script executable
chmod +x venv/bin/activate_utf8

# Create temporary activation for setup
cat > ./temp_activate << EOF
export VIRTUAL_ENV="$PWD/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
unset PYTHON_HOME
EOF

# Activate virtual environment for setup
echo "Activating virtual environment for setup..."
. ./temp_activate

# Install core dependencies first
echo "Installing core dependencies..."
python3 -m pip install --upgrade pip
pip install wheel setuptools
pip install espeakng-loader>=0.1.6 phonemizer-fork>=3.0.2

# Verify espeak-ng loader installation
echo "Verifying espeak-ng installation..."
python3 -c "import espeakng_loader; print('espeak-ng path:', espeakng_loader.get_library_path())"

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt

# Install FFmpeg if needed
if [ "$(uname)" == "Linux" ]; then
    if ! command -v ffmpeg &> /dev/null; then
        echo "Installing FFmpeg..."
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    fi
elif [ "$(uname)" == "Darwin" ]; then
    if ! command -v ffmpeg &> /dev/null; then
        echo "Installing FFmpeg..."
        brew install ffmpeg
    fi
else
    echo "Please install FFmpeg manually if not already installed."
fi

# Clean up temporary activation script
rm ./temp_activate

# Print completion message with clear instructions
echo -e "\n✅ Setup complete!"
echo -e "\nTo start using Kokoro TTS Local:"
echo -e "1. First activate the environment:"
echo -e "   \033[1msource venv/bin/activate_utf8\033[0m"
echo -e "\n2. Then run the program:"
echo -e "   \033[1mpython run.py\033[0m"
echo -e "\nNote: You'll need to activate the environment each time you open a new terminal." 