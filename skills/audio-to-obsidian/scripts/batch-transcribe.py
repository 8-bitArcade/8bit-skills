#!/usr/bin/env python3
"""Batch transcribe all URecorder audio files to Obsidian notes.
Defaults to GPU (RTX 3090) for best quality, falls back to local CPU."""

import os
import sys
import json
import glob
import subprocess
import re
import shlex
from datetime import datetime

URECORDER_DIR = os.path.expanduser("~/urecorder")
VAULT_DIR = os.path.expanduser("~/.obsidian_vault/Efforts/Transcript")
REMOTE_USER = "123"
REMOTE_HOST = "100.110.93.103"
REMOTE_DIR = "C:/Temp/whisper_work"
GPU_MODEL = "large-v3-turbo"
CPU_MODEL = "tiny"  # VPS only has 7.8GB RAM
TEMP_DIR = "/tmp/whisper_gpu"

def run(cmd, check=True):
    """Run a shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    out = result.stdout + result.stderr
    if check and result.returncode != 0:
        return None, f"Command failed: {cmd}\n{out[-300:]}"
    return result, None

SSH_OPTS = "-o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o ConnectTimeout=10"

def transcribe_on_gpu(audio_path):
    """Transfer to Windows RTX 3090, run whisper, transfer result back."""
    base = os.path.splitext(os.path.basename(audio_path))[0]
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Upload audio
    print(f"    ↗ Uploading...")
    res, err = run(f'scp {SSH_OPTS} {shlex.quote(audio_path)} {shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.m4a")}')
    if err:
        return None, f"Upload failed: {err}"
    
    # Upload run script
    print(f"    ↗ Uploading script...")
    res, err = run(f'scp {SSH_OPTS} ~/.hermes/skills/audio-to-obsidian/scripts/run_whisper.py {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/run_whisper.py')
    if err:
        return None, f"Script upload failed: {err}"
    
    # Run whisper on GPU - use forward slashes (PowerShell handles them fine)
    print(f"    ⚡ Transcribing on GPU...")
    remote_file = f"{REMOTE_DIR}/{base}.m4a"
    remote_out = f"{REMOTE_DIR}/{base}.json"
    cmd = (
        f'ssh {SSH_OPTS} {REMOTE_USER}@{REMOTE_HOST} '
        f'\'cd {REMOTE_DIR} && python run_whisper.py {GPU_MODEL} "{remote_file}" "{remote_out}"\''
    )
    res, err = run(cmd)
    if err:
        return None, f"GPU transcription failed: {err}"
    
    # Download JSON
    print(f"    ↙ Downloading result...")
    res, err = run(f'scp {SSH_OPTS} {shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.json")} {shlex.quote(f"{TEMP_DIR}/{base}.json")}')
    if err:
        return None, f"Download failed: {err}"
    
    # Clean remote
    run(f'ssh {SSH_OPTS} {REMOTE_USER}@{REMOTE_HOST} "del /q {remote_file} {remote_out} 2>nul"', check=False)
    
    # Load result
    json_path = os.path.join(TEMP_DIR, f"{base}.json")
    with open(json_path, 'r') as f:
        data = json.load(f)
    os.remove(json_path)
    return data, None

def transcribe_local(audio_path):
    """Fallback: run whisper locally on CPU (slower, lower quality)."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(audio_path))[0]
    json_out = os.path.join(TEMP_DIR, f"{base}.json")
    cmd = ["whisper", audio_path, "--model", CPU_MODEL, "--device", "cpu",
           "--language", "en", "--output_format", "json", "--output_dir", TEMP_DIR]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        return None, f"Whisper error: {result.stderr}"
    if not os.path.exists(json_out):
        return None, f"Output JSON not found: {json_out}"
    with open(json_out, 'r') as f:
        data = json.load(f)
    os.remove(json_out)
    return data, None

def transcribe(audio_path):
    """Try GPU first, fallback to CPU."""
    data, err = transcribe_on_gpu(audio_path)
    if err:
        print(f"  GPU failed ({err}), falling back to local CPU ({CPU_MODEL})...")
        return transcribe_local(audio_path)
    return data, None

def extract_action_items(text):
    patterns = [
        r"(?:need to|should|must|will|going to|let's|I'll|we'll)[:\s]+(.{10,80})",
        r"(?:follow up|check|review|fix|update|create|build|deploy|test)[:\s]+(.{10,80})"
    ]
    items = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        items.extend([m.strip().rstrip('.') for m in matches])
    return list(dict.fromkeys(items))[:10]

def create_note(data, audio_path, model_used):
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    segments = data.get("segments", [])
    full_text = " ".join([s.get("text", "").strip() for s in segments])
    sentences = re.split(r'(?<=[.!?])\s+', full_text.replace('\n', ' '))
    summary = " ".join(s.strip() for s in sentences[:5] if s.strip())
    if not summary:
        summary = full_text[:500]
    key_points = [s.strip() for s in sentences[5:15] if len(s.strip()) > 20]
    action_items = extract_action_items(full_text)
    note = f"""---
date: {timestamp}
source: {os.path.basename(audio_path)}
type: transcript
model: {model_used}
tags: [transcript, audio]
---

# {filename}

## Summary
{summary}

## Key Points
"""
    for point in key_points[:10]:
        note += f"- {point}\n"
    if not key_points:
        note += "- No distinct key points identified\n"
    note += "\n## Action Items\n"
    for item in action_items:
        note += f"- [ ] {item}\n"
    if not action_items:
        note += "- [ ] No action items detected\n"
    note += "\n## Full Transcript\n"
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "").strip()
        if text:
            mins = int(start // 60)
            secs = int(start % 60)
            note += f"**{mins:02d}:{secs:02d}** {text}\n"
    return note

def main():
    print("Starting batch transcription...")
    os.makedirs(VAULT_DIR, exist_ok=True)
    all_files = sorted(glob.glob(os.path.join(URECORDER_DIR, "URecorder_*.m4a")))
    print(f"Found {len(all_files)} audio files")
    done = set()
    if os.path.exists(VAULT_DIR):
        notes = glob.glob(os.path.join(VAULT_DIR, "URecorder_*.md"))
        done = {os.path.splitext(os.path.basename(n))[0] for n in notes}
    to_process = [f for f in all_files if os.path.splitext(os.path.basename(f))[0] not in done]
    total = len(all_files)
    skipped = len(done)
    pending = len(to_process)
    print(f"📁 Total: {total} | ✅ Done: {skipped} | ⏳ Pending: {pending}")
    print("=" * 60)
    for i, audio_path in enumerate(to_process, 1):
        base = os.path.basename(audio_path)
        print(f"\n[{i}/{pending}] Transcribing: {base}")
        print(f"  Attempting GPU ({GPU_MODEL} on RTX 3090)...")
        data, err = transcribe(audio_path)
        if err:
            print(f"  ❌ Error: {err}")
            continue
        # Determine model used from data (or default to GPU)
        model_used = GPU_MODEL
        note = create_note(data, audio_path, model_used)
        note_path = os.path.join(VAULT_DIR, f"{os.path.splitext(base)[0]}.md")
        with open(note_path, 'w') as f:
            f.write(note)
        print(f"  ✅ Saved: {os.path.basename(note_path)} (model: {model_used})")
    print("\n" + "=" * 60)
    print(f"🎉 Batch complete! {pending} files transcribed.")

if __name__ == "__main__":
    main()
