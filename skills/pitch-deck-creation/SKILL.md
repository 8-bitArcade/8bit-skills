---
name: pitch-deck-creation
description: Create investor-facing pitch decks tailored to specific programs, accelerators, or investor audiences
triggers:
  - pitch deck
  - investor deck
  - program application
  - accelerator deck
  - investor materials
---

# Pitch Deck Creation

Create investor-facing pitch decks tailored to specific programs, accelerators, or investor audiences.

## Triggers
- User asks for a pitch deck, investor deck, program application deck, or investor materials
- User shares advisor feedback or program guidelines for a deck
- User needs to reposition existing deck for a new audience

## Approach

1. **Gather context first** — read project files, READMEs, Obsidian vault notes, existing deck content. Never write a deck from memory alone. Search for project structure, tech details, traction metrics.
2. **Cross-reference master deck** — if a master investor deck exists, extract and align team bios, traction metrics, roadmap milestones, market data, and funding status. Do NOT invent team members, bios, or metrics.
3. **Identify audience** — what program/investor is this for? Load any program guidelines or advisor feedback provided.
4. **Map slides to audience requirements** — each program has different expectations. NVIDIA wants AI/GPU focus. YC wants traction. VCs want team + market.
5. **Clarify built vs planned** — explicitly mark what is shipped vs roadmap. Programs like NVIDIA accept "planned" for future GPU workloads, but ambiguity hurts credibility.
6. **Write slide-by-slide** — self-contained slides with clear labels. Target 10-12 slides unless audience specifies otherwise.
7. **Position strategically** — lead with what the audience cares about. Secondary narratives (blockchain, Web3, community) go to appendix unless core to current traction.

## General Slide Structure

Cover → Company Overview → Problem → Solution → Product/Tech → Market → Traction → Business Model → Team → Roadmap → Ask

Adjust order based on audience (see below).

## Audience-Specific Adjustments

- **NVIDIA programs:** Dedicated AI/ML focus slide, GPU infrastructure slide, explicit NVIDIA strategic fit. Position as "AI infrastructure enabling creators", not Web3/GameFi. See `references/nvidia-guidelines.md` for full NVIDIA expectations.
- **YC/accelerators:** Traction first, team second, product third. Less tech detail, more growth narrative.
- **VC investors:** Market size (TAM/SAM/SOM), defensible moat, clear path to revenue, team credibility.
- **Grant programs:** Mission alignment, social impact, technical innovation, sustainability.

## Output Format

Markdown file with `## SLIDE N: Title` headers, ready to drop into Canva/Google Slides/Pitch. Include appendix for secondary narratives. File saved to user's project directory.

## Pitfalls

- Don't lead with buzzwords without substance. Every claim needs a concrete detail (model names, GPU specs, user counts).
- Don't invent team members, bios, traction metrics, or roadmap dates. Cross-reference the master deck or ask the user.
- Don't mix cleanup with new content — write the deck first, then refine.
- Don't over-explain tech to non-technical audiences. Match depth to reviewer.
- Blockchain/Web3 positioning is a liability for AI-focused programs. Move to appendix.
- "Planned" is acceptable for programs like NVIDIA — future GPU plans count as strategic fit.
- Reduce emphasis on anything the audience doesn't care about (e.g., community features for tech programs, marketing for grants).
- Always clarify what is BUILT vs PLANNED. Ambiguity here destroys credibility with technical reviewers.

## References
- NVIDIA program guidelines: `references/nvidia-guidelines.md`
