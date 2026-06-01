---
name: skills-library-management
description: "Manage and sync agent skills to the 8Bit Skills Library — a GitHub repo of production-ready, platform-grade skills for 8bit-ai.com. Covers skill creation, library sync, bundling filters, and library structure."
version: 1.0.0
author: Russell
license: MIT
---

# Skills Library Management

Manage the 8Bit Skills Library — a curated collection of production-ready agent skills published to GitHub for the 8Bit AI platform.

## Trigger

- Creating a new skill that should be published to the library
- Updating an existing skill that's already in the library
- Running the sync script manually or debugging sync failures
- Reviewing the skill library for quality, overlap, or gaps
- Setting up the library on a fresh VPS

## Library Overview

**Repo**: `{{GITHUB_USER}}/8Bit-Skills-Library` (private on GitHub)
**Auto-sync**: Daily at 08:00 CEST via Hermes cron
**Sync script**: `{{SKILLS_LIBRARY_DIR}}/sync-skills-repo.sh`

Skills are synced from `~/.hermes/skills/` to the repo, excluding bundled Hermes skills (filtered via `.bundled_manifest`).

## Library Structure

```
8Bit-Skills-Library/
├── README.md                          # Auto-generated skill list
├── sync-skills-repo.sh                # Sync script
└── skills/
    ├── audio-to-obsidian/            # Flat skills (SKILL.md at root)
    ├── automated-reporting/
    ├── founder-journal-system/
    ├── pitch-deck-creation/
    ├── content-publishing/            # Category folders
    │   └── social-media-publishing/
    ├── devops/
    │   ├── agent-efficiency-audit/
    │   ├── hermes-context-optimization/
    │   ├── hermes-cron-infrastructure/
    │   ├── hermes-lmstudio-catalog/
    │   ├── hermes-mobile-node/
    │   ├── hermes-model-catalog-troubleshooting/
    │   ├── hermes-provider-config/
    │   └── hermes-runtime-ui/
    ├── note-taking/
    │   ├── obsidian-linker/
    │   └── obsidian-vault-management/
    └── software-development/
        ├── provider-setup-and-fallback/
        └── secure-auth-backend/
```

Each skill directory contains:
- `SKILL.md` — the skill definition (required)
- `references/` — domain docs, error transcripts, API references
- `scripts/` — runnable scripts (verification, generation, probes)
- `templates/` — starter files meant to be copied and modified

## Skill Authoring Standards

Skills in the library must be **class-level**, not session-specific:

- **Name**: `category/feature` format. Never a PR number, error string, or session artifact name.
- **SKILL.md**: Rich frontmatter (name, description, version, author, license), clear triggers, numbered steps, pitfalls section.
- **Support files**: Use `references/` for docs, `scripts/` for runnable code, `templates/` for boilerplate.
- **Self-contained**: A user should be able to drop the skill dir into `~/.hermes/skills/` and customize.

### SKILL.md Template

See `templates/skill-template.md` for the canonical scaffold.

## Adding a New Skill

1. Create the skill directory in `~/.hermes/skills/`:
   - Category-based: `~/.hermes/skills/<category>/<skill-name>/`
   - Flat: `~/.hermes/skills/<skill-name>/`

2. Write `SKILL.md` following the template

3. Add support files under `references/`, `scripts/`, `templates/` as needed

4. Run the sync script manually:
   ```bash
   bash {{SKILLS_LIBRARY_DIR}}/sync-skills-repo.sh
   ```

5. Verify on GitHub

## Running the Sync Manually

```bash
cd {{SKILLS_LIBRARY_DIR}}
bash sync-skills-repo.sh
```

The script:
1. Reads `~/.hermes/skills/.bundled_manifest` to exclude bundled skills
2. Syncs each skill dir via `rsync -a --delete`
3. Generates `README.md` with full skill list + descriptions
4. Commits and pushes only if changes detected

Output: "Synced N skills, skipped M bundled." or "No changes to sync."

## Bundled Skill Filtering

The `.bundled_manifest` in `~/.hermes/skills/` lists Hermes-bundled plugin skills (e.g., `obsidian`, `spotify`, `hermes-agent`). These are NOT synced to the library.

**Do NOT add user-created skills to `.bundled_manifest`** — it's Hermes-managed.

User-created skills that happen to share a name with a bundled plugin (e.g., `automated-reporting`) are correctly synced because they're not in the manifest.

## During Skill Review Passes

When the system prompts a review of the skill library (meta-review):

1. **Class-level check**: No skill should be named after a specific session, PR, or error
2. **Overlap check**: Flag any two skills with overlapping coverage
3. **Support file pointers**: Every support file should be referenced in the SKILL.md
4. **Pitfall currency**: User corrections from recent sessions should be encoded as pitfalls
5. **Trigger richness**: Each skill's trigger section should cover real past usage patterns

## Pitfalls

- **Don't edit `sync-skills-repo.sh` without testing** — a broken script means no sync
- **The glob pattern in README generation** must handle both flat skills and category skills (`skills/*/` and `skills/*/*/`)
- **`__pycache__` and `*.pyc`** are excluded from sync — don't accidentally include them in the library
- **The `.bundled_manifest` uses plugin package names**, not skill directory names. User skills like `automated-reporting` are NOT in the manifest even if they sound like bundled features.
- **GitHub org transfer requires web UI** — `gh api repos/{owner}/{repo}/transfer -f new_owner=Org` returns HTTP 422 when the authenticated user lacks org create-repo permission (common for VPS SSH tokens). Workaround: owner must go to repo Settings → Danger Zone → Transfer ownership on github.com. No CLI/API workaround exists.
- **Moving a repo from personal to org after creation** — it's not just an API call. Plan ahead: if the repo should live in the org, either (a) have an org owner create it empty first, then push, or (b) use the web UI transfer.
- **Don't store secrets** in skill files. The repo should be shareable. Use env vars or config that the user provides.

## References

- `references/github-repo-setup.md` — repo URL, fresh-VPS setup, current skill count
- `templates/skill-template.md` — canonical SKILL.md scaffold for new skills

## Verification

After adding or updating a skill:
1. Run sync: `bash sync-skills-repo.sh`
2. Check GitHub shows the updated skill
3. Verify README includes the skill in the listing
4. Confirm no secrets were committed (check `git diff` before first push)
