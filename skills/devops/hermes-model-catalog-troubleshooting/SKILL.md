---
name: hermes-model-catalog-troubleshooting
description: "Troubleshoot {{LMS}} model catalog issues in Hermes — dropdown not showing models, YAML errors, gateway caching."
version: 1.0.0
author: {{USER}}
license: MIT
---

# Model Catalog Troubleshooting Guide

## Quick Diagnostic Commands

```bash
# Check if config.yaml is valid YAML
python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml')); print('✓ Valid')"

# Verify {{LMS}} provider section exists
grep -A5 'model_catalog:' ~/.hermes/config.yaml | grep -A4 'lmstudio'

# Test direct connection to {{LMS}}
curl http://{{LMS_HOST}}/v1/models | python3 -c "import sys,json; print(f'{len(json.load(sys.stdin)[\"data\"])} models found')"

# Check if lmstudio provider is configured
hermes config get model_catalog.providers.lmstudio.base_url
```

## Common Issues and Fixes

### Issue: Models not showing in slash dropdown

**Cause:** `models` field stored as string instead of YAML list

**Symptoms:**
- Dropdown shows only default models from official catalog
- Your custom {{LMS}} models missing

**Fix:**
```python
import yaml
with open('~/.hermes/config.yaml') as f:
    cfg = yaml.safe_load(f)
cfg['model_catalog']['providers']['lmstudio'] = {
    'base_url': 'http://{{LMS_HOST}}/v1',
    'models': [
        '{{MODEL_LARGE}}',
        '{{MODEL_DEFAULT}}',
        # ... add all models
    ]
}
with open('~/.hermes/config.yaml', 'w') as f:
    yaml.dump(cfg, f)  # This ensures proper list format
```

### Issue: Gateway still shows old models after config change

**Cause:** Hermes cached the model catalog

**Fix:** Restart dashboard process
```bash
pkill -f "hermes dashboard" && hermes dashboard --host 0.0.0.0 --port 9119 --insecure &
```

### Issue: YAML syntax error after manual edit

**Cause:** Invalid YAML format introduced

**Fix:** Rebuild config with Python yaml module (see above)

## Model ID Format Rules

Must match {{LMS}} API `/v1/models` response exactly.

**Correct formats:**
- `{{MODEL_LARGE}}` (with slash prefix)
- `{{MODEL_DEFAULT}}` (no prefix)  
- `mistralai/mistral-7b-instruct-v0.3`

**Incorrect:**
- `qwen3.6-27b` when {{LMS}} returns `{{MODEL_LARGE}}`
- Shortened names not matching API response

## Verification Checklist

After configuration:

- [ ] Config.yaml passes YAML validation (`python3 -c "import yaml; yaml.safe_load(...)"`)
- [ ] `models` field is a proper list (not stringified JSON)
- [ ] Model IDs match exactly what `/v1/models` returns
- [ ] Hermes dashboard restarted after config changes
- [ ] No typos in model IDs or base_url

## References

- `hermes-provider-config` — Full provider configuration skill
- `references/openrouter-testing.md` — API connectivity tests