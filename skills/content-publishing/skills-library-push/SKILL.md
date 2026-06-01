---
name: skills-library-push
description: Push approved skills to public {{GITHUB_ORG}}/8bit-skills repo with interactive Telegram button approval via clarify tool
category: content-publishing
---

# Push Skills to Public Repo

Push approved skills from staging repo to `{{GITHUB_ORG}}/8bit-skills` (public).

## Workflow

1. Check for skills needing approval:
   ```
   python3 ~/8Bit-Skills-Library/approval_state.py check
   ```

2. For each new/changed skill, use **clarify tool** to ask for approval:
   ```
   clarify(question="Push skill [name] to public repo?", choices=["Approve", "Deny"])
   ```

3. If Approve → confirm skill:
   ```
   python3 ~/8Bit-Skills-Library/approval_state.py confirm <skill_name>
   ```

4. If Deny → block permanently:
   ```
   python3 ~/8Bit-Skills-Library/approval_state.py deny <skill_name>
   ```

5. After all decisions, push confirmed skills:
   ```
   python3 ~/8Bit-Skills-Library/approval_state.py push
   ```

6. Report summary: what was pushed, denied, or skipped.

## Paths

- Staging repo: `~/8Bit-Skills-Library/` (private, `{{GITHUB_USER}}/8Bit-Skills-Library`)
- Public repo: `8bit-arcade` remote → `{{GITHUB_ORG}}/8bit-skills`
- Approval state: `~/.approval-state.json`
- Denied list: `~/.denied-skills.json`

## Notes

- Clarify tool renders native Telegram inline buttons automatically
- Denied skills are remembered permanently
- Always require explicit approval per skill — never auto-push
