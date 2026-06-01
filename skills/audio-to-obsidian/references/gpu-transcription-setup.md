# GPU Transcription Setup

## Overview
Audio transcription runs on Windows RTX 3090 (100.110.93.103) via SSH. Uses `large-v3-turbo` model (~1.5GB) for best quality. Falls back to VPS CPU `tiny` model if GPU unavailable.

## Prerequisites
- `openai-whisper` + CUDA/PyTorch installed on Windows
- **ffmpeg installed on Windows** (mandatory — see Pitfalls below)
- SSH access to `123@100.110.93.103`

## How It Works
1. `transcribe-single.py` / `batch-transcribe.py` SCP audio to `C:\Temp\whisper_work\`
2. Ships `run_whisper.py` helper script to same dir
3. Runs via PowerShell: sets PATH, calls `python run_whisper.py large-v3-turbo <input> <output>`
4. SCPs JSON result back, cleans remote files
5. Converts JSON to Obsidian markdown note

## SSH Command Pattern
```powershell
ssh 123@100.110.93.103 '$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User"); cd C:\Temp\whisper_work; python run_whisper.py large-v3-turbo input.m4a output.json'
```
- Must set PATH manually in SSH session (winget installs don't persist in SSH env)
- Use single quotes for the entire command string (PowerShell)
- `run_whisper.py` takes 3 args: model_name, input_file, output_file

## Pitfalls
- **Missing ffmpeg = FileNotFoundError**: Whisper uses ffmpeg internally to decode audio. If ffmpeg isn't installed or in PATH, `transcribe()` throws `FileNotFoundError: [WinError 2]` — looks like a missing file but it's ffmpeg. Install: `winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`
- **PATH not persisted**: After winget install, PATH updates don't carry into SSH sessions. Must explicitly set PATH in the SSH command (see pattern above)
- **Direct Whisper CLI fails on Windows via SSH**: `whisper <file> ...` invoked via SSH subprocess throws `FileNotFoundError`. Always use `run_whisper.py` helper instead
- **Windows paths require backslashes**: Use `C:\Temp\whisper_work` not forward slashes
- **First run downloads model**: `large-v3-turbo` (~1.5GB) downloads to `~/.cache/whisper/` on first run. Allow extra time for initial transcription

## Model Notes
- `large-v3-turbo`: Best quality, ~1.5GB. Default for GPU.
- `tiny`: VPS CPU fallback only (~1GB). Lowest accuracy.
- `small`/`medium`: OOM on VPS (7.8GB RAM). Do not use.

## Verified Working
- 2026-05-28: `large-v3-turbo` on RTX 3090 + ffmpeg 8.1.1 via winget. Test transcription of 4min m4a completed successfully with accurate timestamps and text.
