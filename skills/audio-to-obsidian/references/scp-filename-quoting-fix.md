# SCP Filename Quoting Fix

## Problem
Filenames containing parentheses (e.g. `URecorder_20260120_113908 (1).m4a`) break SCP commands because the shell interprets `(` as a subshell opening:

```
/bin/sh: 1: Syntax error: "(" unexpected
```

This affects both upload and download SCP calls in `transcribe-single.py` and `batch-transcribe.py`.

## Root Cause
The local path was quoted with `shlex.quote()` but the bare remote destination (`user@host:path/file (1).m4a`) was interpolated into the shell command string unquoted. The `(` in the filename was then interpreted by `/bin/sh`.

## Fix
Wrap **both** source and destination arguments in `shlex.quote()`:

```python
import shlex

# Upload
local = shlex.quote(audio_path)
remote_dest = shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.m4a")
run(f'scp {SSH_OPTS} {local} {remote_dest}')

# Download
remote_src = shlex.quote(f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{base}.json")
local_dest = shlex.quote(f"{TEMP_DIR}/{base}.json")
run(f'scp {SSH_OPTS} {remote_src} {local_dest}')
```

## Files Fixed
- `scripts/transcribe-single.py` — upload and download SCP calls
- `scripts/batch-transcribe.py` — upload and download SCP calls

## Correctness Test
```bash
# Before fix (would fail):
scp '/path/file (1).m4a' user@host:C:/path/file (1).m4a

# After fix (works):
scp '/path/file (1).m4a' 'user@host:C:/path/file (1).m4a'
```
