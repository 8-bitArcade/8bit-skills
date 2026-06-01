---
name: provider-setup-and-fallback
description: Provider configuration, fallback chains, and troubleshooting for Hermes LLM providers (OpenRouter, {{LMS}}, etc.)
category: software-development
trigger: config, provider, fallback, API key, OpenRouter, {{LMS}}, provider not working, fallback not triggering
---

# Provider Setup & Fallback Configuration

Hermes provider configuration, fallback chains, and common gotchas.

## Quick Checklist

1. Top-level `model.api_key` does NOT cascade into provider-specific blocks — each provider needs its own `api_key` in its section
2. `.env` keys must be uncommented — `# {{OR_API_KEY}}=*** is silently ignored
3. Verify key propagation: `grep 'api_key' ~/.hermes/config.yaml` — provider blocks should show the key, not `''`
4. Test provider directly: `hermes -z "Say hello" --provider <name> -m "<model>"`
5. Check for hidden blockers: `min_coding_score`, privacy/guardrail settings, commented env vars

## Setting Up Fallback

```yaml
# config.yaml
fallback_providers: '[{"provider":"openrouter","model":"nvidia/nemotron-3-super-120b-a12b:free"}]'
fallback_model:
  provider: openrouter
  model: nvidia/nemotron-3-super-120b-a12b:free
```

Then ensure the provider block has the key:
```yaml
openrouter:
  api_key: sk-or-...
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Empty response, exit 0 | Key not in provider block | Set `openrouter.api_key` explicitly |
| 404 "guardrail restrictions" | OpenRouter privacy settings too strict | Adjust at openrouter.ai/settings/privacy |
| Model not found | `min_coding_score` filters it out | Set to 0 for free models |
| Silent failure | `.env` key commented out | Remove `#` prefix |

## Debugging Provider Issues

```bash
# 1. Check key is in provider block
grep -A5 '^openrouter:' ~/.hermes/config.yaml

# 2. Check .env key is active
grep '{{OR_API_KEY}}' ~/.hermes/.env | grep -v '^#'

# 3. Test directly with curl
KEY=$(grep -o 'sk-or-[^ ]*' ~/.hermes/config.yaml | head -1)
curl -s -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/nemotron-3-super-120b-a12b:free","messages":[{"role":"user","content":"Hi"}]}' \
  https://openrouter.ai/api/v1/chat/completions

# 4. Test via hermes CLI
hermes -z "Say hello" --provider openrouter -m "nvidia/nemotron-3-super-120b-a12b:free"
```

## OpenRouter-Specific Notes

- Free models may be blocked by account privacy settings — not a key issue
- `min_coding_score` defaults can filter out free/low-tier models
- Response cache is enabled by default (`response_cache: true`)
- Use `:free` suffix for free tier models

## {{LMS}}-Specific Notes

- Default API key is `lm-studio` (not secret)
- Base URL: `http://<ip>:1235/v1`
- Models must be loaded in {{LMS}} UI before they appear available

## Setting Config Values

```bash
hermes config set openrouter.api_key "sk-or-..."
hermes config set openrouter.min_coding_score 0
hermes config set fallback_providers '[{"provider":"openrouter","model":"..."}]'
```

See `references/openrouter-gotchas.md` for detailed error transcripts and resolution paths.
