# Sanitization System Reference — 2026-06-02

## Architecture

```
~/.hermes/skills/          (source — private instances)
        │
        │  rsync -a (to staging)
        ▼
8Bit-Skills-Library/.staging/   (temporary — raw copy)
        │
        │  python3 sanitize.py <staging> <repo_skills>
        ▼
8Bit-Skills-Library/skills/     (sanitized — platform-ready)
        │
        │  git commit (local only — NO auto-push)
        ▼
Human review → "push 8bit skills" → git push origin main
        │
        ▼
GitHub ({{GITHUB_USER}}/8Bit-Skills-Library) — private staging
        │
        │  manual fork via github.com
        ▼
GitHub ({{GITHUB_ORG}}/8bit-skills) — public
```

**Key change (v3+)**: The sync script commits locally but does NOT push. Human must review diff and approve with "push 8bit skills". This prevents unsanitized or broken skills from reaching any remote repo.

## The sanitize.py Script

**Location**: `{{SKILLS_LIBRARY_REPO}}/sanitize.py`

**Usage**: `python3 sanitize.py <source_dir> <dest_dir>`

**Process**:
1. Walk `source_dir` recursively
2. For each file, apply all regex replacements from the `REPLACEMENTS` list
3. Write sanitized content to `dest_dir` (preserving directory structure)
4. Skip binary files (`.pyc`, `.DS_Store`) and `__pycache__` dirs
5. Report: "Sanitized: N files copied, M sanitized, K skipped/binary"

**Skip list**: `__pycache__/`, `*.pyc`, `*.DS_Store`

## REPLACEMENTS List (Priority Order)

All replacements are applied in order per file. Later patterns can build on earlier ones.

### Personal Names & Identifiers
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `{{GITHUB_USER}}` | `{{GITHUB_USER}}` | GitHub username |
| `{{GITHUB_ORG}}` / `{{GITHUB_ORG}}` | `{{GITHUB_ORG}}` | GitHub org |
| `8bit.io` | `{{DOMAIN}}` | Domain |
| `8bit_arcade1` | `{{SOCIAL_HANDLE}}` | Social handle |
| `{{ADMIN_EMAIL}}` | `{{ADMIN_EMAIL}}` | Email |
| `author: {{USER}}` | `author: {{AUTHOR}}` | Skill metadata |
| `Bobby`, `Aidy` | *(removed)* | Family names |

### Infrastructure (Semantic — Platform-Agnostic)
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `{{INFERENCE_HOST_IP}}` | `{{INFERENCE_HOST_IP}}` | Inference host IP |
| `{{AGENT_HOST_IP}}` | `{{AGENT_HOST_IP}}` | agent host ({{AGENT_HOST}}) IP |
| `{{LMS_HOST}}` | `{{LMS_HOST}}` | {{LMS}} host |
| `{{GPU_MODEL}}` | `{{GPU_MODEL}}` | GPU |
| `whisper-large-v3` | `{{WHISPER_MODEL}}` | Whisper model |
| `{{MOBILE_DEVICE}}` | `{{MOBILE_DEVICE}}` | Phone |
| `{{PERSONAL_ASSISTANT}}` | `{{ASSISTANT_NAME}}` | Assistant |
| `{{MESH_VPN}}` | `{{MESH_VPN}}` | Mesh VPN |
| `{{LMS}}` / `LM_Studio` | `{{LMS}}` | LLM server |
| `{{AGENT_HOST}}:` | `{{AGENT_HOST}}` | {{AGENT_HOST}} as agent host ({{AGENT_HOST}}) label |
| `Agent on {{AGENT_HOST}}` | `Agent on {{AGENT_HOST}}` | {{AGENT_HOST}} in prose |
| `{{AGENT_HOST}}` | `{{AGENT_HOST}}` | {{AGENT_HOST}} with article |
| `\bVPS\b` | `{{AGENT_HOST}}` | Any remaining {{AGENT_HOST}} |
| `workstation` | `{{INFERENCE_HOST}}` | Workstation |
| `{{DESKTOP_HOST}}` | `{{DESKTOP_HOST}}` | {{DESKTOP_HOST}} |
| `Windows machine` | `{{DESKTOP_HOST}}` | Windows machine |
| `Windows` (context: desktop) | `{{DESKTOP_OS}}` | Windows OS |

### Personal Names & Identifiers
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `~/.obsidian_vault` | `{{VAULT_MOUNT}}` | Vault mount |
| `~/.hermes/.env` | `{{ENV_PATH}}` | Env file |
| `~/.hermes/config.yaml` | `{{CONFIG_PATH}}` | Config file |
| `~/.hermes/skills/` | `{{HERMES_HOME}}/skills/` | Skills dir |
| `~/.hermes/scripts/` | `{{HERMES_HOME}}/scripts/` | Scripts dir |
| `~/.hermes/data/` | `{{HERMES_HOME}}/data/` | Data dir |
| `~/.hermes/` | `{{HERMES_HOME}}/` | Hermes home |
| `{{WINDOWS_USER_HOME}}/` | `{{WINDOWS_HOME}}/` | Windows home |
| `123@` | `{{WINDOWS_USER}}@` | {{DESKTOP_USER}} |
| `/home/russell/` | `/home/{{USER}}/` | Linux home |

### Models
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `{{MODEL_DEFAULT}}` | `{{MODEL}}` | Primary model |
| `qwen3.6-27b` | `{{MODEL_LARGE}}` | Large model |
| `qwen3-coder-30b` | `{{MODEL_CODE}}` | Code model |
| `{{MODEL_FAST}}` | `{{MODEL_FAST}}` | Fast model |

### Credential Env Var Names
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `{{META_TOKEN_KEY}}` | `{{META_TOKEN_VAR}}` | Meta token |
| `{{TW_API_KEY}}` / `TW_API_KEY` | `{{TW_API_KEY_VAR}}` | Twitter key |
| `{{TW_API_SECRET}}` / `TW_API_SECRET` | `{{TW_API_SECRET_VAR}}` | Twitter secret |
| `UGGC_API_KEY` | `{{UGGC_API_KEY_VAR}}` | UGGC key |
| `FACEBOOK_PAGE_TOKEN` | `{{FB_TOKEN_VAR}}` | FB token |
| `INSTAGRAM_ACCESS_TOKEN` | `{{IG_TOKEN_VAR}}` | IG token |
| `.*_API_KEY` | `{{ENV_VAR_NAME}}` | Any API key |
| `.*_SECRET` | `{{ENV_VAR_NAME}}` | Any secret |
| `.*_TOKEN` | `{{ENV_VAR_NAME}}` | Any token |
| `.*_PASSWORD` | `{{ENV_VAR_NAME}}` | Any password |

### Cron IDs
| Pattern | Replacement | Matches |
|---------|-------------|---------|
| `[0-9a-f]{12}` (cron IDs) | `{{CRON_ID_N}}` | Any 12-char hex ID |

## Verification

After sanitizing, the sync script runs:
```bash
grep -rn "100\.110\|{{GITHUB_USER}}\|8bit\.io\|@8bit_arcade\|META_LONG\|TWITTER_API\|{{USER}}@8bit" skills/
```

Expected: zero matches. If any match, the `REPLACEMENTS` list needs updating for the new pattern.

## Gotchas

- **src≠dst required**: `sanitize.py` does `shutil.rmtree(dst)` before processing. Never call with same source and dest.
- **Order matters**: `~/.hermes/` replacement must come AFTER the more specific paths like `~/.hermes/.env` to avoid double-replacing.
- **Broad catchers like `.*_API_KEY`** are at the BOTTOM of the list. They catch anything not matched by specific patterns above.
- **`author: {{USER}}`** uses `^` anchor (start of line) to avoid matching `{{USER}}` in prose.
- **Template variable false positives**: When checking for remaining private data, patterns like `{{{{XAI_API_KEY}}}}` will match `grep -rn "API_KEY"` but are safe — they're inside `{{}}` delimiters. Always verify matches are NOT already templated.
- **Paperclip is legacy/dead weight** — Hermes replaced Paperclip entirely. Paperclip runs since May 2026 consuming 14GB disk, 288MB RAM, and its own embedded PostgreSQL. Hermes handles messaging, cron, skills, sessions, terminal, LLM access, and memory. Paperclip can be safely stopped and removed to free resources.
