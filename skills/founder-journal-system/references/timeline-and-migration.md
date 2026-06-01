# Timeline & Migration Story Reference

## Model Release Timeline (Verified)
- **Late 2022:** OpenAI ChatGPT goes public
- **Early 2023:** Claude (Anthropic) and Gemini (Google) follow
- **Later 2023/2024:** LeChat (Mistral) and Grok (X) arrive
- **Mid-2025:** Cloud orchestration tools (n8n, Make.com, CrewAI) tried to bridge the gap
- **January 2026:** Decision to migrate entirely to local AI
- **April 2026:** {{PERSONAL_ASSISTANT}} + Paperclip deployment
- **May 2026:** Hermes adoption

## Early AI Adoption Story
- Started as a way to unblock myself
- Used for: research new tech, brainstorm product ideas, draft work-related text
- {{USER}} has "absolutely loathed the need for long-form writing" his entire life — AI finally gave him a tool that could alleviate the pain of spending hours composing text
- Quickly stopped being a novelty and became a **daily utility tool**

## Memory/RAG Evolution
- Early cloud models: no memory, required prompt injection every session
- Frontier Labs eventually added memory and RAG facilities
- This was a huge step: "Finally, I had a personalized experience where the AI knew something about me from session to session"
- Still wasn't enough to solve privacy/control concerns

## Migration Motivation
- Cloud APIs still make sense for quick prototypes or specialized models
- For daily operations: needed control over own information
- Privacy was a toggle, not a default
- Sending company data to cloud felt wrong even with training off
- Frontier Labs had no financial incentive to give users control

## Local Harness Journey
1. **{{AI_FRAMEWORK}}:** Open source, good for learning, but drifted after founder joined OpenAI
2. **{{PERSONAL_ASSISTANT}}:** Streamlined but manual (skills, memory, file access all coded from scratch)
   - Paperclip deployed here
   - Hit `llama.cpp`/Ollama friction (Qwen 27B choked, 2 min/response)
   - Learned tools built for one ecosystem won't run openweight models seamlessly
   - Used OpenRouter to keep moving (still part of stack today)
   - Burned $40-50 on Claude/Minimax/DeepSeek just troubleshooting
3. **Hermes:** Local models at full speed, file access built in, Telegram+Discord, self-improving profiles
   - Two hours to port everything and it just worked

## Key Phrasing to Use
- "What I needed then, and still do, is control over my own information."
- "Privacy is not a feature I add later. It is the starting point."
- "Local agentic AI gives me predictability. My {{GPU_MODEL}} does not ask for an API key. My data never leaves my machine."
- Frame frustrations as reflections of that specific moment in time
- Acknowledge AI moves fast (months are years) and Frontier Labs have patched some issues since, but new trade-offs emerge
