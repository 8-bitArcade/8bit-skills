---
name: audio-to-obsidian
description: Transcribe audio files to Obsidian notes with summary, transcript, and action items
triggers:
  - transcribe audio
  - audio to note
  - meeting recording
  - voice memo
  - audio transcription
---

# Audio to Obsidian Notes

Transcribe audio files and create formatted Obsidian notes.

## Prerequisites
- `openai-whisper` installed in Hermes venv
- Obsidian vault mounted at `~/.obsidian_vault/`
- Windows machine ({{INFERENCE_HOST_IP}}) has `openai-whisper` + CUDA/PyTorch + **ffmpeg** for GPU transcription
- **ffmpeg on Windows is mandatory**: Whisper uses ffmpeg internally to decode audio. Without it, `whisper.transcribe()` crashes with `FileNotFoundError`. Install via `winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`. After install, restart the SSH session so PATH updates take effect.

## Workflow

### Single file transcription (auto GPU → CPU fallback)
```bash
source ~/.hermes/venv/bin/activate
python3 ~/.hermes/skills/audio-to-obsidian/scripts/transcribe-single.py <audio_file_path>
```
Automatically uses `{{WHISPER_MODEL}}` on Windows {{GPU_MODEL}} GPU for best quality. Falls back to `tiny` on VPS CPU if GPU unavailable. First run downloads model (~1.5GB) to Windows machine.

### Batch transcription (all files)
```bash
source ~/.hermes/venv/bin/activate
python3 ~/.hermes/skills/audio-to-obsidian/scripts/batch-transcribe.py
```
Processes all unique `.m4a` files from `~/urecorder/` in chronological order. Skips already-transcribed files. Reports progress. Uses GPU by default with CPU fallback.

**Timeout note**: Large batches (20+ files) take 30-45 min. Run with `timeout 1800` or as a background process with `notify_on_complete=true`. Without extended timeout, the process gets killed silently (exit -1) with no output.

### LLM Post-Processing (quality improvement)
After GPU transcription, run LLM post-processing to fix misheard words, grammar, and formatting:
```bash
source ~/.hermes/venv/bin/activate
python3 ~/.hermes/skills/audio-to-obsidian/scripts/post_process_llm.py          # all transcripts
python3 ~/.hermes/skills/audio-to-obsidian/scripts/post_process_llm.py URecorder_20250707  # specific file
```
Uses `{{MODEL_LARGE}}` on {{LMS}}. Creates `.backup.md` of each original before overwriting. Temperature 0.3 for conservative corrections.

### Output location
- Notes saved to: `~/.obsidian_vault/Efforts/Transcript/`
- Filename matches source: `URecorder_YYYYMMDD_HHMMSS.md`
- Backup originals: `URecorder_YYYYMMDD_HHMMSS.backup.md` (created during LLM post-processing)

## Model Selection
- `{{WHISPER_MODEL}}` (~1.5GB): GPU transcription on Windows {{GPU_MODEL}}. Best quality. Default for `transcribe-gpu.py`.
- `medium` (~5GB): Too large for VPS (7.8GB RAM) — causes OOM kills.
- `small` (~2.5GB): Also OOM-kills on VPS. Do not use.
- `tiny` (~1GB): VPS fallback only. Lowest accuracy.

**Always pass `--language en`** to reduce hallucination on tech terms, names, and non-English-sounding words. Omitting this causes Whisper to guess language and introduces errors.

## Model Upgrade History
- 2026-05-29: Added LLM post-processing step using `{{MODEL_DEFAULT}}` on {{LMS}}. 27b model too slow (timeouts on large files). Timeout set to 300s. Script filters out `.backup.md` files to avoid double-processing. Creates `.backup.md` of originals before overwriting.
- 2026-05-28: Upgraded from `tiny` → GPU `{{WHISPER_MODEL}}` on Windows {{GPU_MODEL}}. User prioritizes quality over speed. VPS CPU models (`small`, `medium`) cause OOM — GPU is now the primary path. Verified working with ffmpeg installed via winget.

## Pre-flight Check

Run the verification script before transcribing:
```bash
source ~/.hermes/venv/bin/activate
python3 ~/.hermes/skills/audio-to-obsidian/scripts/verify-whisper.py
```

## Audio Source Options
- Telegram/Discord upload (saved to cache)
- Local files in vault/home directory
- **URecorder via SSHFS**: Mounted at `~/urecorder/` (Windows path: `G:\My Drive\URecorder`). Mount with: `{{REMOTE_MOUNT_TOOL}} {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}:"G:/My Drive/URecorder" ~/urecorder -o allow_other,reconnect,_netdev`
- **GDrive via rclone**: `gdrive:` remote has `scope = drive.file` (limited access). `drive:` token expired 2026-03. Re-auth required for full GDrive access.

## Audio File Drop Watcher

The watcher script (`~/.hermes/scripts/watch-urecorder.py`) polls `~/urecorder/` every 30m for new `.m4a` files. State file: `~/.hermes/cron_state/last_transcribed_files.json` (tracks filenames + mtimes).

**Critical**: The watcher script MUST save state after EVERY run — not just when new files are detected. If state isn't saved, every run treats all files as "new" and duplicates transcription work. The script was broken this way initially — it loaded state but never called `save_state()`.

**Seeding state**: After initial setup or state file deletion, seed the state file with existing files before first run:
```python
import os, json
state = {}
for f in os.listdir(os.path.expanduser('~/urecorder/')):
    if f.endswith('.m4a'):
        state[f] = os.path.getmtime(os.path.join(os.path.expanduser('~/urecorder/'), f))
with open(os.path.expanduser('~/.hermes/cron_state/last_transcribed_files.json'), 'w') as fp:
    json.dump(state, fp)
```

**Timeout guard**: The script includes a 60s timeout on `os.listdir()` because `~/urecorder/` is on SSHFS which can hang. Without this, the cron job hits the 120s platform limit and fails.

## Pitfalls
- **{{LMS}} Whisper API does NOT work**: {{LMS}} loads `whisper-large-v3` but does NOT expose `/v1/audio/transcriptions` endpoint. Do NOT attempt to use {{LMS}}'s Whisper via HTTP API — it will fail with "Unsupported Media Type". Use local `openai-whisper` on VPS or GPU transcription instead.
- **VPS RAM limits**: The VPS has 7.8GB RAM. Models larger than `tiny` (small, medium) cause OOM kills. Do NOT attempt them — the process will be killed silently with exit code -1 and no output.
- **`--compute_type` is NOT a valid CLI flag**: This is a Python API parameter only. The Whisper CLI does not accept it.
- **`--fp16 False` increases memory usage**: Disabling fp16 uses float32 which doubles memory. Keep default (`True`) on CPU.
- **GPU transcription requires SSH access to Windows**: If the Windows machine is off or unreachable, fall back to VPS `tiny` model.
- **Windows SSH path handling**: PowerShell via SSH ACCEPTS forward slashes (`{{WINDOWS_TEMP}}/whisper_work`) — do NOT use backslashes in SSH commands, they cause "filename, directory name, or volume label syntax is incorrect" errors. Backslashes get mangled by the SSH shell layer.
- **Direct Whisper CLI fails on Windows via SSH**: `whisper <file> ...` invoked via SSH subprocess throws `FileNotFoundError`. Workaround: ship a Python helper script (`run_whisper.py`) that calls `whisper.load_model()` + `model.transcribe()` directly, avoiding CLI path parsing issues.
- **Missing ffmpeg on Windows = silent crash**: If ffmpeg isn't installed or isn't in PATH, Whisper's `transcribe()` throws `FileNotFoundError: [WinError 2]` — looks like a file issue but it's actually ffmpeg. Verify with `where ffmpeg` on Windows. Install via `winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements`. After install, restart the SSH session so PATH updates take effect.
- **SSH quoting on Windows**: Use single quotes around the entire PowerShell command. Inside, use `&&` (not `;`) to chain commands. Quote file paths with double quotes inside the command. Example: `ssh user@host 'cd C:/path && python script.py "C:/path/file.wav" "C:/path/out.json"'`
- **SSH keepalive required for long runs**: Add `-o ServerAliveInterval=30 -o ServerAliveCountMax=10` to all SSH/SCP commands. Without this, idle connections drop silently after ~5 min, causing transcription to fail with exit -1 and no error. Scripts `transcribe-single.py` and `batch-transcribe.py` include this via `SSH_OPTS` variable.
- **Filenames with parentheses break SCP**: Files like `URecorder_20260120_113908 (1).m4a` cause `/bin/sh: 1: Syntax error: "(" unexpected` because the remote SCP destination is not shell-quoted. Fix: wrap BOTH local and remote paths in `shlex.quote()` in all `scp` calls (upload and download). Without this, any file with `()` in the name silently fails and falls back to CPU. Applies to `transcribe-single.py` and `batch-transcribe.py`. Verify fix: `scp {shlex.quote(local)} {shlex.quote(remote)}`.
- **Batch scripts and background loops die silently (exit -1)**: `batch-transcribe.py` and shell `for` loops running multiple files in background consistently exit with code -1 — no error output, no partial progress. Cause: SSH session timeout or resource exhaustion over long runs (~5+ min). **Reliable approach**: run files in small foreground groups (≤5 files) via a terminal `for` loop, not in background. Example: `source ~/.hermes/venv/bin/activate && for f in ~/urecorder/file1.m4a ~/urecorder/file2.m4a; do python3 ~/.hermes/skills/audio-to-obsidian/scripts/transcribe-single.py "$f"; done` — this runs sequentially in foreground and each file's result is visible immediately. Do NOT use `background=true`, `nohup`, or plain `&` for multi-file transcription.
- **Foreground 5-file batches are reliable**: Groups of ≤5 files (~7-10 min) complete reliably as a single foreground command. Larger groups risk the silent -1 exit. When processing many remaining files, use repeated 5-file foreground loops.

## Notes
- VPS has no GPU — transcription is CPU-only (4 cores, AMD EPYC)
- GPU transcription on {{GPU_MODEL}} is dramatically faster and higher quality than any VPS model
- **Keep files under 30min for reasonable processing time**
- Reference: [GPU transcription setup details](references/gpu-transcription-setup.md)
- Reference: [GPU transcription troubleshooting](references/gpu-transcription-troubleshooting.md)
- Reference: [SCP filename quoting fix](references/scp-filename-quoting-fix.md)
- Whisper `{{WHISPER_MODEL}}` on GPU verified working as of May 2026
