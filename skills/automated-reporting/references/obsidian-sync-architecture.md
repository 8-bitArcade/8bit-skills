# Obsidian Vault Sync Architecture

## Cron Jobs

| Job ID | Name | Schedule | Model | Delivery |
|--------|------|----------|-------|----------|
| `f8c7b071db07` | Daily Brief for Russell | 0 8 * * * | nemotron-nano-4b | Telegram + origin |
| `3e98de640cdb` | Daily Session Summary to Obsidian | 0 8 * * * | qwen3.6-27b | local (vault) |
| `5a29c1960f66` | Session Summary Vault Sync Watcher | every 30m | script-only | local |

## Sync Flow

```
Cron generates summary → writes to ~/.hermes/session_summaries/YYYY-MM-DD.md
  ↓
sync-session-summaries.py checks vault mount (test write)
  ↓
  ├─ Mount up → copies file to ~/.obsidian_vault/Session Summaries/, removes pending
  └─ Mount down → file stays in pending dir, watcher retries in 30min
```

## Key Paths

- Pending: `~/.hermes/session_summaries/`
- Vault target: `~/.obsidian_vault/Session Summaries/`
- Daily Briefs: `~/.obsidian_vault/Daily Briefs/`
- Sync script: `~/.hermes/scripts/sync-session-summaries.py`
- Mount script: `~/.hermes/scripts/mount-obsidian-vault.sh`

## Model Selection

- **nemotron-nano-4b**: Fast, for daily briefs (simple session_search queries)
- **qwen3.6-27b**: Reliable, for session summaries (complex session_search + file writes)
- Nano crashes on scroll-mode session_search (`around_message_id` errors) — only use for discovery queries
