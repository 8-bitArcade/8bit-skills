#!/usr/bin/env python3
"""Post-process transcripts with LLM to improve accuracy and clarity."""

import os
import glob
import requests
import sys
import time

LM_STUDIO_URL = "http://100.110.93.103:1235/v1/chat/completions"
MODEL = "qwen3.5-9b"
VAULT_DIR = os.path.expanduser("~/.obsidian_vault/Efforts/Transcript")

def post_process(transcript_text, filename):
    """Send transcript to LLM for correction."""
    try:
        response = requests.post(LM_STUDIO_URL, json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": (
                    "You are an expert editor correcting audio transcription errors. "
                    "Fix: misheard words, grammar errors, punctuation, capitalization, "
                    "and formatting issues. Preserve original meaning, tone, and structure. "
                    "Return ONLY the corrected text - no explanations, no markdown wrapping."
                )},
                {"role": "user", "content": transcript_text}
            ],
            "temperature": 0.3
        }, timeout=300)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"  ⚠ API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"  ⚠ Error: {e}")
        return None

def main():
    files = sorted(glob.glob(os.path.join(VAULT_DIR, "URecorder_*.md")))
    files = [f for f in files if not f.endswith('.backup.md')]
    if not files:
        print("No transcripts found")
        return
    
    # If specific file passed as argument, only process that one
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
        files = [f for f in files if any(t in f for t in targets)]
        if not files:
            print(f"Files not found: {targets}")
            return
    
    print(f"Found {len(files)} transcripts to post-process")
    print("=" * 60)
    
    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        print(f"\n[{i}/{len(files)}] {filename}")
        
        with open(filepath, 'r') as f:
            original = f.read()
        
        print(f"  🔄 Sending to LLM ({MODEL})...")
        improved = post_process(original, filename)
        
        if improved:
            # Save backup of original
            backup_path = filepath.replace('.md', '.backup.md')
            with open(backup_path, 'w') as f:
                f.write(original)
            
            # Save improved version
            with open(filepath, 'w') as f:
                f.write(improved)
            
            print(f"  ✅ Improved (backup saved)")
        else:
            print(f"  ❌ Failed - keeping original")
        
        # Small delay to avoid overwhelming the API
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"Done! Processed {len(files)} transcripts")

if __name__ == "__main__":
    main()