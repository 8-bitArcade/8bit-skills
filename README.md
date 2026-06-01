# 8Bit Skills Library

Production-tested, platform-agnostic agent skill templates for AI agent platforms.

## What These Are

These skills are **templates** — not plug-and-play. Each one was battle-tested in a real production environment, then sanitized and parameterized so you can adapt it to your own setup.

You **will** need to customize them. Every skill uses `{{VARIABLE}}` placeholders that you replace with your actual config values. Think of these as starting points, not finished products.

**No warranty.** These worked for a specific stack (RTX 3090, Linux VPS, LM Studio, Node.js). Yours may differ. Read the SKILL.md, understand what it does, then adapt it.

## How to Use

1. Browse `skills/` and pick what fits your needs
2. Copy the skill folder into your agent's skills directory (e.g. `~/.hermes/skills/`)
3. Search for `{{` to find all template variables
4. Replace each `{{VARIABLE}}` with your actual values
5. Skills auto-load when their trigger conditions match your context

## Available Skills

- **audio-to-obsidian** — Transcribe audio files to Obsidian notes with summary, transcript, and action items
- **automated-reporting** — Generate automated reports, briefings, and status updates. Covers daily briefs, cron job reports, and scheduled summaries.
- **devops/agent-efficiency-audit** — Audit and review the efficiency of the Hermes agent setup — cron jobs, skills, model selection, context usage, and workflows. Run ad-hoc or via cron.
- **devops/hermes-context-optimization** — Diagnose and reduce Hermes agent context window pressure — config tuning, memory pruning, skill management.
- **devops/hermes-cron-infrastructure** — Maintain, debug, and create Hermes cron jobs and their supporting scripts — including SSHFS timeout handling and health monitoring.
- **devops/hermes-model-catalog-troubleshooting** — Troubleshoot {{LMS}} model catalog issues in Hermes — dropdown not showing models, YAML errors, gateway caching.
- **devops/hermes-runtime-ui** — Configure Hermes runtime UI features — context window indicator footer, display settings, and message formatting for Telegram/Discord gateway.
- **devops/skills-library-management** — Manage and sync agent skills to the 8Bit Skills Library — a GitHub repo of production-ready, platform-grade skills for 8bit-ai.com. Covers skill creation, library sync, bundling filters, and library structure.
- **note-taking/obsidian-linker** — Automatically inject [[wikilinks]] into Obsidian notes based on a master entity list.
- **note-taking/obsidian-vault-management** — Use when managing Obsidian vaults via file tools, web publishing endpoints, and sync workflows. Covers local file access, remote mounting, and custom script integration for note retrieval/editing.

## Platform Variables

Every skill uses the same template variables so you describe your setup once and all skills adapt:

- `{{AGENT_HOST_IP}}` — Where the agent runs (VPS, local, cloud)
- `{{INFERENCE_HOST_IP}}` — Where GPU/LLM inference runs
- `{{DESKTOP_HOST}}` — Your desktop/laptop machine
- `{{LMS_HOST}}` — LLM server (LM Studio, vLLM, etc.)
- `{{LMS}}` — LLM server software name
- `{{MODEL_LARGE}}` — Primary/complex model
- `{{MODEL_FAST}}` — Fast/cheap model
- `{{VAULT_PATH}}` — Obsidian vault location
- `{{MESH_VPN}}` — VPN/mesh networking
- `{{GPU_MODEL}}` — GPU for inference
- `{{DOMAIN}}` — Your domain
- `{{HERMES_HOME}}` — Agent home directory
- `{{BACKEND_PORT}}` — API/backend port
- `{{GITHUB_USER}}` — Your GitHub username
- `{{GITHUB_ORG}}` — Your GitHub organization
- `{{USER}}` — System username
- `{{ADMIN_EMAIL}}` — Admin email
- `{{WHISPER_MODEL}}` — Transcription model

Each skill's SKILL.md notes which variables it uses.

## Supported Setups

Skills are topology-agnostic. Whether you run:
- **Single machine** — agent + inference on one box
- **VPS + workstation** — agent on VPS, inference on local GPU
- **Cloud VM** — everything on a cloud instance
- **Hybrid multi-device** — failover between devices

The `{{AGENT_HOST}}` and `{{INFERENCE_HOST}}` variables adapt each skill to your topology.

## Contributing

Skills are synced from production workflows and sanitized to remove private data.
To contribute: fork this repo, add your skill, and open a PR.

---

*Synced and sanitized from production. Last updated: 2026-06-01 12:37 UTC*
