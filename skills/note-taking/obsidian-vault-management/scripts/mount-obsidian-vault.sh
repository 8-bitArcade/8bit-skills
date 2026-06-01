#!/bin/bash
# Mount Obsidian vault from {{DESKTOP_HOST}} via SSHFS
# Usage: bash mount-obsidian-vault.sh

MOUNT_POINT="$HOME/.obsidian_vault"
VAULT_PATH="{{WINDOWS_USER_DOCS}}/AI_Vault/Admin"
REMOTE_USER="123"
REMOTE_HOST="{{INFERENCE_HOST_IP}}"

mkdir -p "$MOUNT_POINT"

# Check if already mounted
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "Vault already mounted at $MOUNT_POINT"
    exit 0
fi

# Mount the vault
{{REMOTE_MOUNT_TOOL}} "${REMOTE_USER}@${REMOTE_HOST}":"$VAULT_PATH" "$MOUNT_POINT" \
    -o allow_other,reconnect,_netdev

if [ $? -eq 0 ]; then
    echo "Obsidian vault mounted successfully at $MOUNT_POINT"
else
    echo "Failed to mount Obsidian vault"
    exit 1
fi
