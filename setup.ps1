# Setup script for Windows
Write-Host "Setting up Kokoro TTS Local..."

# Check if uv is installed
$uvExists = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvExists) {
    Write-Host "Installing uv package manager..."
    iwr -useb https://astral.sh/uv/install.ps1 | iex
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    uv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies using uv
Write-Host "Installing dependencies..."
uv pip install -r requirements.txt

# Install FFmpeg if not already installed (using winget)
$ffmpegExists = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpegExists) {
    Write-Host "Installing FFmpeg..."
    winget install -e --id Gyan.FFmpeg
}

Write-Host "Setup complete! Run '.\venv\Scripts\Activate.ps1' to activate the virtual environment." 