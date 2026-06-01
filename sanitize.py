#!/usr/bin/env python3
"""
sanitize.py — Strip private/instance-specific data from skill files.
Copies from source skills dir to repo, sanitizing as it goes.

Usage: python3 sanitize.py <source_skills_dir> <dest_skills_dir>

Called by sync-skills-repo.sh after initial copy, before commit.
"""

import os
import re
import sys
import shutil

SKIP_EXT = {'.pyc', '.pyo', '.so', '.dll', '.png', '.jpg', '.gif', '.mp3', '.m4a'}
SKIP_DIR = {'__pycache__', '.git', 'node_modules'}

# (pattern, replacement) — order matters: specific before general
RULES = [
    # Full paths (most specific first)
    (r'/home/russell/\.hermes/\.env', '{{ENV_PATH}}'),
    (r'/home/russell/\.hermes/config\.yaml', '{{CONFIG_PATH}}'),
    (r'/home/russell/\.hermes/skills/', '{{HERMES_SKILLS_DIR}}/'),
    (r'/home/russell/\.hermes/', '{{HERMES_HOME}}/'),
    (r'/home/russell/\.obsidian_vault', '{{VAULT_MOUNT}}'),
    (r'/home/russell/\.hermes/data/', '{{HERMES_DATA}}/'),
    (r'/home/russell/8Bit-Data_Room', '{{PROJECT_DIR}}'),
    (r'/home/russell/hermes-config-backup', '{{CONFIG_BACKUP_DIR}}'),
    (r'/home/russell/urecorder', '{{RECORDINGS_MOUNT}}'),
    (r'/home/russell/8Bit-Skills-Library', '{{SKILLS_LIBRARY_DIR}}'),

    # SSH connection strings with usernames
    (r'ssh 123@100\.110\.93\.103', 'ssh {{WINDOWS_USER}}@{{WORKSTATION_IP}}'),
    (r'ssh -L 3000:localhost:3000 russell@100\.110\.93\.103', 'ssh -L {{PORT}}:localhost:{{PORT}} {{USER}}@{{WORKSTATION_IP}}'),
    (r'123@100\.110\.93\.103', '{{WINDOWS_USER}}@{{WORKSTATION_IP}}'),
    (r'russell@100\.110\.93\.103', '{{USER}}@{{WORKSTATION_IP}}'),
    (r'russell@100\.110\.135\.127', '{{USER}}@{{VPS_IP}}'),

    # IPs
    (r'100\.110\.135\.127', '{{VPS_IP}}'),
    (r'100\.110\.93\.103:1235', '{{LMS_HOST}}'),
    (r'100\.110\.93\.103', '{{WORKSTATION_IP}}'),

    # Windows paths
    (r'C:\\Users\\123\\Documents', '{{WINDOWS_DOCS}}'),
    (r'C:/Users/123/Documents', '{{WINDOWS_DOCS}}'),
    (r'C:\\Users\\123', '{{WINDOWS_HOME}}'),
    (r'C:/Users/123', '{{WINDOWS_HOME}}'),
    (r'C:\\Temp', '{{WINDOWS_TEMP}}'),
    (r'C:/Temp', '{{WINDOWS_TEMP}}'),

    # GPU / hardware
    (r'RTX 3090', '{{GPU_MODEL}}'),
    (r'NVIDIA GeForce RTX 3090', '{{GPU_MODEL}}'),
    (r'large-v3-turbo', '{{WHISPER_MODEL}}'),
    (r'tiny-en', '{{WHISPER_FALLBACK}}'),

    # Model refs (only when tied to local infra)
    (r'qwen/qwen3\.6-27b', '{{MODEL_LARGE}}'),
    (r'qwen3\.5-9b', '{{MODEL_DEFAULT}}'),
    (r'nemotron-nano-4b', '{{MODEL_FAST}}'),
    (r'LM Studio\b', '{{LMS}}'),
    (r'LM_Studio', '{{LMS}}'),

    # Infra / tools
    (r'Tailscale\b', '{{VPN_TOOL}}'),
    (r'tailscale\b', '{{VPN_CMD}}'),
    (r'Nubia Z70 Ultra', '{{MOBILE_DEVICE}}'),
    (r'SD 8 Elite', '{{MOBILE_SOC}}'),

    # Project / personal names
    (r'\bNanoClaw\b', '{{ASSISTANT_NAME}}'),
    (r'\bOpenClaw\b', '{{FRAMEWORK_NAME}}'),
    (r'8Bit-Arcade', '{{GITHUB_ORG}}'),
    (r'Russell-Bryant', '{{GITHUB_USER}}'),
    (r'8bit\.io\b', '{{DOMAIN}}'),
    (r'8Bit\.io', '{{DOMAIN}}'),
    (r'@8bit_arcade1', '{{IG_HANDLE}}'),

    # Cron IDs
    (r'\b3e98de640cdb\b', '{{CRON_ID_1}}'),
    (r'\be4e7e408dad7\b', '{{CRON_ID_2}}'),
    (r'\b840d4c8c8365\b', '{{CRON_ID_3}}'),
    (r'\bf6cdc8ee995c\b', '{{CRON_ID_4}}'),
    (r'\bf8c7b071db07\b', '{{CRON_ID_5}}'),

    # Env var names containing secrets (keep generic)
    (r'OPENROUTER_API_KEY', '{{OR_API_KEY_VAR}}'),
    (r'META_LONG_LIVED_TOKEN', '{{META_TOKEN_VAR}}'),
    (r'TWITTER_API_KEY\b', '{{TW_API_KEY_VAR}}'),
    (r'TWITTER_API_SECRET', '{{TW_API_SECRET_VAR}}'),
    (r'TWITTER_ACCESS_TOKEN\b', '{{TW_ACCESS_TOKEN_VAR}}'),
    (r'TWITTER_ACCESS_TOKEN_SECRET', '{{TW_ACCESS_SECRET_VAR}}'),
    (r'XAI_API_KEY', '{{XAI_KEY_VAR}}'),
    (r'AUTHORIZED_EMAILS', '{{AUTH_EMAILS_VAR}}'),

    # Email
    (r'russell@8bit\.io', '{{ADMIN_EMAIL}}'),
    (r'russell@8bit\.io', '{{ADMIN_EMAIL}}'),

    # App / project references in env context
    (r'996540993337274', '{{META_APP_ID}}'),

    # Client/domain in WebAuthn config
    (r"expectedOrigin: 'http://localhost:3000'", "expectedOrigin: 'http://localhost:{{BACKEND_PORT}}'"),
    (r"rpID: 'localhost'", "rpID: '{{DOMAIN}}'"),
    (r"port: process\.env\.PORT \|\| 3001", "port: process.env.PORT || {{BACKEND_PORT}}"),
]


def sanitize(content):
    for pattern, repl in RULES:
        content = re.sub(pattern, repl, content)
    return content


def process(src_base, dst_base):
    changed = 0
    copied = 0
    skipped = 0

    # Clear destination and re-copy fresh
    if os.path.exists(dst_base):
        shutil.rmtree(dst_base)

    for root, dirs, files in os.walk(src_base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR]

        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in SKIP_EXT:
                skipped += 1
                continue

            src_path = os.path.join(root, fname)
            rel = os.path.relpath(src_path, src_base)
            dst_path = os.path.join(dst_base, rel)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

            try:
                with open(src_path, 'r', encoding='utf-8', errors='strict') as f:
                    content = f.read()
            except (UnicodeDecodeError, IOError):
                # Binary file — copy raw
                shutil.copy2(src_path, dst_path)
                skipped += 1
                continue

            sanitized = sanitize(content)
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(sanitized)

            if sanitized != content:
                changed += 1
            copied += 1

    return copied, changed, skipped


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <src_skills_dir> <dst_skills_dir>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]
    copied, changed, skipped = process(src, dst)
    print(f"Sanitized: {copied} files copied, {changed} sanitized, {skipped} skipped/binary")
