#!/usr/bin/env python3
"""Transcribe a single audio file - defaults to GPU ({{GPU_MODEL}}) for best quality, falls back to local CPU."""

import sys
import os
import subprocess
import json
import re
import shlex
from datetime import datetime

VAULT_PATH = os.path.expanduser("~/.obsidian_vault/Efforts/Transcript")
REMOTE_USER = "123"
REMOTE_HOST = "{{INFERENCE_HOST_IP}}"
REMOTE_DIR = "{{WINDOWS_TEMP}}/whisper_work"
GPU_MODEL = "{{WHISPER_MODEL}}"
CPU_MODEL = "tiny"  # {{AGENT_HOST}} only has 7.8GB RAM

def run(cmd, check=True):
    """Run a shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
    out = result.stdout + result.stderr
    if check and result.returncode != 0:
        print(f"Command failed (exit {result.returncode}): {cmd}")
        print(out[-500:] if len(out) > 500 else out)
        sys.exit(1)
    return result.stdout, result.stderr

SSH_OPTS = "-o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o ConnectTimeout=10"

def transcribe_on_gpu(audio_path):
    """Transfer to Windows {{GPU_MODEL}}, run whisper, transfer result back."""
    base = os.path.splitext(os.path.basename(audio_path))[0]
    tmp_dir = "/tmp/whisper_gpu"
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(VAULT_PATH, exist_ok=True)
    
    # Upload audio
    print(f"  ↗ Uploading to {REMOTE_HOST}...")
    remote_dest = shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.m4a")
    run(f'scp {SSH_OPTS} {shlex.quote(audio_path)} {remote_dest}')
    
    # Upload run script
    run(f'scp {SSH_OPTS} ~/.hermes/skills/audio-to-obsidian/scripts/run_whisper.py {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/run_whisper.py')
    
    # Run whisper on GPU - use forward slashes (PowerShell handles them fine)
    print(f"  ⚡ Transcribing on {{GPU_MODEL}} (model: {GPU_MODEL})...")
    remote_file = f"{REMOTE_DIR}/{base}.m4a"
    remote_out = f"{REMOTE_DIR}/{base}.json"
    cmd = (
        f'ssh {SSH_OPTS} {REMOTE_USER}@{REMOTE_HOST} '
        f'\'cd {REMOTE_DIR} && python run_whisper.py {GPU_MODEL} "{remote_file}" "{remote_out}"\''
    )
    run(cmd)
    
    # Download JSON
    print(f"  ↙ Downloading result...")
    run(f'scp {SSH_OPTS} {shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.json")} {shlex.quote(f"{tmp_dir}/{base}.json")}')
    
    # Clean remote
    run(f'ssh {SSH_OPTS} {REMOTE_USER}@{REMOTE_HOST} "del /q {remote_file} {remote_out} 2>nul"', check=False)
    
    # Load result
    json_path = os.path.join(tmp_dir, f"{base}.json")
    with open(json_path, 'r') as f:
        data = json.load(f)
    os.remove(json_path)
    return data

def transcribe_local(audio_path, output_dir):
    """Fallback: run whisper locally on CPU (slower, lower quality)."""
    cmd = [
        "whisper", audio_path,
        "--model", CPU_MODEL,
        "--device", "cpu",
        "--language", "en",
        "--output_format", "json",
        "--output_dir", output_dir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"Whisper error: {result.stderr}")
        sys.exit(1)
    
    json_file = os.path.join(output_dir, os.path.splitext(os.path.basename(audio_path))[0] + ".json")
    with open(json_file, 'r') as f:
        data = json.load(f)
    os.remove(json_file)
    return data

def extract_action_items(text):
    """Extract potential action items from transcript."""
    patterns = [
        r"(?:need to|should|must|will|going to|let's|I'll|we'll)[:\s]+(.{10,80})",
        r"(?:follow up|check|review|fix|update|create|build|deploy|test)[:\s]+(.{10,80})"
    ]
    items = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        items.extend([m.strip().rstrip('.') for m in matches])
    return list(dict.fromkeys(items))[:10]

def create_obsidian_note(data, audio_path, model_used):
    """Create an Obsidian-compatible markdown note."""
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
    if len(sys.argv) < 2:
        print("Usage: transcribe-single.py <audio_file>")
        sys.exit(1)
    
    audio_path = os.path.expanduser(sys.argv[1])
    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        sys.exit(1)
    
    os.makedirs(VAULT_PATH, exist_ok=True)
    print(f"Transcribing: {os.path.basename(audio_path)}")
    
    # Try GPU first, fallback to CPU
    model_used = GPU_MODEL
    try:
        print(f"Attempting GPU transcription ({GPU_MODEL} on {{GPU_MODEL}})...")
        data = transcribe_on_gpu(audio_path)
    except Exception as e:
        print(f"GPU failed ({e}), falling back to local CPU ({CPU_MODEL})...")
        model_used = CPU_MODEL
        data = transcribe_local(audio_path, VAULT_PATH)
    
    note_content = create_obsidian_note(data, audio_path, model_used)
    
    note_path = os.path.join(VAULT_PATH, f"{os.path.splitext(os.path.basename(audio_path))[0]}.md")
    with open(note_path, 'w') as f:
        f.write(note_content)
    
    print(f"Note saved: {note_path} (model: {model_used})")

if __name__ == "__main__":
    main()
