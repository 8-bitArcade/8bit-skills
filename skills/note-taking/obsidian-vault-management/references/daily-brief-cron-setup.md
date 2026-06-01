# Daily Brief Cron Job Setup

## Cron Configuration
- Job ID: `f8c7b071db07`
- Schedule: `0 8 * * *` (8:00 AM CEST daily)
- Delivery: `origin,telegram:530910105` (both chat + Telegram)
- Toolsets: `session_search`, `todo`, `terminal`, `file`

## Telegram Delivery Quirk
Setting `deliver: telegram:530910105` alone caused silent failures (job ran, status `ok`, no message delivered). Using `origin,telegram:530910105` (comma-delimited) delivers to both the originating chat AND Telegram reliably.

## Brief Structure
```markdown
# Daily Brief — YYYY-MM-DD
## Yesterday's Highlights
## Completed Tasks
## Outstanding Items
## Today's To-Do
## Open Threads
```

## Obsidian Backup
Brief is also written to `~/.obsidian_vault/Daily Briefs/YYYY-MM-DD.md`.

## Key Notes
- Session history pulled via `session_search` (query: "", sort: "newest", limit: 10)
- Task status checked via `todo` tool
- Brief generated before 8 AM CEST runs
