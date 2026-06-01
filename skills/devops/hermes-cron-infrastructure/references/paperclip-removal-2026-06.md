# Paperclip Removal — June 2026

## What Was Removed
- `~/.paperclip/` — 14GB (11GB backups, 1.8GB postgres, 284MB logs)
- `paperclip-with-fallback.sh` startup script
- systemd service (stopped + disabled)
- All postgres processes killed

## Why
Paperclip was legacy system running since May 2026. Hermes replaced all functionality:
- Messaging (Telegram, Discord), Cron jobs, Skills, Sessions, Terminal, LLM access, Memory

## Impact
- Freed 14GB disk, 288MB RAM, 3463 CPU seconds
- Ports 3100 and 54329 released
- {{AGENT_HOST}} disk dropped from 90% to 60%

## Verification
```bash
ls ~/.paperclip 2>/dev/null && echo "Still exists" || echo "Gone"
ps aux | grep -i paperclip | grep -v grep  # Should return nothing
```

## Lessons
- Legacy systems accumulate resources silently
- Health checks should monitor for orphaned processes
- Hermes is sole agent — no fallback to Paperclip needed
