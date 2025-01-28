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

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Create activation script with UTF-8 encoding
$activateContent = @'
# Set UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null

# Activate virtual environment
& "$PSScriptRoot\Activate.ps1"
'@

# Save the custom activation script
$customActivatePath = ".\venv\Scripts\ActivateUTF8.ps1"
$activateContent | Out-File -FilePath $customActivatePath -Encoding UTF8

# Activate virtual environment with UTF-8 encoding
Write-Host "Activating virtual environment..."
& $customActivatePath

# Install pip and dependencies
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check for FFmpeg
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host "FFmpeg not found. Please install FFmpeg manually:"
    Write-Host "1. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    Write-Host "2. Extract to a folder"
    Write-Host "3. Add the bin folder to your system PATH"
}

Write-Host "`nSetup complete! Run '.\venv\Scripts\ActivateUTF8.ps1' to activate the virtual environment." 