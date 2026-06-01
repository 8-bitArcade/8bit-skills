---
name: automated-reporting
description: Generate automated reports, briefings, and status updates. Covers daily briefs, cron job reports, and scheduled summaries.
---

# Automated Reporting

Generate concise automated reports, briefings, and status updates for Russell.

## Trigger
- Creating or modifying cron job prompts for reports
- Drafting daily briefs, status updates, or scheduled summaries
- Any recurring automated communication
- Setting up or troubleshooting Obsidian vault sync

See `references/obsidian-sync-architecture.md` for cron job IDs, sync flow, and model selection.

## Format Rules (user-corrected)

Russell wants briefs detailed enough to be useful but still skimmable. May 28 was 38 lines (too verbose) — then nemotron condensed too much (too brief). Sweet spot: ~25-30 lines with brief context per item.

- **MAX 30 lines total.** Be verbose enough to be useful — include brief context.
- **Keyword phrases + short context.** Expand key items with 1-line detail. Avoid walls of text.
- **One line per item.** No paragraphs.
- **Inline status markers.** Use 🟢🟡🔴 inline, not in separate columns or with legends.
- **Bold emoji headings.** Use **bold** for section labels (e.g. **🔑 TODAY**).
- **No tables.** Bullet lists only.
- **No legends, intros, or filler.** Emojis are self-explanatory.
- **Hard limits.** Max 4 priorities, 4 yesterday items, 3 open threads, 3 actions.
- **Merge duplicates.** If yesterday's item and today's item are the same topic, combine.

## Template

```
📋 [date]

**🔑 TODAY**
1. [keyword phrase with brief context]
2. [keyword phrase with brief context]
3. [keyword phrase with brief context]
4. [keyword phrase with brief context]

**📊 YESTERDAY**
- [item] 🟢/🟡/🔴 (brief detail)
- [item] 🟢/🟡/🔴 (brief detail)
- [item] 🟢/🟡/🔴 (brief detail)
- [item] 🟢/🟡/🔴 (brief detail)

**📌 OPEN**
- [thread] (1-2 line status)
- [thread] (1-2 line status)
- [thread] (1-2 line status)

**📝 DO**
- [action] (why it matters)
- [action] (why it matters)
- [action] (why it matters)
```

**Bold on section labels.** Include brief context per item. Max 30 lines total.

## Obsidian Vault Sync (offline-tolerant)

Reports that write to the Obsidian vault MUST use the local-first sync pattern:

1. Write output to `~/.hermes/session_summaries/YYYY-MM-DD.md` (local pending dir)
2. Run `python3 ~/.hermes/scripts/obsidian-linker.py ~/.hermes/session_summaries/YYYY-MM-DD.md` to inject [[wikilinks]]
3. Run `python3 ~/.hermes/scripts/sync-session-summaries.py` to push to vault
4. If vault is offline (Windows PC down), file stays in pending dir
5. Sync watcher cron job (`5a29c1960f66`) checks every 30min and pushes pending files when vault comes back online

**Never write directly to `~/.obsidian_vault/`** — if the mount drops mid-write, data is lost. Always write locally first, then sync.

## Linking

All notes saved to Obsidian MUST pass through the obsidian-linker script before syncing. This ensures `[[wikilinks]]` are injected automatically.

- Link list lives at `~/.hermes/skills/note-taking/obsidian-linker/references/link-list.json`
- Add new entities to the link list as needed (projects, people, concepts)
- The linker respects code blocks and avoids double-linking

**Session summary cron:** `{{CRON_ID_1}}` (8 AM UK, qwen3.6-27b on {{LMS}} — switched from OpenRouter due to generic "ERROR" responses). Writes daily session summaries to `~/.obsidian_vault/Session Summaries/`.

**Daily brief cron:** `{{CRON_ID_5}}` (8 AM UK, nvidia/nemotron-3-nano-4b). Delivers to Telegram + origin chat. Server timezone is CEST (UTC+2) so cron fires at 09:00 server time = 08:00 UK time year-round (UK and Germany share DST boundaries).

**Cron receipt (proof of receipt):** `{{CRON_ID_4}}` (8:05 AM daily, runs 5 min after daily brief). Status digest of all cron jobs — confirms which ran successfully, which failed. Script: `~/.hermes/scripts/cron-receipt.py`.

## Pitfalls
- **Founder journal system.** Weekly narrative content generation is handled by [founder-journal-system](../founder-journal-system/SKILL.md) — a separate editorial pipeline with human gates. Do NOT conflate daily briefs with founder journal output.
- **Balance conciseness with detail.** User rejected 38-line brief (too verbose) then said nemotron condensed too much (too brief). Target: ~25-30 lines with brief context per item. Enforce 30-line ceiling but don't strip all detail.
- **Nano model ID was wrong.** Cron had `qwen/{{MODEL_FAST}}` but {{LMS}} uses `nvidia/nemotron-3-nano-4b`. Wrong ID causes HTTP 400, not a session_search crash. Nano works fine for cron once the ID is correct.
- **Cron prompt drift.** The daily brief cron prompt (`{{CRON_ID_5}}`) must be updated when format rules change — the skill alone doesn't control cron output.
- **User wants bold on section labels.** Russell requested bold headings (e.g. **🔑 TODAY**) — applied May 27.
- **Timezone is UK (BST/GMT).** Russell is in UK, not Europe/CEST. Cron jobs fire at 09:00 server time = 08:00 UK time year-round (UK and Germany share DST boundaries).
- Don't return "[SILENT]" unless there's genuinely zero content — a brief with empty sections is still worth delivering.
- Obsidian paths: Daily Briefs + Session Summaries → `~/.obsidian_vault/Calendar/`
- Sync script checks mount responsiveness with a test write before syncing — don't skip it
- **Personal context files.** `~/.obsidian_vault/Atlas/IDENTITY.md` and `SOUL.md` are source of truth for Russell's values, decision framework, and identity. Re-read these files periodically to catch user updates. `USER.md` in Hermes memory is a distilled summary — vault files always win on conflicts.
- **File sync timeout.** SSH file sync (`~/.hermes/hermes-agent/tools/environments/ssh.py` line ~261) defaults to 120s timeout. If `~/.hermes` grows large (e.g. 5GB+ venv), tar times out and blocks gateway startup/shutdown + cron jobs. Fix: increase timeout to 600s in the `subprocess.run(...)` call. Long-term: exclude `venv/` from sync via `exclude_paths` in config.
