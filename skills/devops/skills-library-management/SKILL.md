---
name: skills-library-management
description: "Manage and sync agent skills to the 8Bit Skills Library — a GitHub repo of production-ready, platform-grade skills for 8bit-ai.com. Covers skill creation, library sync, bundling filters, and library structure."
version: 1.0.0
author: {{USER}}
license: MIT
---

# Skills Library Management

Manage the 8Bit Skills Library — a curated collection of production-ready agent skills published to GitHub for the 8Bit AI platform.

## Trigger

- Creating a new skill that should be published to the library
- Updating an existing skill that's already in the library
- Running the sync script manually or debugging sync failures
- Reviewing the skill library for quality, overlap, or gaps
- Setting up the library on a fresh {{AGENT_HOST}}

## Library Overview

**Repo**: `{{GITHUB_USER}}/8Bit-Skills-Library` (private on GitHub)
**Auto-sync**: Weekly Monday at 08:00 CEST via Hermes cron (job `85b2e195887e`)
**Sync script**: `{{SKILLS_LIBRARY_REPO}}/sync-skills-repo.sh`

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
   bash {{SKILLS_LIBRARY_REPO}}/sync-skills-repo.sh
   ```

5. Verify on GitHub

## Running the Sync Manually

```bash
cd {{SKILLS_LIBRARY_REPO}}
bash sync-skills-repo.sh
```

The script (v3+ with sanitization + human approval gate):
1. Reads `~/.hermes/skills/.bundled_manifest` to exclude bundled skills
2. Copies each skill to a **staging directory** (`$REPO_DIR/.staging/`) via `rsync -a`
3. Runs `sanitize.py <staging> <repo_skills_dir>` to replace all private data with `{{TEMPLATE}}` variables
4. Cleans staging directory
5. Auto-generates `README.md` with skill list + template variable documentation
6. **Commits locally but does NOT push** — writes `.pending-push` flag file
7. Outputs diff summary for human review

**Human approval required**: The cron job reports "PUSH READY" with diff stats. {{USER}} must reply "push 8bit skills" to push to the personal staging repo. This is intentional — no auto-push to any remote.

**Critical**: The sanitizer MUST be called with separate staging and destination directories. Calling `sanitize.py <dir> <same-dir>` causes `shutil.rmtree(dst)` to delete everything before processing. Always use the staging dir pattern.

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
6. **License**: MIT recommended for maximum adoption
7. **`.gitignore`**: Must exclude `__pycache__/`, `*.pyc`, `.env`, `*.key`, `.DS_Store`, `.vscode/`, `.idea/`

## Publishing to Public Repo

**Public repo**: `8-bitArcade/8bit-skills` on GitHub
**License**: MIT (maximum adoption + attribution)
**`.gitignore`**: Auto-included by sync script (excludes pycache, env, keys, OS files)
**Architecture**: Personal repo as staging → manual fork to org via GitHub web UI
**Note**: Hermes is sole agent — skills reference Hermes only, not Paperclip (removed June 2026)

### Human-in-the-Loop Approval Workflow

**CRITICAL**: No skill is pushed without explicit confirmation from {{USER}}.

**Two-phase flow** (cron cannot use `clarify` — no user present):

**Phase 1 — Weekly cron** (Monday 08:00, job `85b2e195887e`):
1. Runs `sync-skills-repo.sh` → sanitizes, commits locally, writes `.pending-push`
2. Reports diff summary to {{USER}} via Telegram
3. Tells {{USER}} to reply "push" to start approvals

**Phase 2 — Interactive session** (triggered when {{USER}} replies "push"):
1. Agent loads `approval_state.py check` to find new/changed skills
2. Uses `clarify` tool for each skill: `clarify(question="Push skill [name]?", choices=["Approve", "Deny"])`
3. **Approve** → skill confirmed for push
4. **Deny** → skill added to `.denied-skills.json` → never asked again
5. After all decisions, `approval-state.py push` pushes confirmed skills

**Denied skills are permanent** — once denied, never asked again. To re-enable, manually remove from `.denied-skills.json`.

**Why not inline keyboards?** Hermes' Telegram adapter intercepts ALL callback queries. It only processes callbacks with specific prefixes (`ea:`, `sc:`, `cl:`, `mp:`, `gt:`). Custom callback data gets eaten by the catch-all. The `clarify` tool is the native Hermes solution — it renders Telegram buttons automatically with the right callback prefix.

## Sanitization Pipeline

All skills are sanitized before syncing to strip instance-specific/private data and replace with `{{VARIABLE}}` templates.

**Sanitizer**: `sanitize.py` in the repo root. Processes all files in the staging directory.

### Platform-Agnostic Design Principle

Skills must work whether the user runs on a {{AGENT_HOST}}, local machine, cloud VM, or hybrid setup. This means:

1. **Private data** (IPs, paths, names) → replaced with `{{TEMPLATE}}` variables
2. **Semantic deployment terms** ({{AGENT_HOST}}, workstation, {{DESKTOP_HOST}}) → also replaced with `{{TEMPLATE}}` variables so the user customizes their topology
3. **Template variables use semantic names** (`{{AGENT_HOST}}`, `{{INFERENCE_HOST}}`, `{{DESKTOP_HOST}}`) not environment-specific names (`{{{{AGENT_HOST}}}}`, `{{WORKSTATION}}`)

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{AGENT_HOST}}` | Where the agent runs ({{AGENT_HOST}}, local, cloud) | {{AGENT_HOST}} |
| `{{AGENT_HOST_IP}}` | agent host ({{AGENT_HOST}}) IP | `203.0.113.50` |
| `{{INFERENCE_HOST}}` | Where inference runs (workstation, local GPU, cloud API) | workstation |
| `{{INFERENCE_HOST_IP}}` | Inference host IP | `192.168.1.100` |
| `{{DESKTOP_HOST}}` | Desktop/laptop machine | {{DESKTOP_HOST}} |
| `{{DESKTOP_USER}}` | Desktop machine username | `youruser` |
| `{{LMS_HOST}}` | LLM server host:port | `192.168.1.100:1234` |
| `{{LMS}}` | LLM server name | {{LMS}} |
| `{{VAULT_MOUNT}}` | Vault sync/mount method (SSHFS, syncthing, local path) | `~/.obsidian_vault` |
| `{{VAULT_PATH}}` | Vault filesystem path | `/home/user/Documents/AI_Vault` |
| `{{USER}}` | Server Linux username | `{{USER}}` |
| `{{GPU_MODEL}}` | GPU model for inference | {{GPU_MODEL}} |
| `{{MOBILE_DEVICE}}` | Mobile device name | `{{MOBILE_DEVICE}}` |
| `{{DOMAIN}}` | Your domain | `example.com` |
| `{{ADMIN_EMAIL}}` | Admin email | `admin@example.com` |
| `{{GITHUB_USER}}` | GitHub username | `yourname` |
| `{{GITHUB_ORG}}` | GitHub organization | `yourorg` |
| `{{AUTHOR}}` | Skill author name | `{{USER}}` |
| `{{VPN_TOOL}}` | VPN/mesh tool | `{{MESH_VPN}}` |
| `{{MESH_VPN}}` | Mesh VPN tool (synonym) | `{{MESH_VPN}}` |
| `{{ASSISTANT_NAME}}` | Assistant name | `Ash` |
| `{{CRON_ID_N}}` | Cron job ID (per-job) | `abc123def456` |
| `{{ENV_VAR_NAME}}` | Environment variable name | `{{META_TOKEN_KEY}}` |
| `{{REMOTE_MOUNT_TOOL}}` | Remote mount tool ({{REMOTE_MOUNT_TOOL}}, rclone) | `{{REMOTE_MOUNT_TOOL}}` |
| `{{TUNNEL_PORT}}` | SSH tunnel port | `3000` |

### Semantic Replacement Examples

The sanitizer replaces not just private data but deployment-specific terms:

| Source Text | Sanitized |
|---|---|
| `{{AGENT_HOST}}:` | `{{AGENT_HOST}}` |
| `Agent on {{AGENT_HOST}}` | `Agent on {{AGENT_HOST}}` |
| `workstation` | `{{INFERENCE_HOST}}` |
| `{{DESKTOP_HOST}}` | `{{DESKTOP_HOST}}` |
| `{{VAULT_MOUNT}}` | `{{VAULT_MOUNT}}` |
| `{{INFERENCE_HOST_IP}}` | `{{INFERENCE_HOST_IP}}` |
| `{{USER}}` | `{{USER}}` |

This way, a user running everything on one machine sets `{{AGENT_HOST}}` = "my laptop" and the skill reads naturally, while a {{AGENT_HOST}}+workstation user sets `{{AGENT_HOST}}` = "my {{AGENT_HOST}}" and `{{INFERENCE_HOST}}` = "my desktop".

## Pitfalls

- **Cron cannot use `clarify`** — cron jobs run with no user present, so `clarify` buttons won't work. The weekly cron syncs+commits locally and reports. User replies "push" to trigger a separate interactive session that handles approvals with `clarify`.
- **Hermes Telegram adapter eats custom callbacks** — inline keyboard callback data must match Hermes prefixes (`ea:`, `sc:`, `cl:`, `mp:`, `gt:`) or gets discarded. Use `clarify` tool for button interactions — it handles the callback routing automatically.
- **Don't edit `sync-skills-repo.sh` without testing** — a broken script means no sync
- **CRITICAL: `sanitize.py` src must differ from dst** — calling `sanitize.py <dir> <same-dir>` causes `shutil.rmtree(dst)` to delete everything. Always use staging dir: copy to staging, sanitize staging→repo, then delete staging.
- **The glob pattern in README generation** must handle both flat skills and category skills (`skills/*/` and `skills/*/*/`)
- **`__pycache__` and `*.pyc`** are excluded from sync — don't accidentally include them in the library
- **The `.bundled_manifest` uses plugin package names**, not skill directory names. User skills like `automated-reporting` are NOT in the manifest even if they sound like bundled features.
- **GitHub org transfer requires web UI** — `gh api repos/{owner}/{repo}/transfer -f new_owner=Org` returns HTTP 422 when the authenticated user lacks org create-repo permission. `gh repo fork OWNER/REPO --org OrgName` returns HTTP 403 for the same reason. Both fail from {{AGENT_HOST}} SSH tokens. **Workaround**: owner must go to repo page → Fork button → select target org, OR repo Settings → Danger Zone → Transfer ownership on github.com. No CLI/API workaround exists for tokens without org admin rights.
- **Personal repo as staging, org fork as public** — the recommended architecture: develop and sanitize in the personal repo (`{{GITHUB_USER}}/8Bit-Skills-Library`), then **fork** to the org (`{{GITHUB_ORG}}/8bit-skills` or similar) for public-facing distribution. The sync script auto-syncs to the personal repo (after human approval); the org fork is a manual one-time action via GitHub web UI.
- **No auto-push** — the sync script (v3+) commits locally but does NOT push to any remote. Human must review diff and approve with "push 8bit skills". This prevents unsanitized or broken skills from reaching the repo.
- **Approval via `clarify` tool** — interactive session uses `clarify(question="Push skill [name]?", choices=["Approve", "Deny"])` for each skill. Denied skills are blocked permanently in `.denied-skills.json`.
- **Moving a repo from personal to org after creation** — plan ahead: if the repo should live in the org, either (a) have an org owner create it empty first, then push, or (b) use the web UI fork/transfer.
- **Don't store secrets** in skill files. The repo should be shareable. Use `{{TEMPLATE}}` placeholders for all instance-specific values.
- **`author: {{USER}}` in SKILL.md frontmatter** — the sanitizer replaces this with `{{AUTHOR}}`. If you see `author: {{USER}}` in a repo skill file, it means the sanitizer missed it (it was added after the last sanitize run).

## References

- `references/github-repo-setup.md` — repo URL, fresh-{{AGENT_HOST}} setup, current skill count
- `references/sanitization-system.md` — full sanitizer architecture, `REPLACEMENTS` list, template variables, verification commands
- `templates/skill-template.md` — canonical SKILL.md scaffold for new skills

## Verification

After adding or updating a skill:
1. Run sync: `bash sync-skills-repo.sh`
2. Check GitHub shows the updated skill
3. Verify README includes the skill in the listing
4. Confirm no secrets were committed (check `git diff` before first push)
