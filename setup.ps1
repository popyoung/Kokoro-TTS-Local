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

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Create UTF-8 activation script
$activateContent = @"
# Original Activate.ps1 content
`$script:THIS_PATH = `$myinvocation.mycommand.path
`$script:BASE_DIR = Split-Path (Resolve-Path "`$THIS_PATH/..") -Parent

function global:deactivate([switch]`$NonDestructive) {
    if (Test-Path variable:_OLD_VIRTUAL_PATH) {
        `$env:PATH = `$_OLD_VIRTUAL_PATH
        Remove-Variable "_OLD_VIRTUAL_PATH" -Scope global
    }

    if (Test-Path function:_old_virtual_prompt) {
        `$function:prompt = `$function:_old_virtual_prompt
        Remove-Item function:\_old_virtual_prompt
    }

    if (`$env:VIRTUAL_ENV) {
        Remove-Item env:VIRTUAL_ENV -ErrorAction SilentlyContinue
    }

    if (!`$NonDestructive) {
        # Self destruct!
        Remove-Item function:deactivate
    }
}

deactivate -nondestructive

`$env:VIRTUAL_ENV = "`$BASE_DIR"
`$env:_OLD_VIRTUAL_PATH = `$env:PATH
`$env:PATH = "`$env:VIRTUAL_ENV/Scripts;" + `$env:PATH

# Set UTF-8 encoding for Python and console
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
`$env:PYTHONIOENCODING = "utf-8"
chcp 65001 > `$null

function global:_old_virtual_prompt {
    ""
}
`$function:_old_virtual_prompt = `$function:prompt

function global:prompt {
    # Add a prefix to the current prompt, but don't discard it.
    Write-Host -NoNewline -ForegroundColor Green "(venv) "
    _old_virtual_prompt
}
"@

# Save the activation script
$activateUtf8Path = "venv\Scripts\ActivateUTF8.ps1"
$activateContent | Out-File -FilePath $activateUtf8Path -Encoding UTF8

# Create a temporary activation script that we'll use for the setup process
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

# Activate virtual environment for the setup process
Write-Host "Activating virtual environment for setup..."
. $tempActivatePath

# Install pip and dependencies
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install wheel setuptools
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