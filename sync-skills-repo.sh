#!/usr/bin/env bash
# sync-skills-repo.sh — Sync user-created skills through the full pipeline:
#
#   Source skills → Staging → Sanitize → Personal repo → [fork to org]
#
#   Personal staging repo:  Russell-Bryant/8Bit-Skills-Library  (private)
#   Public org repo:        8Bit-Arcade/8bit-skills            (public, when forked)
#
#   The sanitizer strips ALL private data and makes templates platform-agnostic
#   (VPS, local, cloud, or hybrid setups).

set -euo pipefail

SKILLS_SRC="$HOME/.hermes/skills"
REPO_DIR="$HOME/8Bit-Skills-Library"
MANIFEST="$SKILLS_SRC/.bundled_manifest"
STAGING="$REPO_DIR/.staging"

# Public org repo target (set to empty string to skip org push)
ORG_TARGET="${S8B_ORG_TARGET:-}"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ERROR: $REPO_DIR is not a git repo. Run setup first."
  exit 1
fi

# ── 1. Build bundled skill exclusion set ──
declare -A BUNDLED
if [ -f "$MANIFEST" ]; then
  while IFS= read -r line; do
    name="${line%%:*}"
    BUNDLED["$name"]=1
  done < "$MANIFEST"
fi

# ── 2. Copy skills to staging ──
rm -rf "$STAGING"
mkdir -p "$STAGING"

COPIED=0
SKIPPED=0

for item in "$SKILLS_SRC"/*/; do
  [ -d "$item" ] || continue
  name=$(basename "$item")

  if [ -f "$item/SKILL.md" ]; then
    # Flat/top-level skill
    if [ "${BUNDLED[$name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    rsync -a --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
      "$item/" "$STAGING/$name/"
    COPIED=$((COPIED + 1))
  else
    # Category directory
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

# ── 3. Sanitize: staging → repo skills/ ──
echo "Sanitizing ${COPIED} skills..."
python3 "$REPO_DIR/sanitize.py" "$STAGING" "$REPO_DIR/skills"
rm -rf "$STAGING"

# ── 4. Generate README from sanitized skills ──
SKILL_LIST=""

for skill_dir in "$REPO_DIR/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || continue
  desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" 2>/dev/null \
    | sed 's/description: *//;s/^"//;s/"$//' || echo "")
  SKILL_LIST="${SKILL_LIST}- **${name}** — ${desc}"$'\n'
done

for skill_dir in "$REPO_DIR/skills"/*/*/; do
  [ -d "$skill_dir" ] || continue
  category=$(basename "$(dirname "$skill_dir")")
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || continue
  desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" 2>/dev/null \
    | sed 's/description: *//;s/^"//;s/"$//' || echo "")
  SKILL_LIST="${SKILL_LIST}- **${category}/${name}** — ${desc}"$'\n'
done

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")

python3 - "$REPO_DIR/README.md" "$TIMESTAMP" "$SKILL_LIST" << 'PYEOF'
import sys
path, timestamp, skill_list = sys.argv[1], sys.argv[2], sys.argv[3]
readme = f"""# 8Bit Skills Library

Production-ready, platform-agnostic agent skills for AI agent platforms.

Each skill is a self-contained template — copy it into your `~/.hermes/skills/`
directory and customize the `{{{{VARIABLE}}}}` placeholders for your setup.

Works on: local machine, VPS, cloud VM, or hybrid multi-device.

## Available Skills

{skill_list}
## Quick Start

1. Browse `skills/` and pick what you need
2. Copy the skill folder into your `~/.hermes/skills/`
3. Search for `{{{{` to find template variables
4. Replace each `{{{{VARIABLE}}}}` with your actual setup values
5. Skills auto-load when their trigger conditions match

## Platform Variables

Every skill uses the same template variables so you consistently describe
your setup once and all skills adapt:

| Variable | What It Means | Examples |
|----------|---------------|----------|
| `{{{{AGENT_HOST_IP}}}}` | Where the agent runs (VPS, local, cloud) | `192.168.1.10`, `10.0.0.1` |
| `{{{{INFERENCE_HOST_IP}}}}` | Where GPU/LLM inference runs | `192.168.1.100`, `localhost` |
| `{{{{DESKTOP_HOST}}}}` | Your desktop/laptop machine | `my-pc`, `macbook-pro` |
| `{{{{LMS_HOST}}}}` | LLM server (LM Studio, vLLM, etc.) | `192.168.1.100:1234` |
| `{{{{LMS}}}}` | LLM server software name | `LM Studio`, `Ollama`, `vLLM` |
| `{{{{MODEL_LARGE}}}}` | Primary/complex model | `qwen/qwen3.6-27b` |
| `{{{{MODEL_FAST}}}}` | Fast/cheap model | `nemotron-nano-4b` |
| `{{{{VAULT_PATH}}}}` | Obsidian vault location | `~/.obsidian_vault`, `~/Documents/Vault` |
| `{{{{MESH_VPN}}}}` | VPN/mesh networking | `Tailscale`, `ZeroTier` |
| `{{{{GPU_MODEL}}}}` | GPU for inference | `RTX 3090`, `M4 Max` |
| `{{{{DOMAIN}}}}` | Your domain | `example.com` |
| `{{{{HERMES_HOME}}}}` | Agent home directory | `~/.hermes` |
| `{{{{BACKEND_PORT}}}}` | API/backend port | `3001`, `8080` |
| `{{{{GITHUB_USER}}}}` | Your GitHub username | `yourname` |
| `{{{{GITHUB_ORG}}}}` | Your GitHub organization | `yourorg` |
| `{{{{USER}}}}` | System username | `youruser` |
| `{{{{ADMIN_EMAIL}}}}` | Admin email | `admin@example.com` |
| `{{{{WHISPER_MODEL}}}}` | Transcription model | `large-v3-turbo` |

Each skill's SKILL.md notes which variables it uses.

## Architecture Skills Support

Skills are topology-agnostic. Whether you run:
- **Single machine**: agent + inference on one box
- **VPS + workstation**: agent on VPS, inference on local GPU
- **Cloud VM**: everything on a cloud instance
- **Hybrid multi-device**: failover between devices

The `{{{{AGENT_HOST}}}}` and `{{{{INFERENCE_HOST}}}}` variables adapt each
skill to your setup. Set them once per skill, then the instructions follow
your topology.

## Contributing

Skills are synced from production workflows and sanitized to remove private data.
To contribute: fork this repo, add your skill, and open a PR.

---

*Auto-synced and sanitized from production. Last updated: {timestamp}*
"""
with open(path, "w") as f:
    f.write(readme)
PYEOF

# ── 5. Git commit & push to personal staging repo ──
cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  echo "No changes to sync."
  exit 0
fi

git commit -m "Sync & sanitize — ${TIMESTAMP} (${COPIED} skills)"
git push origin main 2>&1
echo "Pushed to personal repo: ${COPIED} skills, ${SKIPPED} bundled skipped."

# ── 6. Mirror to org public repo (if target set & permission available) ──
if [ -n "$ORG_TARGET" ]; then
  echo "Attempting mirror to org: ${ORG_TARGET}..."
  # Mirror via git remote + push
  ORG_URL="https://github.com/${ORG_TARGET}.git"
  git remote remove org-mirror 2>/dev/null || true
  git remote add org-mirror "$ORG_URL" 2>/dev/null || true

  if git push org-mirror main 2>&1; then
    echo "Mirrored to ${ORG_TARGET} ✓"
    git remote remove org-mirror 2>/dev/null || true
  else
    echo "WARNING: Could not push to org (need org write permission)."
    echo "  Manual step: fork https://github.com/Russell-Bryant/8Bit-Skills-Library"
    echo "  to ${ORG_TARGET} via GitHub web UI."
    git remote remove org-mirror 2>/dev/null || true
  fi
fi
