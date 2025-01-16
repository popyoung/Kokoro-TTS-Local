"""
Kokoro-TTS Local Generator
-------------------------
A Gradio interface for the Kokoro-TTS-Local text-to-speech system.
Supports multiple voices and audio formats, with cross-platform compatibility.

Key Features:
- Multiple voice models support
- Real-time generation with progress logging
- WAV, MP3, and AAC output formats
- Network sharing capabilities
- Cross-platform compatibility (Windows, macOS, Linux)

Dependencies:
- gradio: Web interface framework
- soundfile: Audio file handling
- pydub: Audio format conversion
- models: Custom module for voice model management
"""

import gradio as gr
import subprocess
import os
import sys
import platform
from datetime import datetime
import shutil
from pathlib import Path
import soundfile as sf
from pydub import AudioSegment

# Global configuration
CONFIG_FILE = "tts_config.json"  # Stores user preferences and paths
DEFAULT_OUTPUT_DIR = "outputs"    # Directory for generated audio files

def get_default_voices_path():
    """Get OS-agnostic path to voice models directory."""
    system = platform.system().lower()
    if system == "windows":
        base = os.getenv("APPDATA", os.path.expanduser("~"))
        return str(Path(base) / "huggingface" / "hub" / "models--hexgrad--Kokoro-82M" / "voices")
    else:  # Linux and macOS
        return str(Path.home() / ".cache" / "huggingface" / "hub" / "models--hexgrad--Kokoro-82M" / "voices")

def get_available_voices():
    """Get list of available voice models by checking the directory."""
    voices_path = get_default_voices_path()
    try:
        if not os.path.exists(voices_path):
            print(f"Voices directory not found: {voices_path}")
            return []
        voices = [os.path.splitext(f)[0] for f in os.listdir(voices_path) if f.endswith('.pt')]
        print("Available voices:", voices)
        return voices
    except Exception as e:
        print(f"Error retrieving voices: {e}")
        return []

def convert_audio(input_path: str, output_path: str, format: str):
    """Convert audio to specified format using pydub."""
    try:
        audio = AudioSegment.from_wav(input_path)
        if format == "mp3":
            audio.export(output_path, format="mp3", bitrate="192k")
        elif format == "aac":
            audio.export(output_path, format="aac", bitrate="192k")
        else:  # wav
            shutil.copy2(input_path, output_path)
        return True
    except Exception as e:
        print(f"Error converting audio: {e}")
        return False

def generate_tts_with_logs(voice, text, format):
    """Generate TTS audio with real-time logging and format conversion."""
    if not text.strip():
        return "❌ Error: Text required", None
    
    logs_text = ""
    try:
        # Use sys.executable to ensure correct Python interpreter
        cmd = [sys.executable, "tts_demo.py", "--text", text, "--voice", voice]
        
        # Use shell=True on Windows
        shell = platform.system().lower() == "windows"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=shell
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logs_text += output
                yield logs_text, None
        
        if process.returncode != 0:
            logs_text += "❌ Generation failed\n"
            yield logs_text, None
            return
            
        if not os.path.exists("output.wav"):
            logs_text += "❌ No output generated\n"
            yield logs_text, None
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.{format}"
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_path = Path(DEFAULT_OUTPUT_DIR) / filename
        
        # Convert audio using pydub
        if convert_audio("output.wav", str(output_path), format):
            logs_text += f"✅ Saved: {output_path}\n"
            os.remove("output.wav")
            yield logs_text, str(output_path)
        else:
            logs_text += "❌ Audio conversion failed\n"
            yield logs_text, None

    except Exception as e:
        logs_text += f"❌ Error: {str(e)}\n"
        yield logs_text, None

def create_interface(server_name="0.0.0.0", server_port=7860):
    """Create and configure Gradio interface with network sharing capabilities.
    
    Creates a web interface with:
    - Text input area
    - Voice model selection
    - Audio format selection (WAV/MP3/AAC)
    - Real-time progress logging
    - Audio playback and download
    - Example inputs for testing
    
    Args:
        server_name (str): Server address for network sharing (default: "0.0.0.0" for all interfaces)
        server_port (int): Port number to serve on (default: 7860)
    
    Returns:
        gr.Blocks: Configured Gradio interface ready for launching
    """
    theme = gr.themes.Base(
        primary_hue="zinc",
        secondary_hue="slate",
        neutral_hue="zinc",
        font=gr.themes.GoogleFont("Inter")
    )

    with gr.Blocks(theme=theme) as demo:
        gr.Markdown(
            """
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.5em; margin-bottom: 0.5rem;">🎙️ Kokoro-TTS Local Generator</h1>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; background: rgba(0,0,0,0.05); padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
                    <div style="text-align: left;">
                        <h3>✨ Instructions</h3>
                        <p>1. Type or paste your text into the input box</p>
                        <p>2. Choose a voice from the dropdown menu</p>
                        <p>3. Click Generate and wait for processing</p>
                        <p>4. Play or download your generated audio</p>
                    </div>
                    <div style="text-align: left; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 2rem;">
                        <h3>Introduction</h3>
                        <p>A local text-to-speech system using the Kokoro-82M model for natural-sounding voice synthesis.</p>
                        <p>Based on <a href="https://github.com/PierrunoYT/Kokoro-TTS-Local">Kokoro-TTS-Local</a> by <a href="https://github.com/PierrunoYT">PierrunoYT</a></p>
                        <p>Model: <a href="https://huggingface.co/hexgrad/Kokoro-82M">Kokoro-82M</a> by <a href="https://huggingface.co/hexgrad">hexgrad</a></p>
                        <p>Gradio Interface by ChatGPT, Claude & <a href="https://github.com/teslanaut">Teslanaut</a></p>
                    </div>
                </div>
            </div>
            """
        )
        
        text_input = gr.Textbox(
            label="✍️ Text to Synthesize",
            placeholder="Enter text here...",
            lines=3
        )
        
        generate_button = gr.Button("🔊 Generate", variant="primary")

        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    voice = gr.Dropdown(
                        choices=get_available_voices(),
                        label="🗣️ Select Voice",
                        value=None
                    )
                    format = gr.Radio(
                        choices=["wav", "mp3", "aac"],
                        label="🎵 Output Format",
                        value="wav"
                    )
            
            with gr.Column(scale=2):
                audio_output = gr.Audio(
                    label="🎧 Output",
                    type="filepath"
                )
        
        logs_output = gr.Textbox(
            label="📋 Process Log",
            lines=8,
            interactive=False
        )
        
        generate_button.click(
            fn=generate_tts_with_logs,
            inputs=[voice, text_input, format],
            outputs=[logs_output, audio_output]
        )

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,       # Default Gradio port
        share=True,             # Enable Gradio sharing link
        show_error=True
    )
