#!/usr/bin/env python3
"""Verify Whisper transcription environment is ready."""
import sys
import subprocess

def check_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ ffmpeg installed")
            return True
        print("✗ ffmpeg not found")
        return False
    except FileNotFoundError:
        print("✗ ffmpeg not installed — install with: sudo apt install ffmpeg")
        return False

def check_whisper():
    try:
        import whisper
        print(f"✓ whisper installed (v{whisper.__version__})")
        return True
    except ImportError:
        print("✗ whisper not installed — install with: pip install openai-whisper")
        return False

def check_model():
    try:
        import whisper
        model = whisper.load_model('tiny')
        print("✓ tiny model loaded")
        return True
    except Exception as e:
        print(f"✗ model load failed: {e}")
        return False

def main():
    print("Whisper environment check:")
    ok = True
    ok &= check_ffmpeg()
    ok &= check_whisper()
    ok &= check_model()
    if ok:
        print("\n✓ Environment ready for transcription")
    else:
        print("\n✗ Environment incomplete — fix issues above")
        sys.exit(1)

if __name__ == '__main__':
    main()