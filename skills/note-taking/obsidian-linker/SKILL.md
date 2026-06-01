---
name: obsidian-linker
description: Automatically inject [[wikilinks]] into Obsidian notes based on a master entity list.
---

# Obsidian Linker

Automatically adds `[[wikilinks]]` to generated notes to build a connected graph.

## Trigger
- Before saving any note to the Obsidian vault
- Post-processing existing notes

## Workflow
1. Load the Master Link List from `references/link-list.json`
2. Scan the note content for keywords
3. Wrap matches in `[[ ]]` (respecting word boundaries and avoiding double-links)
4. Save the updated note

## Usage
Run the linker script on a specific file:
```bash
python3 ~/.hermes/skills/note-taking/obsidian-linker/scripts/obsidian-linker.py /path/to/note.md
```

Scan entire vault (all .md files):
```bash
find ~/.obsidian_vault/ -name "*.md" -exec python3 ~/.hermes/skills/note-taking/obsidian-linker/scripts/obsidian-linker.py {} \;
```

## Integration
- **Daily Briefs:** Run linker before saving to `~/.obsidian_vault/Calendar/`
- **Session Summaries:** `sync-session-summaries.py` runs linker automatically before syncing pending notes
- **Audio Transcriptions:** Run linker after transcription is saved
- **Founder Journal:** Run linker on weekly drafts
- **Full vault scan:** Run the `find` command above to back-link all existing notes

## Pitfalls
- Avoid linking inside code blocks (``` ... ```)
- **CRITICAL: `link-list.json` entities must be PLAIN TEXT — no `[[` brackets.** The script adds brackets automatically. Running linker on the link list file itself corrupts it. Always exclude `link-list.json` from scans.
- Double-link prevention uses negative lookbehind/lookahead regex. If broken, you'll get quadruple brackets — detect with grep for `[[[[` pattern, clean with Python re.sub
- **Entity expansion**: Scan vault for recurring terms missing from link list using frequency analysis (single-word + capitalized phrases). Add new entities, re-run linker, verify no double brackets
- Case-insensitive matching is preferred
- Don't link common words (e.g., "project", "note", "file")
- Respect user's "dyslexia-friendly" formatting — links should be clear, not cluttered
- Script lives at `~/.hermes/skills/note-taking/obsidian-linker/scripts/obsidian-linker.py` (NOT `~/.hermes/scripts/`)
- After a full vault scan, verify with: `grep -rl '\\[\\[' ~/.obsidian_vault/ --include="*.md" | wc -l` to count linked notes

## Entity Expansion Workflow

Periodically scan vault for recurring terms missing from the link list:

**Single-word frequency scan** (catches lowercase terms like "nemotron", "infrastructure"):
```bash
cd ~/.obsidian_vault && cat *.md */*.md 2>/dev/null | \
  tr '[:upper:]' '[:lower:]' | \
  grep -oP '\b[a-z]{4,}\b' | \
  sort | uniq -c | sort -rn | \
  grep -vP '^(.*\s+(the|and|for|with|from|this|that|were|would|which|there|their|about|could|other|than|then|these|them|some|been|being|have|has|had|his|her|its|our|your|all|can|but|not|get|got|more|most|make|like|long|look|come|know|take|into|over|such|after|before|only|many|way|use|used|using|work|world|also|back|even|just|part|people|think|may|should|will|would|could|did|does|done|going|right|said|same|see|seem|set|shall|she|show|side|since|small|still|such|tell|too|under|up|upon|us|very|want|was|we|well|went|were|what|when|where|which|while|who|why|with|yet|you|your))$' | \
  head -40
```

**Capitalized multi-word phrases** (catches proper nouns like "Daily Brief"):
```bash
grep -roh '[A-Z][a-z]+\s+[A-Z][a-z]+' ~/.obsidian_vault/ --include="*.md" | sort -fi | uniq -ci | sort -rn | head -30
```

**Then:**
1. Filter out already-linked entities and common words
2. Add new entities to `link-list.json` (plain text, no brackets)
3. Re-run linker on vault: `find ~/.obsidian_vault/ -name "*.md" -exec python3 ~/.hermes/skills/note-taking/obsidian-linker/scripts/obsidian-linker.py {} \;`
4. Verify no double brackets: `grep -r '\[\[\[\[' ~/.obsidian_vault/ --include="*.md" | wc -l` should return 0