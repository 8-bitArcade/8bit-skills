---
name: founder-journal-system
description: Curated founder narrative intelligence system. Weekly journal generation from Obsidian vault, session logs, and operational data through a multi-stage editorial pipeline with human gates.
---

# Founder Journal System

Curated founder narrative intelligence system. Transforms raw operational data into high-signal weekly reflections through a staged editorial pipeline.

## Trigger
- Weekly cron execution (Sunday 20:00 UK time)
- Manual invocation for off-cycle drafts
- Any request to analyze weekly themes, generate drafts, or review narrative arcs

## Core Principle

This system produces **selective synthesis** not passive summarization. The goal is "what mattered" not "what happened." Quality threshold > posting consistency.

## Pipeline Architecture (2 Gates)

```
[INPUT: Russell provides topic(s)]
        ↓
Stage 1: Research & Draft → Auto (research, draft, revise, media)
        ↓
Stage 2: Final Editorial → [GATE: Human approves post]
        ↓
Stage 3: Publish → [GATE: Human confirms publish]
```

### Topic Input
Russell provides topics via Telegram/Discord message. Format:
- Single topic: "Write about X"
- Multiple topics: "Topics: 1) X 2) Y 3) Z"
- The agent researches approved data sources for context, then drafts.

### Redraft Workflow
When Russell asks to "retry" or "redraft" a previous post with updated voice:
1. Search session history for the original draft/topic
2. Re-generate using current voice anchors (they may have changed)
3. Do NOT just tweak the old draft — regenerate from scratch with updated voice

### Gate Behavior
- Gates pause execution and deliver draft to Telegram + origin chat
- Include explicit approve/defer instructions
- Backlogging is acceptable when quality threshold not met

### Formatting Rules (Hard)
- **NO em-dashes (—) ever.** They read as corporate polish. Use commas, periods, or restructure.
- **Numbered posts with titles.** Format: `#001 — [Title]`
- **Chronological grounding.** Include rough dates/years (e.g., **2023:**, **Mid-2024:**) to anchor the narrative timeline.
- **Visual structure.** One sentence per line. Short paragraphs. White space is critical for mobile readability.
- **Structural anchors.** Use bold text for dates, thesis statements, or key transitions. Avoid emojis unless they make absolute sense.
- **Fluidity over stop-start.** Prioritize fluid human talk. Use transitional phrases and varied sentence structures. Avoid robotic, choppy, or overly staccato phrasing. Keep paragraphs concise but ensure the narrative flows naturally.
- **Reflective tone.** Frame frustrations as reflections of that specific moment in time. Acknowledge AI moves fast (months are years) and Frontier Labs have patched some issues since, but new trade-offs emerge.
- **Openings:** Do NOT start the post by repeating the title. Start with a hook, personal statement, or direct observation.
- **Closings:** Provide context for callbacks (e.g., "Little by little" needs a full sentence context like "So, little by little, I'm going to start sharing...", never just the phrase alone).
- **GIFs:** Do NOT auto-generate GIFs. Insert a placeholder `[GIF: #NNN pixelated signature]` instead. The user supplies the actual GIF on final review.
- **Links:** Bad for reach. Put in first comment if needed. Keep post self-contained.
- **Cost topic:** Treat API/cloud costs separately in a future journal entry. Do not make it the primary focus unless explicitly requested.
- Hashtags at end (2-4 relevant)
- No corporate jargon

## Data Sources

### Approved Read Sources
- Obsidian vault (approved folders only)
  - `Atlas/` — IDENTITY.md, SOUL.md, me.md (Russell's values, decision framework, identity)
  - `Efforts/Transcript/` — Audio diary transcripts (date-stamped, rich raw material for topics)
  - `Efforts/Brainstorming/`, `Efforts/Research/`, `Efforts/Diary/` — Ideas, notes, reflections
  - `AI OS/` — 8Bit product/tech context
- VPS daily briefs
- Session logs (non-confidential)
- Audio transcripts (approved)
- Planning documentation
- Technical notes
- Brainstorming sessions
- Workflow discussions
- Operational metadata

### Restricted Data (NEVER access, summarize, quote, embed, infer, or publish)
Files or content marked:
- CONFIDENTIAL, PRIVATE, INTERNAL ONLY
- INVESTOR SENSITIVE, LEGAL, FINANCIAL
- SECURITY, PERSONAL

**Heuristic exclusion** (applied when explicit tags absent):
- Skip folders named: private/, personal/, finance/, investor/, legal/
- Skip content containing: specific dollar amounts, investor names, unreleased product details
- When in doubt: exclude entirely

See `references/confidentiality-heuristics.md` for full exclusion logic.

## Editorial Prioritization

### Tier 1 (Priority)
- Major technical discoveries
- Architectural decisions
- AI workflow breakthroughs
- Infrastructure evolution
- Unexpected failures with lessons
- Strategic realizations
- Systems thinking moments
- Future-of-gaming insights
- Agent orchestration lessons
- Scaling challenges
- Workflow experiments
- Product direction shifts
- Meaningful problem-solving

### Tier 2 (Secondary)
- Recurring patterns
- Organizational learning
- Tool evaluations
- Emerging ideas
- Process evolution

### Low Priority (Ignore)
- Repetitive daily tasks
- Maintenance actions
- Routine automation
- Trivial troubleshooting
- Repetitive scheduling
- Ordinary administration
- Generic opinions
- Emotional venting
- Shallow hot takes
- Filler commentary
- Daily updates
- Personal lifestyle content

### Anti-Duplication
Before Stage 1, check `~/.hermes/data/founder-journal/published-topics.json` against candidate topics. Reject topics with >70% semantic overlap to published content within last 8 weeks.
Note: Empty `topics` array means no posts published yet — proceed normally, do not flag as error.

## Narrative Construction Rules (Hard)

- **Strict Chronology:** Always maintain a strict chronological timeline. Do not jump ahead in time. Cover cloud tools and orchestration (n8n, Make.com, CrewAI) *before* discussing local migration or local harnesses ({{FRAMEWORK_NAME}}, {{ASSISTANT_NAME}}, Hermes).
- **AI as Utility First:** Frame early AI adoption as a practical utility tool for research, brainstorming, and drafting. Russell has "absolutely loathed the need for long-form writing" his entire life — AI alleviated the pain of spending hours putting thoughts into text. Set the scene of *how* it was used daily. Do NOT reference dyslexia in every post; it was covered in #001 and is now established.
- **Memory/RAG Evolution:** Acknowledge that while early cloud models lacked memory, the eventual addition of memory and RAG facilities was a huge step toward a personalized experience ("Finally, I had a personalized experience where the AI knew something about me from session to session"), even if it ultimately wasn't enough to solve privacy/control concerns.
- **Model Timeline Reference:** ChatGPT (Late 2022) -> Claude/Gemini (Early 2023) -> LeChat/Grok (Later) -> Orchestration (Mid-2025) -> Local Migration Decision (January 2026) -> Local Harnesses (April/May 2026).
**Model Timeline Reference:** ChatGPT (Late 2022) -> Claude/Gemini (Early 2023) -> LeChat/Grok (Later) -> Orchestration (Mid-2025) -> Local Migration Decision (Spring 2026) -> Local Harnesses (April/May 2026).
- **Migration Motivation:** Clearly set the scene for *why* and *how* the migration from cloud to local happened. Explain the initial discovery, the daily utility phase, the growing friction, and the pivot to local as a natural progression, not a sudden jump.

## Narrative Extraction

Identify across the week:
- Meaningful narrative arcs
- Recurring strategic themes
- Repeated technical friction
- Evolving beliefs
- Significant learning patterns

Compress large volumes of operational activity into:
- A few meaningful insights
- Coherent themes
- High-signal reflections

## Stage 1: Research & Draft (Auto)

**Input:** Russell provides topic(s) via Telegram/Discord.

**Process:**

### 1a. Research & Context Expansion
- Scan approved data sources for context related to the given topic
- Retrieve related discussions, technical notes, session logs
- Identify supporting evidence and personal experiences
- Build narrative framing from Russell's actual work, not generic content

### 1b. Draft Generation
- Generate core narrative (platform-agnostic)
- Include hooks (first 2 lines must grab attention)
- Target length: 100-200 words for LinkedIn (shorter is better)
- **CRITICAL:** Write in Russell's voice (see voice anchors). Short sentences. Direct. Opinionated. No corporate speak. No hedging. No filler.

### 1c. Revision Pass
Self-review for:
- Tone alignment with voice anchors (compare against anchors, not generic "professional" writing)
- **Natural flow check:** Read aloud. Does it sound like Russell speaking, or does it sound robotic/polished? If robotic, rewrite with shorter, more direct sentences.
- Factual accuracy
- Pacing and clarity
- Technical depth
- **Tone check:** Read aloud. Does it sound like Russell wrote it? If not, rewrite.

## Stage 2: Final Editorial

**Checks:**
- Tone verification against voice anchors
- Authenticity review
- Factual consistency check
- Confidentiality scan (full heuristic pass)
- Duplication check against published-topics.json
- Quality scoring (1-10 scale, must be ≥7 to proceed)

**Gate:** Deliver draft + quality score to Russell. Wait for explicit approval.

### 2a. Media Suggestions
- Generate pixelated GIF signature for each post using `scripts/generate_post_gif.py`
- Generate diagrams from scratch (mermaid/timelines) when they support clarity
- Suggest GIF placements (pixelated/retro style for 8Bit brand)
- Media must: support authenticity, improve clarity, remain technically credible
- Media must NOT: generic AI imagery, fake screenshots, over-designed marketing graphics, leak internal architecture

### Stage 3: Publish

Only after explicit human authorization.

**Cross-Platform Adaptation:**
- Core narrative stays consistent
- X/Twitter: 280 chars/tweet, thread structure (hook → body → CTA)
- Instagram: Visual-first, caption 100-200 words, carousel/reels support
- Facebook: Longer posts 100-300 words, discussion prompts, link sharing
- YouTube: Video script + SEO title/description/tags
- TikTok: Raw founder clips, 15-60 sec, trending audio with personal spin
- Discord: Shorter, more conversational
- Telegram: Brief version for personal network

**IMPORTANT:** Adapt tone/format per platform. Never verbatim copy-paste between platforms.

**Post-Publish:**
- Log topic to `published-topics.json` (title, date, tier, key themes)
- Log engagement metrics if available (for future topic weighting)
- Archive draft to `~/.hermes/data/founder-journal/archives/`

## Tone & Voice

**Voice anchor examples** stored in `references/voice-anchors.md` — seed with 5-10 of Russell's best past posts.

**Founder context:** Russell is an introvert who never enjoyed posting. Straight-shooting, literal, struggles with long text. Lots of thoughts, kept to himself. Learning that telling your story matters as a founder. Content is his way of sharing real thoughts without small talk.

**8Bit context:** 8Bit is first and foremost a gaming ecosystem for indie games. We build with agentic services in mind that make sense for our customers and ourselves.

**Privacy/Security stance:** Privacy and control aren't "nice to have" features considered later, but a "default starting point". Acknowledge that early agentic harnesses have been hit and miss around security, we must heed warnings to better implement this liberating technology that is AI.

**Topic teasers:** Use "Expect future posts of my journal to cover..." instead of just "Expect posts covering...".

**Objective:** Authentic founder voice, clear thinking, credible technical insight, reflective intelligence. Sound like someone who'd rather build than talk about building.

**NOT:** Polished corporate writing, viral optimization, controversy bait, motivational content, audience manipulation, "content creator" energy, performative storytelling.

**Long-term goal:** Build trust, intellectual credibility, strategic narrative, and authentic public documentation of the founder journey.

## Quality Control

Optimize for:
- Signal density
- Authenticity
- Clarity
- Insight depth
- Technical credibility
- Long-term narrative consistency

Do NOT optimize for:
- Virality
- Controversy
- Engagement bait
- Motivational content
- Audience manipulation

## Persistence

- Published topics index: `~/.hermes/data/founder-journal/published-topics.json`
- Defer log: `~/.hermes/data/founder-journal/defer-log.md`
- Archives: `~/.hermes/data/founder-journal/archives/`
- Post GIFs: `~/.hermes/data/founder-journal/gifs/`
- Voice anchors: `references/voice-anchors.md`
- Confidentiality rules: `references/confidentiality-heuristics.md`
- Timeline & migration story: `references/timeline-and-migration.md`

## Social Media Integration

### Platform Strategy

Each platform serves a distinct purpose. Content is adapted, not duplicated:

| Platform | Role | Format | Length |
|----------|------|--------|--------|
| X/Twitter | Quick thoughts, threads | Text + GIF | 280 chars/tweet |
| Instagram | Visual storytelling | Photos, carousels, reels | Caption + image |
| Facebook | Community building | Longer posts, links, discussion | 100-300 words |
| YouTube | Deep dives | Video + thumbnails | 3-10 min videos |
| TikTok | Raw authenticity | Short founder clips | 15-60 sec |

**Cross-platform rule:** Same core narrative, adapted tone/length/format per platform. Never verbatim copy-paste.

### X (Twitter) Integration

**Status:** ⚠️ BLOCKED — Auth returns 403 (project error). All 4 creds present in `~/.hermes/.env` (lines 499-502). App "8bit_arcade" project exists but API still rejects. Needs investigation.

**NOTE:** Meta long-lived token expired (user logged out of Facebook). Regenerate via Graph API Explorer before next post.

**IMPORTANT: `x_search` tool ≠ Twitter posting.** The `x_search` tool uses xAI/Grok API credentials (`{{XAI_KEY_VAR}}`), NOT Twitter API v2 credentials. It searches X content but cannot post tweets with Twitter App keys.

**Posting path: Twitter API v2** (chosen by user)
- Requires all 4 creds: `{{TW_API_KEY_VAR}}`, `{{TW_API_SECRET_VAR}}`, `{{TW_ACCESS_TOKEN_VAR}}`, `{{TW_ACCESS_SECRET_VAR}}`
- Authentication: OAuth1 (NOT bearer token). Use `requests_oauthlib.OAuth1`.
- Needs custom posting script — Hermes has no built-in Twitter post tool.
- **Prerequisite:** Keys must be attached to a Project in X Developer Portal → Projects & Apps. Without this, API returns 403 with `client_id: "30620018"` error.
- **Propagation delay:** After creating/linking project, wait 5-10 minutes before testing. X caches project associations.

**X posting requirements:**
- 280 char limit per tweet (threads for longer content)
- Thread structure: hook tweet → body tweets → CTA tweet
- Same formatting rules as core (no em-dashes, bold anchors, short lines)
- Cross-post to Discord/Telegram after X

**Auth verification:** Run `scripts/verify_twitter_auth.py` to test credentials before posting.

**Pitfalls:**
- `hermes env set` and `hermes restart` are NOT valid CLI commands. Add env vars directly to `~/.hermes/.env`.
- Quotes around `.env` values cause parsing issues. Strip quotes.
- `requests_oauthlib` must be installed in Hermes venv (`pip install requests-oauthlib --break-system-packages`).
- Bearer token auth fails on v2 endpoints — always use OAuth1.
- Old tokens issued before project link won't work — regenerate Access Token after attaching app to project.
- **Project linking error persists:** Even after linking, API returns `client_id: "30620018"` (default client ID). May need to create new app INSIDE the project, not separately.

### Meta (Instagram + Facebook) Integration

**Status:** ✅ ACTIVE — Instagram posting works, auto-cross-posts to Facebook Page. Script: `~/.hermes/scripts/post-instagram.py`

**Setup:** Complete. Instagram Business account (`{{IG_HANDLE}}`) linked to Facebook Page (8Bit). Long-lived token stored in `.env`.

**Posting workflow:**
1. Generate post content (image URL required)
2. Run: `POST_CAPTION="..." POST_IMAGE_URL="..." python3 ~/.hermes/scripts/post-instagram.py`
3. Post appears on Instagram + auto-cross-posts to Facebook Page

**Meta API notes:**
- `pages_manage_posts` permission blocked (requires App Review) — using Instagram cross-posting workaround
- Token stored as `{{META_TOKEN_VAR}}` in `.env`
- Token expires ~6 months; regenerate via Graph API Explorer
- See `social-media-publishing/references/meta-token-regen.md` for token refresh steps

**Pitfalls:**
- Instagram posts require images (text-only rejected)
- Token revoked if user logs out of Facebook — regenerate via Graph API Explorer
- Long-lived token exchange can fail in Dev Mode — use original user token if needed

### YouTube Integration

**Status:** 🔲 NOT STARTED

**Setup path:**
1. Google Cloud Console → Create Project
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Web application)
4. Store `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` in `.env`
5. Use `google-auth-oauthlib` for auth

### TikTok Integration

**Status:** 🔲 NOT STARTED

**Setup path:**
1. TikTok for Developers → Create App
2. Apply for Publishing API access (requires 100+ followers, 3+ posts in 180 days)
3. Store `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN` in `.env`

**Pitfall:** TikTok Publishing API has strict eligibility — may need workaround via manual posting + AI-assisted content prep.

## Cron Configuration

- Schedule: Sunday 20:00 UK time (21:00 CEST server time)
- Model: qwen3.6-27b (complex reasoning required)
- Delivery: origin + Telegram
- Enabled toolsets: file, session_search, web (for research), terminal (for data access)

## Pitfalls
- **Robotic tone.** Drafts that feel "too polished" or "robotic" need rewriting. Natural flow > perfect structure. Short, direct sentences that sound like someone actually speaking.
- **No published-topic index = duplication.** Always check before Stage 1.
- **Voice drift without anchors.** Seed voice-anchors.md before first run.
- **Confidentiality heuristics are conservative.** When in doubt, exclude.
- **Em-dashes are banned.** They signal corporate polish, not authentic voice. Use commas or periods.
- **Post numbering required.** Always use `#NNN — [Title]` format.
- **Quality threshold is real.** < 2 Tier-1 topics = defer, not publish weak content.
- **Media from screenshots is dangerous.** Only generate diagrams from scratch or use pixelated GIFs.
- **Cross-platform is adaptation, not rewrite.** Same core narrative, different tone/length.
- **Obsidian vault can be offline.** Use local-first sync pattern for any writes.
- **Word count matters.** 100-200 words max for LinkedIn. Shorter is better.
- **Model selection for drafts.** Use qwen3.6-27b for draft generation — nano model produces too minimal output, {{MODEL_DEFAULT}} times out with longer prompts. 27b is the sweet spot for quality + reliability.
- **Meta Developer UI changes often.** "Add Product" button may be hidden — look for "Add Platform", "Set Up", or direct links. Instagram Graph API requires Business account, not Professional.
- **TikTok Publishing API has eligibility requirements.** 100+ followers, 3+ posts in 180 days, no violations. May need manual posting workaround.
