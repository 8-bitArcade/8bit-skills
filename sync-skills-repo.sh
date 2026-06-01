#!/usr/bin/env bash
# sync-skills-repo.sh — Sync user-created skills to 8Bit-Skills-Library repo
# Sanitizes all skills before committing (strips private data, replaces with {{TEMPLATES}})

set -euo pipefail

SKILLS_SRC="$HOME/.hermes/skills"
REPO_DIR="$HOME/8Bit-Skills-Library"
MANIFEST="$SKILLS_SRC/.bundled_manifest"
STAGING="$REPO_DIR/.staging"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ERROR: $REPO_DIR is not a git repo. Run setup first."
  exit 1
fi

# Build set of bundled skill names
declare -A BUNDLED
if [ -f "$MANIFEST" ]; then
  while IFS= read -r line; do
    name="${line%%:*}"
    BUNDLED["$name"]=1
  done < "$MANIFEST"
fi

# Clean staging
rm -rf "$STAGING"
mkdir -p "$STAGING"

# Copy each user-created skill to staging
# Structure: flat skills go to STAGING/skill_name/, category skills to STAGING/category/skill_name/
COPIED=0
SKIPPED=0

for item in "$SKILLS_SRC"/*/; do
  [ -d "$item" ] || continue
  name=$(basename "$item")

  if [ -f "$item/SKILL.md" ]; then
    # Flat/top-level skill (e.g. automated-reporting/, pitch-deck-creation/)
    if [ "${BUNDLED[$name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
      "$item/" "$STAGING/$name/"
    COPIED=$((COPIED + 1))
  else
    # Category directory (e.g. devops/, note-taking/) — contains sub-skills
    for skill_item in "$item"/*/; do
      [ -d "$skill_item" ] || continue
      skill_name=$(basename "$skill_item")
      [ -f "$skill_item/SKILL.md" ] || continue

      if [ "${BUNDLED[$skill_name]+isset}" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
      fi

      mkdir -p "$STAGING/$name/$skill_name"
      rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
        "$skill_item/" "$STAGING/$name/$skill_name/"
      COPIED=$((COPIED + 1))
    done
  fi
done

# Sanitize: strip private data from staging, write sanitized to repo skills/
echo "Sanitizing ${COPIED} skills..."
SANITIZE_OUTPUT=$(python3 "$REPO_DIR/sanitize.py" "$STAGING" "$REPO_DIR/skills" 2>&1)
echo "$SANITIZE_OUTPUT"

# Clean staging
rm -rf "$STAGING"

# Collect skill list for README
SKILL_LIST=""

for skill_dir in "$REPO_DIR/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || continue
  desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" 2>/dev/null | sed 's/description: *//;s/^"//;s/"$//' || echo "")
  SKILL_LIST="${SKILL_LIST}- **${name}** — ${desc}"$'\n'
done

for skill_dir in "$REPO_DIR/skills"/*/*/; do
  [ -d "$skill_dir" ] || continue
  category=$(basename "$(dirname "$skill_dir")")
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || continue
  desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" 2>/dev/null | sed 's/description: *//;s/^"//;s/"$//' || echo "")
  SKILL_LIST="${SKILL_LIST}- **${category}/${name}** — ${desc}"$'\n'
done

# Generate README
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
python3 - "$REPO_DIR/README.md" "$TIMESTAMP" "$SKILL_LIST" << 'PYEOF'
import sys
path, timestamp, skill_list = sys.argv[1], sys.argv[2], sys.argv[3]
readme = f"""# 8Bit Skills Library

Production-ready agent skills for AI agent platforms (Hermes, OpenClaw, etc.).

Each skill is self-contained — copy it into your skills directory and customize
the `{{{{VARIABLE}}}}` template values for your setup.

## Available Skills

{skill_list}
## Quick Start

1. Browse the `skills/` directory
2. Copy any skill folder into your `~/.hermes/skills/` directory
3. Search for `{{{{` in the skill files to find template variables
4. Replace each `{{{{VARIABLE}}}}` with your actual value
5. Skills auto-load when relevant triggers are detected

## Template Variables

Skills use `{{{{VARIABLE}}}}` placeholders for instance-specific values:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{{{WORKSTATION_IP}}}}` | Your workstation/local AI server IP | `192.168.1.100` |
| `{{{{VPS_IP}}}}` | Your VPS/server IP | `203.0.113.50` |
| `{{{{LMS_HOST}}}}` | LLM server host:port | `192.168.1.100:1234` |
| `{{{{LMS}}}}` | LLM server name | LM Studio |
| `{{{{MODEL}}}}` / `{{{{MODEL_LARGE}}}}` | Primary model name | `qwen/qwen3.6-27b` |
| `{{{{VAULT_MOUNT}}}}` | Obsidian vault mount path | `~/.obsidian_vault` |
| `{{{{HERMES_HOME}}}}` | Hermes agent home | `~/.hermes` |
| `{{{{ENV_PATH}}}}` | Environment file path | `~/.hermes/.env` |
| `{{{{USER}}}}` | Server username | `russell` |
| `{{{{WINDOWS_USER}}}}` | Windows machine username | `youruser` |
| `{{{{GPU_MODEL}}}}` | GPU model for inference | RTX 3090 |
| `{{{{DOMAIN}}}}` | Your domain | `example.com` |
| `{{{{GITHUB_USER}}}}` | GitHub username | `yourname` |

Each skill's SKILL.md lists the specific variables it uses.

## Contributing

To propose a new skill, open a PR with the skill directory.

---

*Auto-synced from production. Last updated: {timestamp}*
"""
with open(path, "w") as f:
    f.write(readme)
PYEOF

# Git commit and push
cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  echo "No changes to sync."
else
  git commit -m "Sync skills — ${TIMESTAMP} (${COPIED} skills, sanitized)"
  git push origin main 2>&1
  echo "Synced ${COPIED} skills, skipped ${SKIPPED} bundled."
fi
