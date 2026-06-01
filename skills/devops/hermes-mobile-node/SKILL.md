---
name: hermes-mobile-node
description: "Design and deploy a mobile AI inference node (phone) that acts as failover for a {{AGENT_HOST}}+workstation setup. Covers health endpoints, cron relay routing, model management, and Termux deployment."
version: 1.0.0
author: {{USER}}
license: MIT
---

# Hermes Mobile Node

Build a phone into an AI inference failover device. When the workstation is offline, the phone picks up cron jobs and conversational workloads via local LLM inference.

## Trigger

- Setting up a mobile phone as an AI inference node
- Building health endpoints for workstation availability detection
- Routing cron jobs between {{AGENT_HOST}}, workstation, and mobile
- Optimizing `llama.cpp` inference on Android/Termux
- Managing model loading/unloading on a RAM-constrained mobile device

## Architecture

```
Telegram/Discord → {{AGENT_HOST}} Hermes → Workstation ({{LMS}}, primary, tier 1)
                              → Phone (llama.cpp, failover, tier 2)
                              → OpenRouter (cloud API, ultimate fallback, tier 3)
```

- {{AGENT_HOST}} is the single entry point for all messaging. No split agents.
- Phone runs `llama.cpp` via Termux for local inference.
- Health endpoint on {{AGENT_HOST}} tells phone whether to run locally or defer.
- Cron relay on {{AGENT_HOST}} routes jobs across three tiers: workstation → mobile → OpenRouter.
- OpenRouter API key is read from `~/.hermes/config.yaml` (not env) when running as standalone script.

## Execution Rules

- **Build the minimal working version first.** Get one model loading and responding before optimizing.
- **Phone scripts go in `~/.hermes/scripts/mobile-node/`** — ready to `scp` to the phone.
- **Always test the health endpoint** after any {{AGENT_HOST}} restart: `curl -s http://localhost:9191/mobile`
- **Test cron relay** after changes: `python3 ~/.hermes/scripts/cron_relay.py --check`
- **Workstation-only jobs must be explicitly listed** in `WORKSTATION_ONLY_JOBS` in `cron_relay.py`. Everything else is assumed mobile-compatible.
- **When workstation is offline**, the health endpoint returns `run_local: true`. No separate "offline mode" flag.

## SSH Backend Constraint (Critical)

The Hermes SSH backend **intercepts all shell-level backgrounding**: `&`, `nohup`, `disown`, `setsid`, `daemon=true`. Background processes started via these methods are killed immediately.

`terminal(background=True)` also **does not work** for long-lived blocking servers (`serve_forever()`, `while True` loops). The Hermes wrapper kills the process because it never returns. This was confirmed empirically — the process starts but exits within seconds with no output.

**Reliable daemonization: Use `screen`:**

```bash
screen -dmS <name> <command>
```

To check: `screen -ls`
To attach: `screen -r <name>`
To kill: `screen -X -S <name> quit`
To restart: kill then re-launch.

**For auto-restart after reboot**, add to crontab:
```bash
@reboot sleep 30 && screen -dmS <name> <command>
```

**Do NOT use** `terminal(background=True)` for long-lived servers — the wrapper kills `serve_forever()`-style blocking calls. Only use it for bounded tasks (builds, tests) with `notify_on_complete=True`.

## Health Endpoint Design

The health endpoint runs on the **{{AGENT_HOST}}** (not the workstation). It polls the workstation via {{MESH_VPN}} status and `curl` to {{LMS}}. Returns two views:

- `/health` — full diagnostics (workstation {{MESH_VPN_CMD}} + {{LMS}} + {{AGENT_HOST}} disk/memory/load)
- `/mobile` — minimal decision for phone: `{"run_local": true/false, "workstation_online": false, "timestamp": "..."}`

Phone should call `/mobile` (not `/health`) to minimize data usage.

## Cron Relay Routing Logic (Three-Tier)

1. Check workstation health via `http://localhost:9191/mobile`
2. **Tier 1:** Workstation online → run job normally on {{AGENT_HOST}}
3. **Tier 2:** Workstation offline → look up phone in {{MESH_VPN}} (`{{MESH_VPN_CMD}} status --json`, match hostname containing "nubia"/"z70" or OS == "android")
   - Phone found → forward job to phone via `http://<tailscale_ip>:9192/cron/trigger` (2000-char context limit)
   - Phone fails → log and fall through to tier 3
4. **Tier 3:** Both local + mobile unreachable → call OpenRouter API (`https://openrouter.ai/api/v1/chat/completions`, model `openrouter/auto`)
   - Reads API key from `~/.hermes/config.yaml` if `{{OR_API_KEY}}` env var is not set
   - Includes system prompt noting no Hermes tool access (files, session_search unavailable)
5. **All tiers failed** → log failure, job is dropped and retried on next cron cycle

Workstation-only jobs (Daily Brief, Session Summary, Atlas Sync, Founder Journal, Health Check) are NOT skipped when workstation is offline — they fall through to mobile (best-effort) then OpenRouter (context-only). Only skipped if all three tiers fail.

## Model Manager

The phone needs a model manager because RAM is finite (24GB shared with OS). Load models on demand, unload when idle:

- **Default model**: Nemotron 3 4B (fast, for cron/classification)
- **Heavy model**: Qwen 9B Q5 (conversation/reasoning)
- **Context windows**: 4096 for conversation, 2048 for cron tasks
- **GPU**: Snapdragon Adreno 830 via Vulkan — build `llama.cpp` with `-DGGML_VULKAN=1`
- **Threads**: 6 on Snapdragon 8 Elite (leave 2 for OS)

**Speed estimates (Snapdragon 8 Elite, Vulkan):**
- Nemotron 4B (Q4): ~30-50 tok/s
- Qwen 9B Q5: ~15-30 tok/s
- Full precision: ~40-60% slower, not recommended for production use

## Pitfalls

- **SSH backgrounding blocked** — use `screen`, never `&`, `nohup`, `setsid`, or `daemon=true`. `terminal(background=True)` also fails for blocking servers. Confirmed: `serve_forever()` processes die silently.
- **Termux battery optimization** — Android kills background processes. Whitelist Termux in battery settings before deploying.
- **AIOS (Nubia ROM) may restrict Termux** — test `termux-setup-storage` and process persistence early
- **{{MESH_VPN}} IP changes** — mobile uses DHCP within {{MESH_VPN}} network. Cron relay resolves IP dynamically from `{{MESH_VPN_CMD}} status --json`, never hardcode
- **Workstation offline ≠ sleep** — if workstation is truly off {{MESH_VPN}} (not just asleep), last_seen timestamp will be hours old. Use {{MESH_VPN}} `online` field, not just `last_seen`
- **Model GGUFs are large** — download over WiFi, not mobile data. Use a download script that validates SHA256.
- **OpenRouter key not in {{AGENT_HOST}} env** — Hermes config has the key but standalone Python scripts can't see Hermes env. The `cron_relay.py` script reads the key from `~/.hermes/config.yaml` directly. Don't rely on `{{OR_API_KEY}}` env var on {{AGENT_HOST}}.

## Verification

1. Health endpoint: `curl -s http://localhost:9191/mobile | python3 -m json.tool`
2. Cron relay: `python3 ~/.hermes/scripts/cron_relay.py --check`
3. Screen sessions: `screen -ls` should show `hermes-health`
4. After phone joins {{MESH_VPN}}: `{{MESH_VPN_CMD}} status --json` shows phone hostname/IP

## Reference Files

- `scripts/workstation_health.py` — Health endpoint ({{AGENT_HOST}}). Run via `screen -dmS hermes-health python3 ... --serve`
- `scripts/cron_relay.py` — Three-tier cron routing ({{AGENT_HOST}}). Run via `python3 ... --check` to test
- `scripts/hermes_mobile.py` — Mobile service scaffold (phone/Termux). Run via `python3 ... --daemon`
- `scripts/mobile_model_manager.sh` — Model loader/unloader (phone/Termux)
- `references/phase1-termux-setup.md` — Phase 1 Termux setup steps (phone-side)
- `references/inference-optimization.md` — llama.cpp build flags and tuning for Snapdragon 8 Elite

## Related Skills

- `hermes-cron-infrastructure` — cron job creation, health monitoring, SSHFS patterns
- `hermes-provider-config` — model catalog, {{LMS}} configuration