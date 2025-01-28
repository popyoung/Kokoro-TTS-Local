"""Wrapper script to handle encoding and launch TTS applications"""
import sys
import os

# Set UTF-8 encoding for Python
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    # Set console code page to UTF-8 on Windows
    os.system("chcp 65001 > nul")

def main():
    print("\n🎙️ Kokoro TTS Local")
    print("-------------------")
    print("1. TTS Demo (Command Line)")
    print("2. Web Interface")
    print("q. Quit")
    
    while True:
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == '1':
            import tts_demo
            tts_demo.main()
            break
        elif choice == '2':
            import gradio_interface
            break
        elif choice in ['q', 'quit', 'exit']:
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or q")

if __name__ == "__main__":
    main() 