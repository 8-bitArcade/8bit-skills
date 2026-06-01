# {{LMS}} Whisper API Limitation

**Confirmed:** May 2026

## Finding
{{LMS}} shows `whisper-large-v3` in `/v1/models` but does NOT expose transcription endpoints.

## Tested Endpoints (all failed)
- `POST /v1/audio/transcriptions` → `"Unsupported Media Type. POST requests must use 'application/json'"`
- `POST /v1/audio` → `"Unexpected endpoint or method"`
- Base64 audio in JSON body → Same error

## Root Cause
{{LMS}}'s OpenAI-compatible API only serves:
- Chat completions (`/v1/chat/completions`)
- Model listing (`/v1/models`)
- Embeddings (`/v1/embeddings`)

Audio transcription endpoints are NOT implemented, even when Whisper models are loaded.

## Resolution
Use `openai-whisper` CLI directly on VPS instead. Whisper loads the model locally and processes audio without needing an API endpoint.

## Security Note
User prefers VPS transcription (data stays local) over SSH to Windows PC with {{GPU_MODEL}}, even though GPU would be significantly faster. Privacy > speed.
