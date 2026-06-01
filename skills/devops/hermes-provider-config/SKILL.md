---
name: hermes-provider-config
description: "Configure and troubleshoot Hermes LLM providers — LM Studio, OpenRouter fallback, API keys, privacy settings, and gateway caching."
version: 1.0.0
author: Russell
license: MIT
---

# Hermes Provider Configuration

## Trigger

- User asks to configure a new provider (OpenRouter, LM Studio, etc.)
- Setting up fallback providers
- Provider returns errors (401, 404 guardrail, empty responses)
- "Why isn't my fallback working?"
- OpenRouter privacy/guardrail issues

## OpenRouter Fallback Setup

### Steps

1. **Set API key** — both locations matter:
   ```bash
   # config.yaml (top-level model.api_key)
   hermes config set model.api_key "sk-or-..."
   
   # .env file — MUST be uncommented
   # Check: grep 'OPENROUTER_API_KEY' ~/.hermes/.env
   # If commented out with '#', uncomment it
   ```

2. **Set provider-specific key** (top-level key may not propagate):
   ```bash
   hermes config set openrouter.api_key "sk-or-..."
   ```

3. **Configure fallback model:**
   ```bash
   hermes config set fallback_model.provider openrouter
   hermes config set fallback_model.model "openrouter/owl-alpha"  # or other free model
   ```

4. **Clear old `fallback_providers`** (JSON array format conflicts with `fallback_model`):
   ```bash
   hermes config set fallback_providers '[]'
   ```

5. **Lower `min_coding_score`** if using free models (default 0.65 filters them out):
   ```bash
   hermes config set openrouter.min_coding_score 0
   ```

6. **Verify with direct API call** (see references/openrouter-testing.md):
   ```bash
   # Test before trusting hermes -z output
   python3 -c "import urllib.request; ..."  # See references/
   ```

### Known Pitfalls

- **`.env` key commented out** — `# OPENROUTER_API_KEY=...` is inert. Must be uncommented.
- **`min_coding_score` filters free models** — default 0.65 blocks most free tiers. Set to 0.
- **OpenRouter privacy guardrails** — 404 "No endpoints matching guardrail restrictions" means your account's data policy blocks the model. Fix at https://openrouter.ai/settings/privacy (lower privacy level).
- **Top-level key doesn't propagate** — `model.api_key` does NOT automatically populate `openrouter.api_key`. Set both.
- **Gateway caches config** — after changing provider settings, `hermes -z` may still use cached config. Restart gateway or test via direct API call first.
- **`fallback_providers` vs `fallback_model`** — both exist in config. `fallback_providers` is a JSON array, `fallback_model` is a YAML map. Clear `fallback_providers` to avoid conflicts.
- **Cron jobs pin models at creation** — cron jobs do NOT use `fallback_model`. They pin the provider+model specified at creation time. If LM Studio goes down, a cron job pinned to LM Studio will fail even though fallback is configured globally. Fix: set `model: {provider: openrouter, model: "openrouter/owl-alpha"}` when creating cron jobs that need reliability, or use `cronjob action=update` to repin after outages.
- **`hermes env set` and `hermes restart` are NOT valid CLI commands.** Add env vars directly to `~/.hermes/.env` or use `hermes config set` for config changes. Restart via `pkill -f "hermes dashboard" && hermes dashboard ...`.

### Verification

```bash
# Check config is correct
head -10 ~/.hermes/config.yaml
grep -A2 'fallback_model:' ~/.hermes/config.yaml

# Test OpenRouter directly (bypasses gateway cache)
# See references/openrouter-testing.md

# Test fallback triggers when primary is down
# Temporarily point base_url at invalid address, test, then restore
```

### Free Models (as of May 2026)

- `openrouter/owl-alpha` — tested working
- `nvidia/nemotron-3-super-120b-a12b:free` — may require privacy setting adjustment
- Check https://openrouter.ai/models for current free tier availability

## LM Studio Model Catalog Configuration

### Problem
Hermes does NOT dynamically discover models from LM Studio's `/v1/models` endpoint for the slash command dropdown. The model list comes from a predefined catalog configured in `model_catalog.providers`.

### Solution
Add your LM Studio models to the custom provider section:

```yaml
model_catalog:
  providers:
    lmstudio:
      base_url: http://YOUR_IP:1235/v1
      models:
        - qwen/qwen3.6-27b
        - qwen3.5-9b
        - qwen-image-edit-2511
        # ... etc
```

### Steps

1. **Fetch available models from LM Studio:**
   ```bash
   curl http://YOUR_IP:1235/v1/models | python3 -c "import sys,json; [print(m['id']) for m in json.load(sys.stdin)['data']]"
   ```

2. **Update config.yaml** (protected file — use Python or CLI):
   
   **Option A: Using Python:**
   ```python
   import yaml
   with open('~/.hermes/config.yaml') as f:
       cfg = yaml.safe_load(f)
   cfg['model_catalog']['providers']['lmstudio'] = {
       'base_url': 'http://100.110.93.103:1235/v1',
       'models': [
           'qwen/qwen3.6-27b',
           'qwen3.5-9b',
           # ... add all your models
       ]
   }
   with open('~/.hermes/config.yaml', 'w') as f:
       yaml.dump(cfg, f)
   ```

   **Option B: Using CLI:**
   ```bash
   hermes config set model_catalog.providers.lmstudio.base_url "http://100.110.93.103:1235/v1"
   hermes config set model_catalog.providers.lmstudio.models '["model1", "model2"]'
   ```

3. **Fix YAML format** — models must be a proper list, not a stringified JSON array. Use Python's yaml.dump to ensure correct formatting.

4. **Verify syntax:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('~/.hermes/config.yaml')); print('✓ Valid')"
   ```

5. **Restart Hermes** if running:
   ```bash
   pkill -f "hermes dashboard" && hermes dashboard --host 0.0.0.0 --port 9119 --insecure &
   ```

### Known Pitfalls

- **String vs list format** — `models: '[\"a\", \"b\"]'` is WRONG. Must be `models:\n  - a\n  - b`. Use Python yaml.dump to fix.
- **Protected config.yaml** — cannot edit directly via patch. Use Python or CLI.
- **Gateway caching** — after changes, Hermes may still show old models. Restart the dashboard process.
- **Model ID format must match LM Studio API** — use exact IDs from `/v1/models` response (e.g., `qwen/qwen3.6-27b`, not just `qwen3.6-27b`).

### Verification

```bash
# Test that catalog loads correctly
hermes -z "What models are available?"

# Or test direct LM Studio connection
curl http://100.110.93.103:1235/v1/models | head -c 500
```

### References

- `references/lmstudio-model-catalog.md` — LM Studio model catalog configuration guide
- `references/openrouter-testing.md` — Direct API test scripts for verifying provider connectivity
## References

- `references/openrouter-testing.md` — Direct API test scripts for verifying provider connectivity