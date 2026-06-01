---
name: hermes-lmstudio-catalog
description: "Configure {{LMS}} model catalog in Hermes — add custom models to slash command dropdown."
version: 1.0.0
author: {{USER}}
license: MIT
---

# {{LMS}} Model Catalog Configuration

## Trigger

- Models not showing in Hermes slash command dropdown
- Need to add custom {{LMS}} models to available list
- "Why can't I select my qwen3-coder-30b model?"

## Problem

Hermes does NOT dynamically discover models from {{LMS}}'s `/v1/models` endpoint. The slash command dropdown uses a predefined catalog configured in `model_catalog.providers`.

## Solution

Add your {{LMS}} models to the custom provider section in config.yaml:

```yaml
model_catalog:
  providers:
    lmstudio:
      base_url: http://YOUR_IP:1235/v1
      models:
        - {{MODEL_LARGE}}
        - {{MODEL_DEFAULT}}
        # ... etc
```

## Steps

### 1. Fetch available models from {{LMS}}

```bash
curl http://{{LMS_HOST}}/v1/models | python3 -c "import sys,json; [print(f'  - {m[\"id\"]}') for m in json.load(sys.stdin)['data']]"
```

Expected output:
```
  - {{MODEL_LARGE}}
  - {{MODEL_DEFAULT}}
  - qwen-image-edit-2511
  - qwen/qwen3-vl-30b
  - qwen/qwen2.5-coder-14b
  - qwen/qwen3-coder-30b
  - mistralai/mistral-7b-instruct-v0.3
  - nvidia/nemotron-3-nano-4b
```

### 2. Update config.yaml using Python (recommended)

```python
import yaml

with open('~/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)

cfg['model_catalog']['providers']['lmstudio'] = {
    'base_url': 'http://{{LMS_HOST}}/v1',
    'models': [
        '{{MODEL_LARGE}}',
        '{{MODEL_DEFAULT}}',
        'qwen-image-edit-2511',
        'qwen/qwen3-vl-30b',
        'qwen/qwen2.5-coder-14b',
        'qwen/qwen3-coder-30b',
        'mistralai/mistral-7b-instruct-v0.3',
        'nvidia/nemotron-3-nano-4b',
    ]
}

with open('~/.hermes/config.yaml', 'w') as f:
    yaml.dump(cfg, f)

print('✓ Config updated')
```

### 3. Verify YAML syntax

```bash
python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml')); print('✓ Valid')"
```

### 4. Restart Hermes dashboard (if running)

```bash
pkill -f "hermes dashboard" && hermes dashboard --host 0.0.0.0 --port 9119 --insecure &
```

## Known Pitfalls

- **String vs list format** — `models: '[\"a\", \"b\"]'` is WRONG. Must be proper YAML list with `-` prefixes. Use Python yaml.dump() to fix.
- **Protected config.yaml** — cannot edit via patch command. Must use Python or CLI.
- **Gateway caching** — after changes, Hermes may still show old models. Restart the dashboard process.
- **Model ID format must match {{LMS}} API exactly** — use exact IDs from `/v1/models` response (e.g., `{{MODEL_LARGE}}`, not just `qwen3.6-27b`).

## Verification

```bash
# Test that catalog loads correctly
hermes -z "What models are available?"

# Or test direct {{LMS}} connection
curl http://{{LMS_HOST}}/v1/models | head -c 500
```

## References

- `references/lmstudio-model-catalog.md` — Detailed troubleshooting guide and examples