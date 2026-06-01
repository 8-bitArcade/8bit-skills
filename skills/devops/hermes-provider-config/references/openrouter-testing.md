# OpenRouter Connectivity Testing

## Quick Test Script

Test if OpenRouter API key works and model is accessible:

```python
import json, urllib.request, subprocess

key = subprocess.check_output(
    ['grep', '-o', 'sk-or-[^ ]*', '{{HERMES_CONFIG_PATH}}'],
    text=True
).splitlines()[0]

data = json.dumps({
    'model': 'openrouter/owl-alpha',
    'messages': [{'role': 'user', 'content': 'Say hello'}]
}).encode()

headers = {
    'Authorization': 'Bearer ' + key,
    'Content-Type': 'application/json'
}

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    data=data,
    headers=headers
)

try:
    resp = urllib.request.urlopen(req, timeout=30)
    print(resp.read().decode()[:300])
except urllib.error.HTTPError as e:
    print(f'Error {e.code}: {e.read().decode()[:300]}')
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 "User not found" | Invalid/expired API key | Check key at https://openrouter.ai/keys |
| 404 "No endpoints matching guardrail" | Privacy settings block model | Lower data policy at https://openrouter.ai/settings/privacy |
| Empty response from `hermes -z` | Gateway caching old config | Test via direct API first, then restart gateway |
| 429 rate limit | Free tier exhausted | Wait or switch model |

## Testing Fallback Triggers

To verify fallback activates when primary is down:

1. Save current base_url
2. Set invalid URL: `hermes config set model.base_url "http://127.0.0.1:9999/v1"`
3. Test: `hermes -z "Say hello"`
4. Restore: `hermes config set model.base_url "http://{{LMS_HOST}}/v1"`

Note: Gateway may need restart after config changes for fallback to take effect.
