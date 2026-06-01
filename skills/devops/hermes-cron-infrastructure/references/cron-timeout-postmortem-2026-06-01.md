# Cron Timeout Post-Mortem — 2026-06-01

Three cron jobs failed simultaneously with `RuntimeError: Request timed out` (120s platform limit):

| Job | job_id | Root cause |
|-----|--------|------------|
| System Health Check | `{{CRON_ID_HEALTH_CHECK}}` | Script used `ls` on SSHFS mounts without subprocess timeout → hung on stale FUSE. Also used `hermes cron list --all` which may not exist in the CLI. |
| Session Summary | `{{CRON_ID_SESSION_SUMMARY}}` | `skills: ["automated-reporting"]` injected the full SKILL.md (~300 lines) into the prompt. The self-referential `[SILENT]` instruction in the skill conflicted with the job's delivery requirements. |
| Founder Journal | `{{CRON_ID_FOUNDER_JOURNAL}}` | `skills: ["founder-journal-system"]` injected the full SKILL.md (~300+ lines) into the prompt. {{LMS}} couldn't process the massive prompt within 120s. |

## Fixes applied

1. **Health check script**: Replaced `ls` on mount points with subprocess calls using `timeout=8` per mount. Replaced `hermes cron list --all` with `ps aux | grep cron`.
2. **All agent-driven jobs**: Set `skills: []` (empty) and wrote self-contained prompts with explicit paths and steps.
3. **Health check**: Changed from `no_agent=True` to `no_agent=False` with a tight 5-step agent prompt.

## Lessons (also added to SKILL.md pitfalls)

- `hermes cron list --all` may not be a valid CLI command. Use `ps aux | grep cron` or `cronjob(action="list")` instead.
- `[SILENT]` instructions in skills can conflict with cron job delivery requirements. Never use `[SILENT]` in skills that might be loaded into scheduled jobs.
- When multiple cron jobs fire near-simultaneously on {{LMS}}, they queue and each gets less wall-clock time. Stagger schedules by at least 5 minutes.
