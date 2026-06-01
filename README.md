# 8Bit Skills Library

Production-ready agent skills for the [8Bit AI](https://8bit-ai.com) platform.

Each skill is self-contained — drop it into your `~/.hermes/skills/` directory and customize.

## Available Skills

- **audio-to-obsidian** — Transcribe audio files to Obsidian notes with summary, transcript, and action items
- **automated-reporting** — Generate automated reports, briefings, and status updates. Covers daily briefs, cron job reports, and scheduled summaries.
- **founder-journal-system** — Curated founder narrative intelligence system. Weekly journal generation from Obsidian vault, session logs, and operational data through a multi-stage editorial pipeline with human gates.
- **pitch-deck-creation** — Create investor-facing pitch decks tailored to specific programs, accelerators, or investor audiences
- **content-publishing/social-media-publishing** — Platform-specific API setup, credential management, and posting workflows for automated content distribution across Instagram, Facebook, X/Twitter, YouTube, and TikTok.
- **devops/agent-efficiency-audit** — Audit and review the efficiency of the Hermes agent setup — cron jobs, skills, model selection, context usage, and workflows. Run ad-hoc or via cron.
- **devops/hermes-context-optimization** — Diagnose and reduce Hermes agent context window pressure — config tuning, memory pruning, skill management.
- **devops/hermes-cron-infrastructure** — Maintain, debug, and create Hermes cron jobs and their supporting scripts — including SSHFS timeout handling and health monitoring.
- **devops/hermes-lmstudio-catalog** — Configure LM Studio model catalog in Hermes — add custom models to slash command dropdown.
- **devops/hermes-mobile-node** — Design and deploy a mobile AI inference node (phone) that acts as failover for a VPS+workstation setup. Covers health endpoints, cron relay routing, model management, and Termux deployment.
- **devops/hermes-model-catalog-troubleshooting** — Troubleshoot LM Studio model catalog issues in Hermes — dropdown not showing models, YAML errors, gateway caching.
- **devops/hermes-provider-config** — Configure and troubleshoot Hermes LLM providers — LM Studio, OpenRouter fallback, API keys, privacy settings, and gateway caching.
- **devops/hermes-runtime-ui** — Configure Hermes runtime UI features — context window indicator footer, display settings, and message formatting for Telegram/Discord gateway.
- **note-taking/obsidian-linker** — Automatically inject [[wikilinks]] into Obsidian notes based on a master entity list.
- **note-taking/obsidian-vault-management** — Use when managing Obsidian vaults via file tools, web publishing endpoints, and sync workflows. Covers local file access, remote mounting, and custom script integration for note retrieval/editing.
- **software-development/provider-setup-and-fallback** — Provider configuration, fallback chains, and troubleshooting for Hermes LLM providers (OpenRouter, LM Studio, etc.)
- **software-development/secure-auth-backend** — Build secure authentication backends with WebAuthn passkeys, email whitelists, JWT sessions, and SQLite storage

## Usage

1. Browse the `skills/` directory
2. Copy any skill folder into your `~/.hermes/skills/` directory
3. Customize the SKILL.md and supporting files for your setup
4. Skills auto-load when relevant triggers are detected

## Contributing

Skills are synced automatically from production agent workflows.
To propose a new skill, open a PR with the skill directory.

---

*Auto-synced from production. Last updated: 2026-06-01 06:33 UTC*
