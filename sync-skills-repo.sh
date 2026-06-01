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

# ── 1b. Load denied skills (never sync these) ──
declare -A DENIED
DENIED_LIST=$(python3 -c "
import json
from pathlib import Path
denied_file = Path('$REPO_DIR/.denied-skills.json')
if denied_file.exists():
    data = json.load(open(denied_file))
    for name in data.get('denied', []):
        if isinstance(name, dict):
            print(name.get('name', ''))
        else:
            print(name)
" 2>/dev/null || true)
while IFS= read -r name; do
  [ -n "$name" ] && DENIED["$name"]=1
done <<< "$DENIED_LIST"

# ── 1c. Load pending skills (not ready for sync either) ──
declare -A PENDING
PENDING_LIST=$(python3 -c "
import json
from pathlib import Path
state_file = Path('$REPO_DIR/.approval-state.json')
if state_file.exists():
    data = json.load(open(state_file))
    for entry in data.get('pending', []):
        print(entry.get('name', ''))
" 2>/dev/null || true)
while IFS= read -r name; do
  [ -n "$name" ] && PENDING["$name"]=1
done <<< "$PENDING_LIST"

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
    if [ "${DENIED[$name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    if [ "${PENDING[$name]+isset}" ]; then
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
    if [ "${DENIED[$skill_name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
    if [ "${PENDING[$skill_name]+isset}" ]; then
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

# ── 5. Git commit locally (NO auto-push — waits for human approval) ──
cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
  # Output empty JSON so cron knows there's nothing to review
  echo '{"status": "no_changes"}'
  exit 0
fi

git commit -m "Sync & sanitize — ${TIMESTAMP} (${COPIED} skills)"

# ── 6. Generate diff summary for human review ──
DIFF_SUMMARY=$(git diff --stat HEAD~1 HEAD 2>/dev/null || echo "first commit")
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | head -20)

echo "── SKILLS SYNC REVIEW ──"
echo "Skills: ${COPIED} synced, ${SKIPPED} bundled skipped"
echo ""
echo "Changed files:"
echo "$CHANGED_FILES"
echo ""
echo "Diff stats:"
echo "$DIFF_SUMMARY"
echo ""
echo "To approve and push, reply: push 8bit skills"
echo "To discard, reply: discard 8bit skills"
echo ""
echo "ORG_TARGET is NOT set — no automatic mirror to 8Bit-Arcade org."

# ── 7. Mirror to org public repo (only if ORG_TARGET is explicitly set) ──
# This requires: gh CLI with org write permission, AND human approval first
if [ -n "$ORG_TARGET" ]; then
  echo "ORG_TARGET=${ORG_TARGET} but auto-mirror is DISABLED pending manual review."
fi

# ── 8. Mark pending approval (atomic flag file for cron pickup) ──
PENDING_FILE="$REPO_DIR/.pending-push"
cat > "$PENDING_FILE" << EOF
COMMIT=$(git rev-parse HEAD)
TIMESTAMP=${TIMESTAMP}
SKILLS=${COPIED}
FILES_CHANGED=$(echo "$CHANGED_FILES" | wc -l)
EOF
echo ""
echo "Pending push flag written: $PENDING_FILE"
