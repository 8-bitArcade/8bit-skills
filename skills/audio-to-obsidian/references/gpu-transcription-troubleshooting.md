# GPU Transcription Troubleshooting

## Common Failures & Fixes

### 1. `FileNotFoundError: [WinError 2]` on `transcribe()`
**Cause**: Missing ffmpeg on Windows. Whisper uses ffmpeg internally to decode audio.
**Fix**: `winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`
**Verify**: `where ffmpeg` on Windows returns a path.
**Note**: After install, restart SSH session so PATH updates take effect.

### 2. "filename, directory name, or volume label syntax is incorrect"
**Cause**: Backslashes in SSH commands get mangled by the SSH shell layer.
**Fix**: Use forward slashes everywhere in SSH commands (`C:/Temp/whisper_work` not `C:\Temp\whisper_work`). PowerShell on Windows accepts forward slashes natively.

### 3. Direct Whisper CLI fails via SSH (`FileNotFoundError`)
**Cause**: CLI path parsing breaks over SSH subprocess.
**Fix**: Ship `run_whisper.py` helper script that calls `whisper.load_model()` + `model.transcribe()` directly, bypassing CLI entirely.

### 4. Batch transcription killed silently (exit -1, no output)
**Cause**: Default 600s timeout too short for 20+ files (~30-45 min).
**Fix**: Use `timeout 1800` or background with `notify_on_complete=true`.

### 5. GPU transcription fails, falls back to CPU
**Cause**: Windows machine offline or SSH unreachable.
**Fix**: Script auto-falls back to `tiny` model on VPS CPU. If you need quality, wait for Windows machine to come back online.

## SSH Command Pattern (Working)
```bash
ssh 123@100.110.93.103 'cd C:/Temp/whisper_work && python run_whisper.py large-v3-turbo "C:/Temp/whisper_work/file.m4a" "C:/Temp/whisper_work/file.json"'
```
- Single quotes around entire PowerShell command
- `&&` to chain (not `;`)
- Double quotes for file paths inside command
- Forward slashes throughout

## Remote Environment
- **Host**: `123@100.110.93.103`
- **Work dir**: `C:/Temp/whisper_work/`
- **Python**: `C:\Program Files\Python313\python.exe`
- **Model cache**: `C:\Users\123\.cache\whisper\large-v3-turbo.pt` (~1.5GB)
- **GPU**: NVIDIA GeForce RTX 3090 (CUDA available)
