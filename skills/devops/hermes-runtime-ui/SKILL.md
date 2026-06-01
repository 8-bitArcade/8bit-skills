---
name: hermes-runtime-ui
description: Configure Hermes runtime UI features — context window indicator footer, display settings, and message formatting for Telegram/Discord gateway.
triggers:
  - context window indicator
  - runtime footer
  - show tokens used
  - Hermes UI customization
  - message footer config
---

# Hermes Runtime UI Configuration

Configure visual indicators and display features in Hermes gateway messages.

## Context Window Indicator (runtime_footer)

Shows model name and context usage percentage as a progress bar appended to every agent response.

### Enable in config.yaml

```yaml
runtime_footer:
  enabled: true
  fields:
    - model
    - context_pct
```

Edit via Python (config.yaml is protected):
```python
import yaml
with open('~/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
cfg['runtime_footer'] = {'enabled': True, 'fields': ['model', 'context_pct']}
with open('~/.hermes/config.yaml', 'w') as f:
    yaml.dump(cfg, f)
```

### Customizing the Progress Bar

The footer renders a block-based progress bar with color thresholds. Source: `hermes-agent/gateway/runtime_footer.py`

**Default:** 10 blocks. **Recommended:** 5 blocks for cleaner Telegram/Discord display.

To customize, edit `runtime_footer.py`:
- Block count: modify the number of progress blocks
- Color thresholds: adjust percentage breakpoints (e.g., green <70%, yellow 70-89%, red 90%+)
- Emoji blocks: 🟩🟧🟥 for green/yellow/red states

After editing, restart the gateway:
```bash
systemctl --user restart hermes-gateway.service
# or
pkill -f "hermes-gateway" && hermes gateway
```

### Available Footer Fields

- `model` — current model name
- `context_pct` — context window usage percentage with visual progress bar
- (check source for additional fields)

### Verification

After enabling, check any Telegram/Discord message — the footer appears at the bottom of agent responses. Example:
```
🤖 qwen3.5-9b | Context: 🟩🟩🟩⬜⬜ 42%
```

## Pitfalls

- **Gateway caching** — config changes require gateway restart to take effect
- **Protected config.yaml** — cannot edit directly with patch tool; use Python or CLI
- **Source edits don't survive updates** — custom `runtime_footer.py` changes may be overwritten by `hermes update`. Keep a diff or note your changes.