---
name: agent-efficiency-audit
description: Audit and review the efficiency of the Hermes agent setup — cron jobs, skills, model selection, context usage, and workflows. Run ad-hoc or via cron.
---

# Agent Efficiency Audit

Audit the agentic setup for waste, misconfiguration, and optimization opportunities.

## Trigger
- User requests an efficiency review
- Run monthly via cron (recommended)
- After adding/removing skills or cron jobs
- When context window pressure increases or jobs start timing out

## Methodology

Run each check below. Collect evidence, then score and summarize.

### 1. Cron Job Audit

Pull live cron data:
```
hermes cron list
```

Evaluate:
- **Agent-driven jobs that should be `no_agent: true`** — any job with a `script` field that also has a prompt/toolsets but not `no_agent: true`. These waste tokens and risk timeout.
- **Schedule overlap** — jobs firing at the same time causing resource contention.
- **Over-frequency** — daily jobs that could be weekly, hourly that could be every-6h.
- **Error loops** — jobs with `last_status: "error"` that keep retrying and burning tokens.
- **Delivery waste** — `origin` + explicit duplicate telegram target.
- **Disabled jobs still scheduled** — stale entries.
- **Health check agent timeouts** — agent-driven health checks that exceed the timeout lose the script's output entirely. Flag any health check job where the agent prompt allows open-ended investigation. The agent should only: parse JSON → report or fix → done.

### 2. Skill Audit

List all skills:
```
ls ~/.hermes/skills/
```

Evaluate:
- **Unused skills** — skills with no cron or recent session references. Check via `session_search` for skill names.
- **Overlapping coverage** — two skills that do the same thing.
- **Missing coverage** — recurring tasks handled inline that should be skills.
- **Pinned but stale** — pinned skills that haven't been updated despite issue fixes.

### 3. Model Right-Sizing

Review each cron job's model assignment:

| Task Complexity | Appropriate Model |
|---|---|
| Simple/status/formatting | {{MODEL_FAST}} |
| Standard reports/briefs | nemotron-3-nano-4b or qwq-32b (openrouter) |
| Complex analysis/research | qwen3.6-27b |
| Code-heavy tasks | qwen3-coder-30b |

Flag:
- Jobs using a complex model for a simple task (waste)
- Jobs using a simple model for a complex task (quality risk)
- OpenRouter fallback jobs when {{LMS}} model is available (latency + cost)

### 4. Context Window Pressure

Check for:
- **Large files injected on every run** — AGENTS.md / CLAUDE.md / .cursorrules size
- **Cascading tool calls** — one tool output feeding 3+ more tool calls
- **Unbounded session_search** — no limit parameter, pulling entire transcripts
- **Heredocs / large prompts** in cron jobs

### 5. Backup & Recovery Completeness

Verify:
- Config backup script runs and pushes to GitHub
- Cron job definitions are backed up
- Skills directory is backed up
- Memories are backed up
- **8Bit Skills Library** syncs daily to `{{GITHUB_USER}}/8Bit-Skills-Library` (check last commit age)
- Test restore process is documented

### 6. Health Check Scope

Verify the health check script covers:
- Disk, memory, load ✓
- SSHFS mounts ✓
- {{LMS}} reachability ✓
- Cron error status ✓
- **Missing:** Backup repo last push age, pending session summary count

## Scoring

Rate each area 1-5:
- 5 = optimal, no changes needed
- 4 = minor tweaks possible
- 3 = moderate waste identified
- 2 = significant issues, action needed
- 1 = broken or severely wasteful

## Output Format

```
📊 EFFICIENCY AUDIT — [date]

**⏰ CRON JOBS** [score]/5
- [finding]
- [finding]

**🧩 SKILLS** [score]/5
- [finding]

**🧠 MODEL SIZING** [score]/5
- [finding]

**📏 CONTEXT** [score]/5
- [finding]

**💾 BACKUPS** [score]/5
- [finding]

**🏥 HEALTH CHECK** [score]/5
- [finding]

**⚡ TOP ACTIONS**
1. [highest impact fix]
2. [next fix]
3. [next fix]

Overall: [average]/5
```

## Pitfalls
- Scores without evidence are worthless — always cite specific cron IDs, skill names, file paths
- Don't recommend deleting skills immediately — ping user first
- Missing backup for cron definitions is a known gap, flag it every time
- Check `no_agent` flag before flagging agent-driven timeout risk
- Don't score on a curve — a 3 means there's genuine waste
