# SSHFS Vault Access Setup Guide

## Prerequisites Checklist
- [ ] SSH server running on remote machine
- [ ] Key-based auth configured (VPS public key in remote's `authorized_keys`)
- [ ] `{{REMOTE_MOUNT_TOOL}}` installed on agent host ({{AGENT_HOST}})
- [ ] `/etc/fuse.conf` has `user_allow_other` uncommented

## Windows-Specific Notes
- Windows 10/11 has OpenSSH Server built-in (Settings → Optional Features)
- PowerShell path: `C:\Users\<username>\.ssh\authorized_keys`
- Use forward slashes in SSHFS paths: `C:/Path/To/Vault`
- Test connectivity: `ssh user@ip "powershell -Command \"Test-Path 'C:/Path'\""`

## Common Issues
1. **"option allow_other only allowed"** → uncomment `user_allow_other` in `/etc/fuse.conf`
2. **"No such file or directory"** → verify path format (forward slashes on Windows)
3. **"Permission denied"** → check SSH key is in remote's `authorized_keys`
4. **Mount fails silently** → check SSH connectivity first with `ssh user@ip "whoami"`

## {{USER}}'s Setup (Specific)
- Remote: {{DESKTOP_HOST}} at `{{INFERENCE_HOST_IP}}`
- User: `123`
- Vault: `{{WINDOWS_USER_DOCS}}/AI_Vault/Admin`
- Mount: `~/.obsidian_vault/`
- Mount script: `scripts/mount-obsidian-vault.sh`
