# 8Bit Skills Library

Production-ready, platform-agnostic agent skills for AI agent platforms.

Each skill is a self-contained template — copy it into your `~/.hermes/skills/`
directory and customize the `{{VARIABLE}}` placeholders for your setup.

Works on: local machine, VPS, cloud VM, or hybrid multi-device.

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

1. Browse `skills/` and pick what you need
2. Copy the skill folder into your `~/.hermes/skills/`
3. Search for `{{` to find template variables
4. Replace each `{{VARIABLE}}` with your actual setup values
5. Skills auto-load when their trigger conditions match

## Platform Variables

Every skill uses the same template variables so you consistently describe
your setup once and all skills adapt:

| Variable | What It Means | Examples |
|----------|---------------|----------|
| `{{AGENT_HOST_IP}}` | Where the agent runs (VPS, local, cloud) | `192.168.1.10`, `10.0.0.1` |
| `{{INFERENCE_HOST_IP}}` | Where GPU/LLM inference runs | `192.168.1.100`, `localhost` |
| `{{DESKTOP_HOST}}` | Your desktop/laptop machine | `my-pc`, `macbook-pro` |
| `{{LMS_HOST}}` | LLM server (LM Studio, vLLM, etc.) | `192.168.1.100:1234` |
| `{{LMS}}` | LLM server software name | `LM Studio`, `Ollama`, `vLLM` |
| `{{MODEL_LARGE}}` | Primary/complex model | `qwen/qwen3.6-27b` |
| `{{MODEL_FAST}}` | Fast/cheap model | `nemotron-nano-4b` |
| `{{VAULT_PATH}}` | Obsidian vault location | `~/.obsidian_vault`, `~/Documents/Vault` |
| `{{MESH_VPN}}` | VPN/mesh networking | `Tailscale`, `ZeroTier` |
| `{{GPU_MODEL}}` | GPU for inference | `RTX 3090`, `M4 Max` |
| `{{DOMAIN}}` | Your domain | `example.com` |
| `{{HERMES_HOME}}` | Agent home directory | `~/.hermes` |
| `{{BACKEND_PORT}}` | API/backend port | `3001`, `8080` |
| `{{GITHUB_USER}}` | Your GitHub username | `yourname` |
| `{{GITHUB_ORG}}` | Your GitHub organization | `yourorg` |
| `{{USER}}` | System username | `youruser` |
| `{{ADMIN_EMAIL}}` | Admin email | `admin@example.com` |
| `{{WHISPER_MODEL}}` | Transcription model | `large-v3-turbo` |

Each skill's SKILL.md notes which variables it uses.

## Architecture Skills Support

Skills are topology-agnostic. Whether you run:
- **Single machine**: agent + inference on one box
- **VPS + workstation**: agent on VPS, inference on local GPU
- **Cloud VM**: everything on a cloud instance
- **Hybrid multi-device**: failover between devices

The `{{AGENT_HOST}}` and `{{INFERENCE_HOST}}` variables adapt each
skill to your setup. Set them once per skill, then the instructions follow
your topology.

## Contributing

Skills are synced from production workflows and sanitized to remove private data.
To contribute: fork this repo, add your skill, and open a PR.

---

*Auto-synced and sanitized from production. Last updated: 2026-06-01 07:41 UTC*
