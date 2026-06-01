# 8Bit Skills Library — Repository Reference

**Repo**: `{{GITHUB_USER}}/8Bit-Skills-Library` (private)
**URL**: https://github.com/{{GITHUB_USER}}/8Bit-Skills-Library
**Purpose**: Production-ready agent skills for the 8Bit AI platform
**Auto-sync**: Daily at 08:00 CEST (cron job ID: 85b2e195887e)

## Setup on a Fresh VPS

1. Clone the repo:
   ```bash
   git clone git@github.com:{{GITHUB_USER}}/8Bit-Skills-Library.git ~/8Bit-Skills-Library
   ```

2. Copy skills to Hermes:
   ```bash
   # Flat skills
   cp -r ~/8Bit-Skills-Linux/skills/audio-to-obsidian ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/automated-reporting ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/founder-journal-system ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/pitch-deck-creation ~/.hermes/skills/

   # Category skills
   cp -r ~/8Bit-Skills-Library/skills/content-publishing ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/devops ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/note-taking ~/.hermes/skills/
   cp -r ~/8Bit-Skills-Library/skills/software-development ~/.hermes/skills/
   ```

3. The sync script (`sync-skills-repo.sh`) is in the repo root. Move it if needed.

## Current Skill Count

17 skills across 4 categories + 4 flat skills (as of 2026-06-01).

## Sync Behavior

- Only syncs skills NOT listed in `~/.hermes/skills/.bundled_manifest`
- Generates README.md automatically with skill list and descriptions
- Commits only when changes are detected
- Excludes `__pycache__/`, `*.pyc`, `.DS_Store`