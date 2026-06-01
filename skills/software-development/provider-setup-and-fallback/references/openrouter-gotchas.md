# OpenRouter Configuration Gotchas

## Session: 2026-05-26 — OpenRouter Fallback Setup

### Issue 1: Top-Level API Key Not Propagating to Provider Block

**Symptom:** `openrouter:` block shows `api_key: ''` even though `model.api_key` has the key.

**Root cause:** Top-level `model.api_key` does NOT cascade into provider-specific sections. Each provider block needs its own `api_key`.

**Fix:**
```bash
hermes config set openrouter.api_key "sk-or-..."
```

### Issue 2: `.env` Key Commented Out

**Symptom:** `{{OR_API_KEY_VAR}}` appears in `.env` but is commented out.

**Root cause:** Default `.env` template has `# {{OR_API_KEY_VAR}}=*** — the `#` prefix prevents loading.

**Fix:** Remove the `#` prefix:
```bash
sed -i 's/^# {{OR_API_KEY_VAR}}=/{{OR_API_KEY_VAR}}=/' ~/.hermes/.env
```

### Issue 3: OpenRouter Privacy/Guardrail Settings Block Free Models

**Symptom:** 404 error: `"No endpoints available matching your guardrail restrictions and data policy"`

**Root cause:** OpenRouter account privacy settings are too restrictive. Free models require data retention that conflicts with strict privacy settings.

**Fix:** Visit https://openrouter.ai/settings/privacy and relax data policy settings.

**Note:** This error looks like a "model not found" error but is actually a privacy policy issue. Do NOT assume the model name is wrong.

### Issue 4: `min_coding_score` Filters Out Free Models

**Symptom:** Provider configured, key valid, but free models don't work.

**Root cause:** Default `min_coding_score: 0.65` filters out free/low-tier models.

**Fix:**
```bash
hermes config set openrouter.min_coding_score 0
```

### Verification Commands

```bash
# Check provider block has key
grep -A5 '^openrouter:' ~/.hermes/config.yaml

# Check .env key is active (no # prefix)
grep '{{OR_API_KEY_VAR}}' ~/.hermes/.env | grep -v '^#'

# Test directly with curl
KEY=$(grep -o 'sk-or-[^ ]*' ~/.hermes/config.yaml | head -1)
curl -s -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/nemotron-3-super-120b-a12b:free","messages":[{"role":"user","content":"Hi"}]}' \
  https://openrouter.ai/api/v1/chat/completions

# Test via hermes CLI
hermes -z "Say hello" --provider openrouter -m "nvidia/nemotron-3-super-120b-a12b:free"
```
