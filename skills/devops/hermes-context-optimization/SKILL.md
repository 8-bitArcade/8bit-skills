---
name: hermes-context-optimization
description: "Diagnose and reduce Hermes agent context window pressure — config tuning, memory pruning, skill management."
version: 1.0.0
author: Russell
license: MIT
---

# Hermes Context Window Optimization

## Trigger

- User reports context window filling up too quickly
- Sessions hit compaction prematurely
- System prompt feels bloated
- Any conversation about token budget or context efficiency

## Quick Wins (Apply First)

### 0. Per-Job Model Selection for Cron Jobs

Cron jobs run autonomously with no user present — use the smallest capable model to reduce latency, token cost, and context pressure on the main session.

**Pattern:** Assign lightweight models ({{MODEL_FAST}}) to cron jobs that do data gathering, formatting, or simple reporting. Reserve larger models (qwen3.6-27b) for reasoning-heavy tasks.

```python
# Via cronjob API — the CORRECT way
cronjob(action='update', job_id='...', model={'provider': 'lmstudio', 'model': 'qwen/{{MODEL_FAST}}'})
```

**DO NOT** edit `~/.hermes/cron/jobs.json` directly. The file structure is `data['jobs']` (a dict with a 'jobs' key), and the model field expects `{"model": "qwen/...", "provider": "lmstudio"}`. Direct edits can corrupt the format and cause `AttributeError: 'dict' object has no attribute 'lower'` at runtime.

### 1. Memory Trim

Memory is injected into EVERY turn. Keep it lean.

```yaml
# ~/.hermes/config.yaml
memory:
  enabled: true
  max_chars: 2200  # default; reduce if memory is verbose
```

Action: Read `~/.hermes/memories/memory.md` and `~/.hermes/memories/user.md`. Remove stale facts, consolidate entries. Target: under 50% usage.

### 2. Compression Settings

Tune when Hermes auto-compresses conversation history:

```yaml
# ~/.hermes/config.yaml
compression:
  enabled: true
  threshold: 0.40   # compress at 40% usage (default 0.50)
  target: 0.15     # compress down to 15% (default 0.20)
```

Lower threshold = earlier compression. Lower target = more aggressive reduction.

### 3. Hygiene Message Limit

Controls how many messages survive compaction:

```yaml
hygiene:
  max_messages: 300  # default 400
```

### 4. Tool Output Caps

Reduce max output from tools to save context:

```yaml
tools:
  terminal:
    max_output: 30000   # default 50000 (bytes)
    max_lines: 1000     # default 2000
  file:
    max_read: 50000     # default 100000 (chars)
    max_lines: 1000     # default 2000
```

### 5. Skills List Pruning

The skills list is embedded in the system prompt. Each skill adds ~500-1000 chars. Remove unused skills:

```bash
# List skills with sizes
wc -c ~/.hermes/skills/*/SKILL.md

# Remove unused skill
hermes curator delete <skill-name>
# or
rm -rf ~/.hermes/skills/<category>/<skill-name>/
```

Categories to audit: gaming, smart-home, red-teaming, creative (many one-off skills), yuanbao.

## Diagnosis Steps

1. **Measure system prompt size:**
   ```bash
   # Approximate: config + memory + skills list + project context
   wc -c ~/.hermes/config.yaml
   wc -c ~/.hermes/memories/*.md
   find ~/.hermes/skills -name SKILL.md -exec wc -c {} + | tail -1
   # Check project context files (CLAUDE.md, AGENTS.md)
   ```

2. **Check compression config:**
   ```bash
   grep -A5 'compression:' ~/.hermes/config.yaml
   ```

3. **Check memory usage:**
   Look for `MEMORY` percentage in tool responses — Hermes reports usage.

4. **Check skill count vs usage:**
   Many skills are loaded but never triggered. Each unused skill is dead weight.

## Pitfalls

- **Don't over-compress:** Setting threshold too low (below 0.30) means losing recent context that's still relevant.
- **Don't delete skills you actually use:** Audit before removing. Check `~/.hermes/logs/` for skill trigger history if available.
- **Memory vs Skills distinction:** Memory is "who the user is / current state". Skills are "how to do tasks". Don't put procedural knowledge in memory — it's injected every turn.
- **CLAUDE.md bloat:** Project context files are loaded per-session. Keep them under 5KB. Move detailed sections to `docs/` subfiles.
- **Never edit `~/.hermes/cron/jobs.json` directly** — the file structure is `data['jobs']` (dict with 'jobs' key), and model fields expect `{"model": "qwen/...", "provider": "lmstudio"}`. Direct edits corrupt the format causing `AttributeError: 'dict' object has no attribute 'lower'`. Always use `cronjob(action='update')` instead.

## Config Reference

All settings go in `~/.hermes/config.yaml`:

| Setting | Default | Recommended | Effect |
|---------|---------|-------------|--------|
| `compression.threshold` | 0.50 | 0.40 | When to start compressing |
| `compression.target` | 0.20 | 0.15 | How much to compress to |
| `hygiene.max_messages` | 400 | 300 | Messages to retain |
| `tools.terminal.max_output` | 50000 | 30000 | Terminal output cap |
| `tools.file.max_read` | 100000 | 50000 | File read cap |
| `memory.max_chars` | 2200 | 2200 | Memory injection limit |

## Verification

After changes, restart Hermes and check:
1. Context usage percentage in first tool response
2. Compression kicks in at expected threshold
3. Memory is concise and under 50% usage
4. Skills list only includes actively used skills