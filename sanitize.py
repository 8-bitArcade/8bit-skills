#!/usr/bin/env python3
"""
sanitize.py — Strip private/instance-specific data from skill files.

Produces platform-agnostic templates that work whether the user runs on:
  - A VPS + workstation setup (like the original author)
  - A single local machine
  - A cloud VM
  - A hybrid/multi-device setup

All {{VARIABLE}} templates are documented in README.md.

Usage: python3 sanitize.py <source_skills_dir> <dest_skills_dir>
Called by sync-skills-repo.sh between staging and commit.
"""

import os
import re
import sys
import shutil

SKIP_EXT = {'.pyc', '.pyo', '.so', '.dll', '.png', '.jpg', '.gif', '.mp3', '.m4a', '.ico'}
SKIP_DIR = {'__pycache__', '.git', 'node_modules'}

# ──────────────────────────────────────────────────────────────────────
# SANITIZATION RULES — ordered: most specific / longest match first
# ──────────────────────────────────────────────────────────────────────
# Philosophy: replace with SEMANTIC templates, not just anonymized values.
# "VPS" → {{AGENT_HOST}} not {{VPS}} (works for "runs on my laptop" too)
# "workstation" → {{INFERENCE_HOST}} not {{WORKSTATION}} (GPU could be local)
# ──────────────────────────────────────────────────────────────────────
RULES = [
    # ── Full file paths (most specific first, before partial matches) ──
    (r'/home/russell/\.hermes/\.env', '{{HERMES_ENV_PATH}}'),
    (r'/home/russell/\.hermes/config\.yaml', '{{HERMES_CONFIG_PATH}}'),
    (r'/home/russell/\.hermes/skills/', '{{HERMES_SKILLS_DIR}}/'),
    (r'/home/russell/\.hermes/data/', '{{HERMES_DATA_DIR}}/'),
    (r'/home/russell/\.hermes/scripts/', '{{HERMES_SCRIPTS_DIR}}/'),
    (r'/home/russell/\.hermes/', '{{HERMES_HOME}}/'),
    (r'/home/russell/\.obsidian_vault', '{{VAULT_PATH}}'),
    (r'/home/russell/8Bit-Data_Room', '{{PROJECT_ROOT}}'),
    (r'/home/russell/hermes-config-backup', '{{CONFIG_BACKUP_REPO}}'),
    (r'/home/russell/urecorder', '{{RECORDINGS_PATH}}'),
    (r'/home/russell/8Bit-Skills-Library', '{{SKILLS_LIBRARY_REPO}}'),
    (r'/home/russell/\.hermes/session_summaries', '{{SESSION_SUMMARIES_DIR}}'),

    # ── Windows-specific paths ──
    (r'C:\\Users\\123\\Documents', '{{WINDOWS_USER_DOCS}}'),
    (r'C:/Users/123/Documents', '{{WINDOWS_USER_DOCS}}'),
    (r'C:\\Users\\123', '{{WINDOWS_USER_HOME}}'),
    (r'C:/Users/123', '{{WINDOWS_USER_HOME}}'),
    (r'C:\\Temp', '{{WINDOWS_TEMP}}'),
    (r'C:/Temp', '{{WINDOWS_TEMP}}'),

    # ── SSH connection strings (before bare IPs) ──
    (r'ssh 123@100\.110\.93\.103',
     'ssh {{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}'),
    (r'ssh -L 3000:localhost:3000 russell@100\.110\.93\.103',
     'ssh -L {{TUNNEL_PORT}}:localhost:{{TUNNEL_PORT}} {{USER}}@{{INFERENCE_HOST_IP}}'),
    (r'123@100\.110\.93\.103',
     '{{WINDOWS_USER}}@{{INFERENCE_HOST_IP}}'),
    (r'russell@100\.110\.93\.103',
     '{{USER}}@{{INFERENCE_HOST_IP}}'),
    (r'russell@100\.110\.135\.127',
     '{{USER}}@{{AGENT_HOST_IP}}'),

    # ── IP addresses (bare, after SSH strings handled) ──
    (r'\b100\.110\.135\.127\b', '{{AGENT_HOST_IP}}'),
    (r'100\.110\.93\.103:1235', '{{LMS_HOST}}'),
    (r'\b100\.110\.93\.103\b', '{{INFERENCE_HOST_IP}}'),

    # ── Hardware / GPU ──
    (r'RTX 3090', '{{GPU_MODEL}}'),
    (r'NVIDIA GeForce RTX 3090', '{{GPU_MODEL}}'),
    (r'large-v3-turbo', '{{WHISPER_MODEL}}'),
    (r'\btiny-en\b', '{{WHISPER_MODEL_SMALL}}'),

    # ── LLM model identifiers ──
    (r'qwen/qwen3\.6-27b', '{{MODEL_LARGE}}'),
    (r'qwen3\.5-9b', '{{MODEL_DEFAULT}}'),
    (r'nemotron-nano-4b', '{{MODEL_FAST}}'),
    (r'\bLM Studio\b', '{{LMS}}'),

    # ── Author metadata ──
    (r'^author: Russell\b', 'author: {{AUTHOR}}'),

    # ── Networking / infrastructure tools ──
    (r'\bTailscale\b', '{{MESH_VPN}}'),
    (r'\btailscale\b', '{{MESH_VPN_CMD}}'),
    (r'sshfs\b', '{{REMOTE_MOUNT_TOOL}}'),

    # ── Mobile device references ──
    (r'Nubia Z70 Ultra', '{{MOBILE_DEVICE}}'),
    (r'SD 8 Elite', '{{MOBILE_SOC}}'),
    (r'\bAIOS\b \(Android 15\)', '{{MOBILE_OS}}'),

    # ── Project / brand names ──
    (r'\bNanoClaw\b', '{{PERSONAL_ASSISTANT}}'),
    (r'\bOpenClaw\b', '{{AI_FRAMEWORK}}'),
    (r'\b8Bit-Arcade\b', '{{GITHUB_ORG}}'),
    (r'\b8Bit\.io\b', '{{DOMAIN}}'),
    (r'@8bit_arcade1', '{{SOCIAL_HANDLE}}'),

    # ── GitHub username ──
    (r'\bRussell-Bryant\b', '{{GITHUB_USER}}'),

    # ── Secret/API variable names ──
    (r'\bOPENROUTER_API_KEY\b', '{{OR_API_KEY}}'),
    (r'\bMETA_LONG_LIVED_TOKEN\b', '{{META_TOKEN_KEY}}'),
    (r'\bTWITTER_API_KEY\b', '{{TW_API_KEY}}'),
    (r'\bTWITTER_API_SECRET\b', '{{TW_API_SECRET}}'),
    (r'\bTWITTER_ACCESS_TOKEN\b', '{{TW_ACCESS_TOKEN}}'),
    (r'\bTWITTER_ACCESS_TOKEN_SECRET\b', '{{TW_ACCESS_SECRET}}'),
    (r'\bXAI_API_KEY\b', '{{XAI_API_KEY}}'),
    (r'\bAUTHORIZED_EMAILS\b', '{{AUTH_EMAILS_KEY}}'),

    # ── App IDs ──
    (r'\b996540993337274\b', '{{META_APP_ID}}'),

    # ── Domain in code/config (localhost is fine, but specific domains aren't) ──
    (r'\bexpectedOrigin:\s*[\'"]http://localhost:3000[\'"]',
     "expectedOrigin: 'http://localhost:{{BACKEND_PORT}}'"),
    (r'\brpID:\s*[\'"]localhost[\'"]', "rpID: '{{DOMAIN}}'"),
    (r'port:\s*process\.env\.PORT\s*\|\|\s*3001',
     'port: process.env.PORT || {{BACKEND_PORT}}'),

    # ── Cron IDs (instance-specific) ──
    (r'\b3e98de640cdb\b', '{{CRON_ID_SESSION_SUMMARY}}'),
    (r'\be4e7e408dad7\b', '{{CRON_ID_FOUNDER_JOURNAL}}'),
    (r'\b840d4c8c8365\b', '{{CRON_ID_HEALTH_CHECK}}'),
    (r'\bf6cdc8ee995c\b', '{{CRON_ID_CRON_RECEIPT}}'),
    (r'\bf8c7b071db07\b', '{{CRON_ID_DAILY_BRIEF}}'),

    # ── Email addresses ──
    (r'\brussell@8bit\.io\b', '{{ADMIN_EMAIL}}'),

    # ── Usernames & identity (low priority, after paths/IPs) ──
    (r'(?<![/@\w-])russell(?![/\w-])', '{{USER}}'),
    (r'(?<![/@\w-])Russell(?![/\w-])', '{{USER}}'),

    # ── Semantic deployment descriptions (replace specific terms with templates) ──
    # These let users define their own topology (VPS, local, cloud, hybrid)
    (r'\b[Vv]orkstation\b', '{{INFERENCE_HOST}}'),
    (r'\bWindows PC\b', '{{DESKTOP_HOST}}'),
    (r'\bwindows machine\b', '{{DESKTOP_HOST}}'),
    (r'\bmount point on VPS\b', '{{VAULT_MOUNT}}'),
    (r'\bWindows username\b', '{{DESKTOP_USER}}'),

    # VPS / infrastructure terms in prose
    (r'\bagent runs on VPS\b', 'agent runs on {{AGENT_HOST}}'),
    (r'\bAgent on VPS\b', 'Agent on {{AGENT_HOST}}'),
    (r'\bagent host\b', 'agent host ({{AGENT_HOST}})'),
    (r'\bAgent host\b', 'agent host ({{AGENT_HOST}})'),
    (r'\bVPS \(agent host\)\b', '{{AGENT_HOST}}'),
    (r'\bOn VPS\b', 'On {{AGENT_HOST}}'),
    (r'\bon VPS\b', 'on {{AGENT_HOST}}'),
    (r'\bto VPS\b', 'to {{AGENT_HOST}}'),
    (r'\bfrom VPS\b', 'from {{AGENT_HOST}}'),
    (r'\bthe VPS\b', '{{AGENT_HOST}}'),
]


def sanitize(content):
    """Apply all sanitization rules to content."""
    for pattern, repl in RULES:
        content = re.sub(pattern, repl, content)
    return content


def process(src_base, dst_base):
    """Walk src_base, sanitize each text file, write to dst_base."""
    changed = 0
    copied = 0
    skipped = 0

    # Clear destination and rebuild fresh
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


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <src_skills_dir> <dst_skills_dir>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]
    copied, changed, skipped = process(src, dst)
    print(f"Sanitized: {copied} files copied, {changed} sanitized, {skipped} skipped/binary")


if __name__ == '__main__':
    main()
