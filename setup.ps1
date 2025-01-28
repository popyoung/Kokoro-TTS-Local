#Requires -Version 5.0
<#
.SYNOPSIS
    Setup script for Kokoro TTS Local
.DESCRIPTION
    Installs required dependencies and sets up the environment for Kokoro TTS Local
.NOTES
    Author: PierrunoYT
    License: Apache 2.0
#>

[CmdletBinding()]
param()

Write-Host "Setting up Kokoro TTS Local..."

# Check Python version
$pythonVersion = python --version 2>&1
if (-not $pythonVersion) {
    Write-Host "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
}

# Check for espeak-ng
$espeakPath = "$env:USERPROFILE\AppData\Local\espeak-ng"
if (-not (Test-Path $espeakPath)) {
    Write-Host "`nespeak-ng not found. Installing via pip..."
    pip install espeakng-loader --user
    
    if (-not $?) {
        Write-Host "Error installing espeak-ng. Please install manually:"
        Write-Host "1. Download espeak-ng from: https://github.com/espeak-ng/espeak-ng/releases"
        Write-Host "2. Install it to the default location"
        Write-Host "3. Add it to your system PATH"
        exit 1
    }
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Create temporary activation for setup
$tempActivateContent = @"
`$env:VIRTUAL_ENV = "$((Get-Item .).FullName)\venv"
`$env:_OLD_VIRTUAL_PATH = `$env:PATH
`$env:PATH = "`$env:VIRTUAL_ENV\Scripts;" + `$env:PATH
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
`$env:PYTHONIOENCODING = "utf-8"
"@

$tempActivatePath = ".\temp_activate.ps1"
$tempActivateContent | Out-File -FilePath $tempActivatePath -Encoding UTF8

# Activate virtual environment for setup
Write-Host "Activating virtual environment for setup..."
. $tempActivatePath

# Install core dependencies first
Write-Host "Installing core dependencies..."
python -m pip install --upgrade pip
pip install wheel setuptools
pip install espeakng-loader>=0.1.6 phonemizer-fork>=3.0.2

# Verify espeak-ng loader installation
Write-Host "Verifying espeak-ng installation..."
python -c "import espeakng_loader; print('espeak-ng path:', espeakng_loader.get_library_path())"

# Install remaining dependencies
Write-Host "Installing remaining dependencies..."
pip install -r requirements.txt

# Check for FFmpeg
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host "`nFFmpeg not found. Please install FFmpeg manually:"
    Write-Host "1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    Write-Host "2. Extract to a folder"
    Write-Host "3. Add the bin folder to your system PATH"
}

# Clean up temporary activation script
Remove-Item $tempActivatePath

# Print completion message with clear instructions
Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nTo start using Kokoro TTS Local:"
Write-Host "1. First activate the environment:"
Write-Host "   .\venv\Scripts\ActivateUTF8.ps1" -ForegroundColor Cyan
Write-Host "`n2. Then run the program:"
Write-Host "   python run.py" -ForegroundColor Cyan
Write-Host "`nNote: You'll need to activate the environment each time you open a new terminal." 