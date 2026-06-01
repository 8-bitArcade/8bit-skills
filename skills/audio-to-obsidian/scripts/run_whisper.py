#!/usr/bin/env python3
"""Run Whisper transcription with GPU on Windows machine.
Ship this to {{WINDOWS_TEMP}}/whisper_work/ via SCP, then invoke via SSH:
  ssh user@host 'cd {{WINDOWS_TEMP}}/whisper_work && python run_whisper.py {{WHISPER_MODEL}} "{{WINDOWS_TEMP}}/whisper_work/input.m4a" "{{WINDOWS_TEMP}}/whisper_work/output.json"'
"""
import whisper
import json
import sys

model_name = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]

print(f"Loading model: {model_name}")
model = whisper.load_model(model_name)

print(f"Transcribing: {input_file}")
result = model.transcribe(input_file, language="en")

with open(output_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"Done. Output: {output_file}")
