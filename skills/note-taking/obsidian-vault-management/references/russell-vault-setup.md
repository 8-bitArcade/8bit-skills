# {{USER}}'s Obsidian Vault Setup

## Configuration
- **Vault location**: `{{WINDOWS_USER_DOCS}}\AI_Vault\Admin` ({{DESKTOP_HOST}})
- **Remote host**: `{{INFERENCE_HOST_IP}}` ({{DESKTOP_HOST}}, same as {{LMS}})
- **Remote user**: `123`
- **Mount point on {{AGENT_HOST}}**: `~/.obsidian_vault`
- **SSH key**: `~/.ssh/id_ed25519` ({{AGENT_HOST}}) → added to Windows `~/.ssh/authorized_keys`

## Setup Steps Completed
1. Added {{AGENT_HOST}} public key to {{DESKTOP_HOST}} `authorized_keys` (ran as admin)
2. Verified SSH connectivity: `ssh {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}} "whoami"` → `gaming-ai-3090r\123`
3. Enabled `user_allow_other` in `/etc/fuse.conf` on {{AGENT_HOST}}
4. Mounted vault: `{{REMOTE_MOUNT_TOOL}} {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}:"{{WINDOWS_USER_DOCS}}/AI_Vault/Admin" ~/.obsidian_vault -o allow_other,reconnect`
5. Verified read/write: created and deleted test note

## Known Vault Contents (as of 2026-05-27)
```
.obsidian/
8Bit Buddy_IDENTITY.pdf
AI OS/
Atlas/
Calendar/
Efforts/
Gamified Roadmap Proposal Summary.pdf
me.md
skills-map.md
vault-map.md
```

## Troubleshooting Notes
- Windows OpenSSH server must be enabled (Settings → Optional Features)
- PowerShell commands for Windows SSH setup:
  ```powershell
  # Add key as admin
  Set-Content -Path "$env:USERPROFILE\.ssh\authorized_keys" -Value "ssh-ed25519 AAAA..." -Force
  icacls "$env:USERPROFILE\.ssh\authorized_keys" /grant "username:(R,W)"
  ```
- If mount fails after reboot, run: `bash ~/.hermes/scripts/mount-obsidian-vault.sh`
