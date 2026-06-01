---
name: obsidian-vault-management
description: Use when managing Obsidian vaults via file tools, web publishing endpoints, and sync workflows. Covers local file access, remote mounting, and custom script integration for note retrieval/editing.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [note-taking, obsidian, vaults, sync]
    related_skills: [hermes-agent-skill-authoring]
---

# Obsidian Vault Management

## Overview

This skill handles all interactions with Obsidian vaults when no native plugin exists. Uses standard file tools (`terminal`, `file`) and web access for published content.

## When to Use

- User provides Obsidian vault URL (127.0.0.1 or public)
- Request to read/write specific notes from vault
- Need to bridge Obsidian with external tools/APIs
- Vault sync or publishing configuration needed

## Core Workflows

### 1. SSHFS Mount (Primary — Vault on {{DESKTOP_HOST}}, Agent on VPS)
**When**: Vault lives on user's {{DESKTOP_HOST}} (`{{INFERENCE_HOST_IP}}`), agent runs on VPS. This is the recommended approach for cross-machine vault access.

**Prerequisites**:
- SSH server running on {{DESKTOP_HOST}} (Settings → Optional Features → OpenSSH Server)
- VPS public key added to Windows `authorized_keys`
- `/etc/fuse.conf` on VPS has `user_allow_other` uncommented
- `{{REMOTE_MOUNT_TOOL}}` installed on VPS (`apt install {{REMOTE_MOUNT_TOOL}}`)

**Steps**:
```bash
# 1. Add VPS public key to {{DESKTOP_HOST}} (run in PowerShell as Administrator)
$key = "ssh-ed25519 AAAA... (VPS pub key)"
Set-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value $key -Force
icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "USERNAME:(R,W)"

# 2. Mount vault on VPS
mkdir -p ~/.obsidian_vault
{{REMOTE_MOUNT_TOOL}} {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}:"{{WINDOWS_USER_DOCS}}/AI_Vault/Admin" ~/.obsidian_vault -o allow_other,reconnect,_netdev

# 3. Verify access
ls -la ~/.obsidian_vault/
```

**Mount script** (auto-reconnects after reboot): `scripts/mount-obsidian-vault.sh`

**Pitfalls**:
- ⚠️ Windows `authorized_keys` permissions: file created as admin but user can't read → must run `icacls` fix in admin PowerShell.
- ⚠️ `/etc/fuse.conf` must have `user_allow_other` uncommented, or `{{REMOTE_MOUNT_TOOL}} -o allow_other` fails.
- ⚠️ SSHFS path format: use forward slashes (`C:/Users/...`) and quote the path.
- ⚠️ No sudo on VPS → cannot add to `/etc/fstab`. Use mount script instead.
- ⚠️ Vault path on Windows: user's username is `123`, vault at `{{WINDOWS_USER_DOCS}}\AI_Vault\Admin`.

### 2. Local File Access (SSH Machine)
**When**: Vault lives directly on the VPS SSH host.

**Steps**:
```bash
# Read specific note
read_file path="~/.obsidian_vault/Note.md"

# Search across vault
search_files pattern="#tag" target="content" path="~/.obsidian_vault/"
```
**When**: Vault has "Publish" enabled (creates static site).

**Steps**:
```bash
# Fetch published note from web endpoint
web_search query="site:127.0.0.1:27124 NoteName"

# Or direct fetch if CORS allows
curl -s https://your-vault.vercel.app/NoteName.md
```

**Pitfalls**:
- ⚠️ `127.0.0.1` won't work remotely — need public IP or tunnel (SSH port forward, ngrok).
- ⚠️ CORS may block direct fetches; use proxy or publish to external host.

### 3. Cross-Vault Migration (Same Machine)
**When**: Moving files between two Obsidian vaults on the same {{DESKTOP_HOST}} (e.g., Admin vault → Ash vault).

**Steps**:
```powershell
# 1. Create target folders FIRST (Copy-Item fails if parent missing)
New-Item -ItemType Directory -Force -Path 'C:/Target/Vault/Subfolder'

# 2. Copy files
Copy-Item 'C:/Source/Vault/file.md' 'C:/Target/Vault/Subfolder/' -Force
```
Or from VPS (files already on VPS via SSHFS mount):
```bash
scp ~/.obsidian_vault/source/file.md {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}:"C:/Target/Vault/Subfolder/"
```

**Vault structure** (Admin vault — four folders only):
- `AI OS/` — System configs, maps, 8Bit Buddy docs, Ideas
- `Atlas/` — USER.md, IDENTITY.md, SOUL.md (user profile)
- `Calendar/` — Daily briefs + session summaries (cron writes here)
- `Efforts/` — Research, Templates, Transcripts, Diary, Reddit, Reference, Make Collective
- ⚠️ No new top-level folders. Map all content into these four.

**Pitfalls**:
- ⚠️ PowerShell `Copy-Item` fails if target parent folder doesn't exist — always `New-Item -ItemType Directory -Force` first
- ⚠️ SCP from VPS to Windows works for files already on VPS (SSHFS mount). For pure Windows-to-Windows, use PowerShell over SSH.
- ⚠️ Windows paths in SSH commands: use forward slashes and quote the full path string.
- ⚠️ Daily briefs + session summaries write to `~/.obsidian_vault/Calendar/` (not separate folders).
- ⚠️ Cron jobs run in fresh sessions — prompt must be self-contained.
- ⚠️ Obsidian mount must be active before cron runs (use mount script in crontab `@reboot`).
- ⚠️ Set `enabled_toolsets` to minimize token overhead.

### 4. Custom Sync Script
**When**: Need bidirectional sync between Obsidian and external storage.

**Template script** (`scripts/obsidian-sync.sh`):
```bash
#!/bin/bash
# Sync vault changes to remote folder via rsync
VAULT="$HOME/.obsidian/myvault"
REMOTE="user@server:/path/to/sync/folder"

rsync -avz --delete "$VAULT/" "$REMOTE/"
```

**Steps**:
1. Create script in `~/.hermes/scripts/`
2. Make executable: `chmod +x ~/.hermes/scripts/obsidian-sync.sh`
3. Schedule via cronjob or call from agent workflow

### 5. Automated Daily Briefs
**When**: User wants daily summaries delivered to messaging platforms with Obsidian backup.

**Steps**:
1. Create cron job with `session_search`, `todo`, `terminal`, `file` toolsets
2. Prompt should: review yesterday's sessions, check task status, generate to-do list, write to vault
3. Set `deliver` to target platform (e.g., `telegram:USER_ID` or `discord:CHANNEL`)
4. Schedule for morning (e.g., `0 8 * * *` for 8 AM CEST)

**Example prompt structure**:
```
1. Session Review: session_search for yesterday's conversations
2. Task Status: check todo list for completed/outstanding items
3. Format as markdown with sections: Highlights, Completed, Outstanding, Today's To-Do
4. Write to ~/.obsidian_vault/Daily Briefs/[YYYY-MM-DD].md
5. Output brief as final response
```

**Pitfalls**:
- ⚠️ Cron jobs run in fresh sessions — prompt must be self-contained
- ⚠️ Obsidian mount must be active before cron runs (use mount script in crontab `@reboot`)
- ⚠️ Set `enabled_toolsets` to minimize token overhead

---

## MCP Integration (Future)
**When**: Obsidian MCP server is configured.

**Steps**:
```yaml
# config.yaml
mcpServers:
  obsidian:
    command: npx
    args: [ "@davidgerard/obsidian-mcp" ]
    env:
      OBSIDIAN_VAULT_PATH: ~/.obsidian/myvault
```

Then use `native-mcp` skill to connect.

## References

- **SSHFS Setup Guide**: See `references/{{REMOTE_MOUNT_TOOL}}-setup.md` for cross-platform mount details
- **Mount Script**: See `scripts/mount-obsidian-vault.sh` for reusable auto-mount
- **Vault Location Discovery**: Probe with `ssh user@ip "powershell -Command \"Test-Path 'C:/Path'\""` on Windows

## Tools Used

- `read_file`: Direct note access
- `search_files`: Tag/file searches across vault
- `web_search`: Fetch published content
- `terminal`: Run sync scripts, probe paths
- `cronjob`: Schedule recurring syncs

## User Environment

- **{{DESKTOP_HOST}} (vault host):** `{{INFERENCE_HOST_IP}}` — also runs {{LMS}}
- **VPS (agent host):** `{{AGENT_HOST_IP}}` (user: {{USER}}, Ubuntu)
- **Vault path on Windows:** TBD — needs confirmation from user
- SSH server already running on {{DESKTOP_HOST}}
- Hermes `hermes mcp` CLI available on VPS for adding MCP servers

## Recommended Architecture

**MCP server on {{DESKTOP_HOST}} + SSH tunnel from VPS** — this is the preferred route for this user's setup. The MCP server handles vault I/O locally where the vault lives, SSH tunnel encrypts the connection, no file lock conflicts.

### SSH Tunnel Setup (VPS → {{DESKTOP_HOST}})
```bash
# From VPS, forward local port 3000 to {{DESKTOP_HOST}}'s MCP server
ssh -L {{TUNNEL_PORT}}:localhost:{{TUNNEL_PORT}} {{USER}}@{{INFERENCE_HOST_IP}} -N -f
```

### Register MCP Server with Hermes
```bash
# On VPS, after tunnel is up:
hermes mcp add obsidian --url http://localhost:3000
```

### {{DESKTOP_HOST}}: Install MCP Server
```powershell
# In PowerShell on {{DESKTOP_HOST}}:
npm install -g @davidgerard/obsidian-mcp
# Or use the Python variant:
pip install obsidian-mcp-server
# Point OBSIDIAN_VAULT_PATH env var at your vault directory
```

### Alternative: SSHFS Mount (if MCP proves problematic)
```bash
# On VPS:
{{REMOTE_MOUNT_TOOL}} {{USER}}@{{INFERENCE_HOST_IP}}:/path/to/vault /mnt/obsidian
# Then use read_file/search_files directly on /mnt/obsidian/
```

## Verification Checklist

- [ ] Vault path confirmed via `ls ~/.obsidian/` before accessing files
- [ ] SSH key (`id_rsa`) available for backend connection
- [ ] Published vault accessible from external network if using web endpoint
- [ ] Sync scripts tested with dry-run flag first (`--dry-run`)