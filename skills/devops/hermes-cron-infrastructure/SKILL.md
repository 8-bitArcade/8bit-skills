---
name: hermes-cron-infrastructure
description: "Maintain, debug, and create Hermes cron jobs and their supporting scripts — including SSHFS timeout handling and health monitoring."
version: 1.0.0
author: {{USER}}
license: MIT
---

# Hermes Cron Infrastructure

Maintain, debug, and create Hermes cron jobs and their supporting scripts.

## Trigger

- Creating, updating, or troubleshooting cron jobs
- Scripts timing out, hanging, or failing silently
- SSHFS mount issues in cron scripts
- Health monitoring of the Hermes agent system

## SSHFS Timeout Pattern (Critical)

**Problem:** `os.listdir()`, `os.stat()`, and other blocking syscalls on SSHFS/FUSE mounts hang indefinitely when the remote is slow or unresponsive. Python's `signal.alarm()` does NOT interrupt blocked FUSE syscalls.

**Fix:** Run filesystem operations in a subprocess with a hard timeout.

### Pattern: Helper Script + Timeout Wrapper

1. **Create a helper script** that does the actual filesystem work and outputs JSON:

```python
#!/usr/bin/env python3
# urecorder-list.py
import os, sys, json
path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/urecorder/")
try:
    entries = os.listdir(path)
except OSError as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
result = []
for fname in sorted(entries):
    if not fname.endswith('.m4a'):
        continue
    try:
        result.append({"name": fname, "mtime": os.path.getmtime(os.path.join(path, fname))})
    except OSError:
        pass
print(json.dumps(result))
```

2. **Call it from the main script** with a timeout:

```python
import subprocess, sys, json

LISTDIR_TIMEOUT = 30  # seconds

def scan_with_timeout(path):
    try:
        result = subprocess.run(
            [sys.executable, "helper-script.py", path],
            capture_output=True, text=True, timeout=LISTDIR_TIMEOUT
        )
        return json.loads(result.stdout) if result.returncode == 0 else []
    except subprocess.TimeoutExpired:
        print("Timeout — SSHFS mount may be stale")
        sys.exit(0)
```

### Why This Works

- Subprocess timeout kills the child process, unblocking the parent
- JSON output handles filenames with spaces/parens safely (no shell interpolation issues)
- Helper script runs in its own process — no shared state corruption

## Cron Job Best Practices

- **no_agent scripts:** Always set explicit timeouts. Default cron timeout is 120s.
- **Silent on success:** Scripts should output nothing when healthy. Only report issues or new items.
- **State files:** Persist scan state to `~/.hermes/cron_state/` to avoid reprocessing.
- **Model selection:** Agent-driven jobs need an explicit `model` set. Use qwen3.6-27b for reasoning, nano-4b for simple tasks.
- **Toolsets:** Restrict `enabled_toolsets` to what the job actually needs to reduce token overhead. A health check that only runs a script and reads output needs only `["terminal"]`. Don't load `["terminal", "file", "cronjob", "web"]` unless the job actually uses web searches.
- **Frequency:** Match check frequency to expected change rate. Audio files = weekly. System health = daily.

## Health Check System

A daily health check runs at 06:00 (`health-check.py` + agent prompt). Monitors:
- Disk usage (alert > 85%)
- Memory usage (alert > 90%)
- SSHFS mount responsiveness
- {{LMS}} connectivity
- Cron job error count
- **Legacy process cleanup** — Paperclip removed June 2026. If Paperclip processes appear, kill and remove.

The agent prompt auto-fixes: stale mounts (remount via `mount-obsidian-vault.sh`), cron bugs (fix scripts).

**Infrastructure note:** Hermes is sole agent system. Paperclip (legacy) removed — freed 14GB disk, 288MB RAM, 3463 CPU seconds.

**Critical: Keep the agent prompt TIGHT.** The script does the detection — the agent should only:
1. Parse the JSON result
2. If all healthy → report "all clear" and exit
3. If issues found → apply the specific fix (remount, restart, etc.) → verify → report

No open-ended investigation chains. No "let me also check X" tangents. Agent-driven health checks that exceed the timeout will fail the entire job and lose the script's output.

**Backup before fixes:** Before modifying ANY files, scripts, or config, create timestamped backup:
```bash
cp -r ~/.hermes/scripts ~/.hermes/scripts.backup.$(date +%Y%m%d_%H%M%S)
```
This is non-negotiable — user requirement for safety net on auto-fixes.

## SSH Backgrounding Constraint (Critical)

The Hermes SSH backend **intercepts all shell-level backgrounding**: `&`, `nohup`, `disown`, `setsid`, and `terminal(background=True)`. These all fail silently or get killed immediately.

**Reliable daemonization:** Always use `screen`:

```bash
screen -dmS <name> <command>
```

Check: `screen -ls` | Attach: `screen -r <name>` | Kill: `screen -X -S <name> quit`

Apply this to any long-lived process: health endpoints, model servers, watchers.

## Pitfalls

See `references/cron-timeout-postmortem-2026-06-01.md` for a real-world case study of 3 simultaneous cron failures and the fixes applied.
See `references/paperclip-removal-2026-06.md` for legacy system cleanup (freed 14GB disk, 288MB RAM).

- **SSHFS mounts become stale after {{AGENT_HOST}} reboot** — cron jobs depending on them will hang without subprocess timeouts
- **`signal.alarm()` doesn't work for FUSE syscalls** — only subprocess timeouts do
- **Filenames with spaces/parens** break with f-string shell interpolation — use JSON helpers instead
- **Agent-driven cron jobs without `model` set** will fail silently
- **Never edit `~/.hermes/cron/jobs.json` directly** — always use `cronjob(action='update')`
- **Agent-driven health checks can timeout even when the script is fine** — the LLM agent's reasoning about results has its own time cost. Keep agent prompts for health checks TIGHT: script runs → agent gets JSON result → agent reports or fixes → done. No open-ended investigation chains. If the job consistently times out, convert to `no_agent: true` with the script delivering its own summary.
- **SSH backgrounding is blocked** — use `screen -dmS`, never `&`, `nohup`, `setsid`, or `daemon=true`
- **`no_agent=True` with `enabled_toolsets` set is contradictory** — when `no_agent=True`, the script IS the job and the prompt + toolsets are completely ignored. If you want agent-driven jobs (e.g., "run script, then analyze and report"), set `no_agent: false` (default) and keep toolsets.
- **Skill injection into cron prompts causes timeouts** — attaching a skill via `skills: ["some-skill"]` injects the full SKILL.md into the prompt. For jobs running on {{LMS}} with a 120s timeout, a 300-line SKILL.md + a long prompt will time out. Always prefer `skills: []` (empty) and write a self-contained prompt with explicit paths and steps. **Real case (2026-06-01)**: Weekly Agent Efficiency Audit, Daily Session Summary, and Founder Journal Weekly all failed simultaneously because each had a skill attached. Removing the skill attachment and writing focused 4-6 step prompts fixed all three.
- **`gh repo transfer` / org API transfer requires org create-repo permission** — `gh api repos/{owner}/{repo}/transfer -f new_owner=Org` returns 422 if the authenticated user can't create repos in the target org. The only reliable path is GitHub web UI: repo Settings → Danger Zone → Transfer ownership.
- **`hermes cron list --all` may not be a valid CLI command** — use `cronjob(action="list")` API or `ps aux | grep cron` to verify cron processes instead of shelling out to CLI commands that may not exist.
- **Stagger concurrent cron jobs on {{LMS}}** — when multiple agent-driven cron jobs fire near-simultaneously, they queue behind each other on the inference server. Each job gets less wall-clock time and may timeout. Stagger schedules by at least 5 minutes for jobs running on the same {{LMS}} instance.
- **`gh repo fork --org` also fails with org permission errors** — `gh repo fork OWNER/REPO --org OrgName` returns HTTP 403 when {{AGENT_HOST}} token lacks org admin rights, same as `gh api repos/{owner}/{repo}/transfer`. The only reliable path to move skills to an org is manual fork via GitHub web UI. Document this blocker in the skills-library-management skill.
- **`[SILENT]` instructions in skills conflict with cron delivery** — skills that contain `[SILENT]` or similar suppression instructions will conflict with cron jobs that need to deliver results. Never use `[SILENT]` in skills that might be loaded as cron job skills.

## Verification

After creating or fixing a cron script:
1. Test manually: `python3 ~/.hermes/scripts/<script>.py`
2. Check it completes within timeout: `timeout 30 python3 ~/.hermes/scripts/<script>.py`
3. Verify cron job runs: `hermes cron list --all`
4. Watch for next scheduled run in logs
