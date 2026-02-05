# CLAUDE.md — On Time Edge repo guidance

## Goals
- Keep changes small and reviewable.
- Prefer minimal, safe fixes over refactors unless requested.
- Add/adjust tests when behavior changes.

## How to run locally
- Install: `npm install`
- Start dev server: `npm run dev`
- Run tests: `npm test`
- Lint/format: `npm run lint` / `npm run format:check`

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
