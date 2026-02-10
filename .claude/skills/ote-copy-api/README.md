# OTE Copy Generation Robot — Installation Guide

This robot generates brand-safe marketing copy for On Time Edge using Sugarman's direct-response principles.

## Option 1: Claude Code CLI Skill (localhost API)

**Best for**: Using Claude Code CLI with your local API running

### Installation
The skill is already installed globally at `~/.claude/skills/ote-copy-api/`

### Usage
1. Start your API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. In Claude Code CLI, invoke the skill:
   ```
   /ote-copy-api
   ```

3. Claude will prompt you for inputs and call your local API

**Pros**: Uses your actual API with full functionality
**Cons**: Only works when API is running locally

---

## Option 2: Claude Chat Project (No API Required)

**Best for**: Using claude.ai (web) without running the API

### Installation
1. Go to https://claude.ai
2. Navigate to **Projects** → **Create Project**
3. Name it **"OTE Copy Generator"**
4. Click **Add Content** → **Upload** → Select `/home/user/On-Time-Edge/.claude/CLAUDE_CHAT_INSTRUCTIONS.md`
5. Start a new conversation in that project

### Usage
In the project chat, use this prompt template:

```
Generate OTE copy for:
- Asset type: landing_hero
- Audience: VP Manufacturing at mid-market CPG companies
- Outcome: Book discovery call
- Key benefit: Reduce firefighting with real-time constraint visibility
- Proof point: 1000+ implementations, 90-day time-to-value
- Main objection: "We've tried APS before and it failed"
```

Claude will generate copy using the embedded knowledge (brand profile, 30 Sugarman triggers, objections, etc.)

**Pros**: Works anywhere, no API needed, full brand knowledge embedded
**Cons**: Doesn't use your actual API (but has all the logic built-in)

---

## Asset Types Supported

- `landing_hero` — Hero section for landing pages
- `landing_sections` — Body sections for landing pages
- `email_single` — Single promotional email
- `email_sequence` — Multi-part nurture sequence
- `linkedin_post` — LinkedIn thought leadership
- `google_search_ad` — Google Search ad copy
- `sales_one_pager` — PDF/print one-sheet

---

## Key Features in Both Options

✅ **Sugarman's 30 triggers** — Automatically detected and explained
✅ **Slippery slide analysis** — Each sentence pulls to the next
✅ **Brand guardrails** — Banned words (synergy, paradigm, IED-Net) flagged
✅ **Unsubstantiated claims** — Warns about unsourced stats
✅ **Objection library** — Addresses common audience concerns
✅ **Concept extraction** — Key operational keywords identified
✅ **First-sentence library** — Proven high-converting openers

---

## Files

- `SKILL.md` — Claude Code CLI skill definition (for local API)
- `CLAUDE_CHAT_INSTRUCTIONS.md` — Full knowledge base for Claude Chat projects
- `README.md` — This file

---

## Which Should You Use?

| Scenario | Recommended Option |
|----------|-------------------|
| Working in terminal with API running | Option 1 (CLI Skill) |
| Quick copy generation on the go | Option 2 (Claude Chat) |
| Testing API changes | Option 1 (CLI Skill) |
| Sharing with non-technical team | Option 2 (Claude Chat) |
| Mobile/tablet copy generation | Option 2 (Claude Chat) |

Both options produce the same quality output — Claude Chat just doesn't call your actual API.
