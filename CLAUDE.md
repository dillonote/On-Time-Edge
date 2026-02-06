# CLAUDE.md — AI-Assisted Development Guidance

## Project Overview

OTE Marketing Copy Generator v2.0 — a FastAPI service that generates brand-safe
marketing copy for On Time Edge using Sugarman direct-response copywriting
principles. Single-file architecture (`main.py`) with six enhancement engines.

## Architecture

- **Single file**: All logic lives in `main.py` for simplicity
- **Three providers**: template (instant, no deps), ollama (local LLM), compatible (API)
- **Six enhancements**: Trigger detection, first-sentence library, auto-objection,
  concept extraction, interactive refinement, A/B variant generation
- **Brand guardrails**: Banned word detection, unsubstantiated claim flagging

## Key Design Decisions

1. Template provider is the default — works without any LLM infrastructure
2. All analysis (triggers, slippery slide, objections, concept) runs locally —
   no LLM needed for analysis, only for generation
3. Brand profile is externalized via JSON env var for easy updates
4. Sugarman's 30 triggers are pattern-matched, not LLM-inferred

## How to run locally

- Install: `pip install -r requirements.txt`
- Start dev server: `uvicorn main:app --reload`
- Run tests: `pytest`
- Lint/format: `ruff check .` / `ruff format --check .`
- Quick CLI test: `python main.py`

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /generate | Generate copy with full analysis |
| POST | /refine | Iteratively refine existing copy |
| POST | /variants | Generate A/B test variants |
| GET | /triggers | List Sugarman's 30 triggers |
| GET | /openers | Browse first-sentence library |
| GET | /objections/{audience} | View audience objections |
| GET | /health | Health check |

## Brand Rules

- Company: On Time Edge
- Banned words: synergy, paradigm, disrupt, revolutionize, game-changer,
  bleeding edge, pivot, circle back
- Tone: Executive-level, direct, credible. Never hype. Use specific numbers.
- Partners: PlanetTogether, Kinaxis, Fuuz, Boomi, 42Q, ZONTAL, Apogean,
  Epicflow, Indeavor

## Code conventions

- Python 3.10+, type hints everywhere
- Pydantic v2 for all request/response models
- Keep everything in main.py unless it gets past ~1500 lines
- Use `textwrap.dedent` for multi-line strings
- Ruff for linting and formatting
- Follow existing patterns in the repo
- Do not introduce new frameworks without asking

## Safety / permissions

- Never print, log, or commit secrets.
- If you need env vars, ask for a sample `.env.example` instead.
- Before touching CI/CD, auth, billing, or data migrations: explain plan + get confirmation.

## PR expectations

- Include: what changed, why, how tested, screenshots (if UI), and any follow-ups.
