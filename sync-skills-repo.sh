#!/usr/bin/env bash
# sync-skills-repo.sh — Sync user-created skills to 8Bit-Skills-Library repo
# Called by backup-hermes.sh after each backup run
# Only syncs skills NOT in .bundled_manifest (user-created only)

set -euo pipefail

SKILLS_SRC="$HOME/.hermes/skills"
REPO_DIR="$HOME/8Bit-Skills-Library"
MANIFEST="$SKILLS_SRC/.bundled_manifest"

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

# Copy each user-created skill (raw copy first, then sanitize)
COPIED=0
SKIPPED=0

for category_dir in "$SKILLS_SRC"/*/; do
  [ -d "$category_dir" ] || continue
  category=$(basename "$category_dir")
  [ "$category" = "." ] || true

  # Check if this top-level dir IS a skill (has SKILL.md directly)
  if [ -f "$category_dir/SKILL.md" ]; then
    skill_name="$category"
    if [ "${BUNDLED[$skill_name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
    else
      dest="$REPO_DIR/skills/$category"
      mkdir -p "$dest"
      rsync -a --delete \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        "$category_dir/" "$dest/"
      COPIED=$((COPIED + 1))
    fi
    continue
  fi

  # Otherwise it's a category folder with sub-skills
  for skill_dir in "$category_dir"/*/; do
    [ -d "$skill_dir" ] || continue
    skill_name=$(basename "$skill_dir")
    [ -f "$skill_dir/SKILL.md" ] || continue

    if [ "${BUNDLED[$skill_name]+isset}" ]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi

    dest="$REPO_DIR/skills/$category/$skill_name"
    mkdir -p "$dest"
    rsync -a --delete \
      --exclude='__pycache__' \
      --exclude='*.pyc' \
      --exclude='.DS_Store' \
      "$skill_dir/" "$dest/"

    COPIED=$((COPIED + 1))
  done
done

# Sanitize all copied skills — strip private data, replace with {{TEMPLATES}}
echo "Sanitizing copied skills..."
SANITIZE_OUTPUT=$(python3 "$REPO_DIR/sanitize.py" "$REPO_DIR/skills" "$REPO_DIR/skills" 2>&1)
echo "$SANITIZE_OUTPUT"

# Collect skill list for README (handles both flat and category skills)
SKILL_LIST=""

# Flat skills (directly under skills/)
for skill_dir in "$REPO_DIR/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  name=$(basename "$skill_dir")
  if [ -f "$skill_dir/SKILL.md" ]; then
    desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" | sed 's/description: *//;s/^"//;s/"$//' || echo "")
    SKILL_LIST="${SKILL_LIST}- **${name}** — ${desc}"$'\n'
  fi
done

# Category-based skills (skills/category/skill/)
for skill_dir in "$REPO_DIR/skills"/*/*/; do
  [ -d "$skill_dir" ] || continue
  category=$(basename "$(dirname "$skill_dir")")
  name=$(basename "$skill_dir")
  [ -f "$skill_dir/SKILL.md" ] || continue
  desc=$(grep -m1 "^description:" "$skill_dir/SKILL.md" | sed 's/description: *//;s/^"//;s/"$//' || echo "")
  SKILL_LIST="${SKILL_LIST}- **${category}/${name}** — ${desc}"$'\n'
done

# Generate README
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
python3 - "$REPO_DIR/README.md" "$TIMESTAMP" "$SKILL_LIST" << 'PYEOF'
import sys
path, timestamp, skill_list = sys.argv[1], sys.argv[2], sys.argv[3]
readme = f"""# 8Bit Skills Library

Production-ready agent skills for the [8Bit AI](https://8bit-ai.com) platform.

Each skill is self-contained — drop it into your `~/.hermes/skills/` directory and customize.

## Available Skills

{skill_list}
## Usage

1. Browse the `skills/` directory
2. Copy any skill folder into your `~/.hermes/skills/` directory
3. Customize the SKILL.md and supporting files for your setup
4. Skills auto-load when relevant triggers are detected

## Contributing

Skills are synced automatically from production agent workflows.
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
