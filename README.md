# 8Bit Skills Library

Production-ready agent skills for AI agent platforms (Hermes, OpenClaw, etc.).

Each skill is self-contained — copy it into your skills directory and customize
the `{{VARIABLE}}` template values for your setup.

## Available Skills

- **audio-to-obsidian** — Transcribe audio files to Obsidian notes with summary, transcript, and action items
- **automated-reporting** — Generate automated reports, briefings, and status updates. Covers daily briefs, cron job reports, and scheduled summaries.
- **founder-journal-system** — Curated founder narrative intelligence system. Weekly journal generation from Obsidian vault, session logs, and operational data through a multi-stage editorial pipeline with human gates.
- **pitch-deck-creation** — Create investor-facing pitch decks tailored to specific programs, accelerators, or investor audiences
- **content-publishing/social-media-publishing** — Platform-specific API setup, credential management, and posting workflows for automated content distribution across Instagram, Facebook, X/Twitter, YouTube, and TikTok.
- **devops/agent-efficiency-audit** — Audit and review the efficiency of the Hermes agent setup — cron jobs, skills, model selection, context usage, and workflows. Run ad-hoc or via cron.
- **devops/hermes-context-optimization** — Diagnose and reduce Hermes agent context window pressure — config tuning, memory pruning, skill management.
- **devops/hermes-cron-infrastructure** — Maintain, debug, and create Hermes cron jobs and their supporting scripts — including SSHFS timeout handling and health monitoring.
- **devops/hermes-lmstudio-catalog** — Configure {{LMS}} model catalog in Hermes — add custom models to slash command dropdown.
- **devops/hermes-mobile-node** — Design and deploy a mobile AI inference node (phone) that acts as failover for a VPS+workstation setup. Covers health endpoints, cron relay routing, model management, and Termux deployment.
- **devops/hermes-model-catalog-troubleshooting** — Troubleshoot {{LMS}} model catalog issues in Hermes — dropdown not showing models, YAML errors, gateway caching.
- **devops/hermes-provider-config** — Configure and troubleshoot Hermes LLM providers — {{LMS}}, OpenRouter fallback, API keys, privacy settings, and gateway caching.
- **devops/hermes-runtime-ui** — Configure Hermes runtime UI features — context window indicator footer, display settings, and message formatting for Telegram/Discord gateway.
- **devops/skills-library-management** — Manage and sync agent skills to the 8Bit Skills Library — a GitHub repo of production-ready, platform-grade skills for 8bit-ai.com. Covers skill creation, library sync, bundling filters, and library structure.
- **note-taking/obsidian-linker** — Automatically inject [[wikilinks]] into Obsidian notes based on a master entity list.
- **note-taking/obsidian-vault-management** — Use when managing Obsidian vaults via file tools, web publishing endpoints, and sync workflows. Covers local file access, remote mounting, and custom script integration for note retrieval/editing.
- **software-development/provider-setup-and-fallback** — Provider configuration, fallback chains, and troubleshooting for Hermes LLM providers (OpenRouter, {{LMS}}, etc.)
- **software-development/secure-auth-backend** — Build secure authentication backends with WebAuthn passkeys, email whitelists, JWT sessions, and SQLite storage

## Quick Start

1. Browse the `skills/` directory
2. Copy any skill folder into your `~/.hermes/skills/` directory
3. Search for `{{` in the skill files to find template variables
4. Replace each `{{VARIABLE}}` with your actual value
5. Skills auto-load when relevant triggers are detected

## Template Variables

Skills use `{{VARIABLE}}` placeholders for instance-specific values:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{WORKSTATION_IP}}` | Your workstation/local AI server IP | `192.168.1.100` |
| `{{VPS_IP}}` | Your VPS/server IP | `203.0.113.50` |
| `{{LMS_HOST}}` | LLM server host:port | `192.168.1.100:1234` |
| `{{LMS}}` | LLM server name | LM Studio |
| `{{MODEL}}` / `{{MODEL_LARGE}}` | Primary model name | `qwen/qwen3.6-27b` |
| `{{VAULT_MOUNT}}` | Obsidian vault mount path | `~/.obsidian_vault` |
| `{{HERMES_HOME}}` | Hermes agent home | `~/.hermes` |
| `{{ENV_PATH}}` | Environment file path | `~/.hermes/.env` |
| `{{USER}}` | Server username | `russell` |
| `{{WINDOWS_USER}}` | Windows machine username | `youruser` |
| `{{GPU_MODEL}}` | GPU model for inference | RTX 3090 |
| `{{DOMAIN}}` | Your domain | `example.com` |
| `{{GITHUB_USER}}` | GitHub username | `yourname` |

Each skill's SKILL.md lists the specific variables it uses.

## Contributing

To propose a new skill, open a PR with the skill directory.

---

*Auto-synced from production. Last updated: 2026-06-01 07:17 UTC*
