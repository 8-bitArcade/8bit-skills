# Confidentiality Heuristics

## Purpose
Define exclusion rules for sensitive content. Applied during Stage 1 (intelligence scan) and Stage 3 (final editorial pass).

## Explicit Tags (Hard Block)
If content contains any of these markers, exclude entirely:
- CONFIDENTIAL
- PRIVATE
- INTERNAL ONLY
- INVESTOR SENSITIVE
- LEGAL
- FINANCIAL
- SECURITY
- PERSONAL

## Folder Exclusion (Path-Based)
Skip these Obsidian vault paths entirely:
- private/
- personal/
- finance/
- investor/
- legal/
- security/
- Any folder with "confidential" or "private" in name

## Content Heuristics (Pattern-Based)
Exclude content containing:
- Specific dollar amounts (e.g., "£50,000", "$10k")
- Investor names or contact details
- Unreleased product feature names or specs
- Employee compensation details
- Legal case references
- Security vulnerability details
- API keys, tokens, credentials
- Internal infrastructure passwords or secrets

## Contextual Exceptions
Allowed when explicitly approved by Russell:
- Public company metrics (revenue ranges, user counts already published)
- Previously disclosed technical architecture
- Open-source project details
- Public blog post content

## Uncertainty Rule
When sensitivity is unclear:
1. Exclude the material
2. Log the exclusion in defer-log.md
3. Flag for manual review if topic seems high-value

## Scan Implementation
During Stage 1:
```
1. Read file/folder path
2. Check against folder exclusion list
3. Scan content for explicit tags
4. Scan content for pattern-based triggers
5. If any match: skip and log
6. If no match: include in intelligence summary
```

During Stage 3:
```
1. Full re-scan of draft content
2. Check for accidental inference from restricted sources
3. Verify no restricted data leaked through paraphrasing
4. Quality-gate fails if confidentiality violation detected
```

## Logging
All exclusions logged to `~/.hermes/data/founder-journal/defer-log.md` with:
- Source path
- Exclusion reason
- Date
- Whether flagged for manual review
