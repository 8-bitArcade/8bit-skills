# GDrive Access Issues

**Status:** Resolved via SSHFS workaround

## rclone Configuration
Two remotes configured:
- `drive:` — Full scope, token expired 2026-03-25
- `gdrive:` — `scope = drive.file` (limited to app-created files only)

## Problem
- `gdrive:` only sees files created by that rclone app instance
- Cannot access user's existing GDrive folders (e.g., URecorder)
- Re-auth with full scope requires browser authorization flow

## Working Solution: SSHFS Mount
Mount Windows GDrive sync folder directly via SSHFS:
```bash
sshfs 123@100.110.93.103:"G:/My Drive/URecorder" ~/urecorder -o allow_other,reconnect,_netdev
```

## Mount Details
- Windows path: `G:\My Drive\URecorder`
- Mount point: `~/urecorder/`
- Contains: `.m4a` audio files from URecorder app
- Files appear as duplicates (original + `(1)` copy) — skip `(1)` files

## Future Fix (Optional)
To fix rclone GDrive access:
1. Run `rclone authorize "drive" "drive"` on local machine
2. Paste token into `~/.config/rclone/rclone.conf`
3. Remove `scope = drive.file` line for full access
