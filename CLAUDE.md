# CLAUDE.md — On Time Edge repo guidance

## Goals
- Keep changes small and reviewable.
- Prefer minimal, safe fixes over refactors unless requested.
- Add/adjust tests when behavior changes.

## How to run locally
- Install: `pip install -r requirements.txt`
- Start dev server: `uvicorn main:app --reload`
- Run tests: `pytest`
- Lint/format: `ruff check .` / `ruff format --check .`
- Quick CLI test: `python main.py`

## Code conventions
- Follow existing patterns in the repo.
- Do not introduce new frameworks without asking.
- Match formatting and naming used nearby.

## Safety / permissions
- Never print, log, or commit secrets.
- If you need env vars, ask for a sample `.env.example` instead.
- Before touching CI/CD, auth, billing, or data migrations: explain plan + get confirmation.

## PR expectations
- Include: what changed, why, how tested, screenshots (if UI), and any follow-ups.
