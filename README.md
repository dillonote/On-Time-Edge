# On Time Edge — Marketing Copy Generator v2.0

A FastAPI service for generating brand-safe marketing copy with built-in guardrails and Sugarman direct-response copywriting principles. Supports template-based generation and LLM-powered copy (via Ollama or OpenAI-compatible APIs).

## What's New in v2.0 — Six Sugarman Enhancements

1. **Trigger Detection** — Scans generated copy for Sugarman's 30 psychological triggers (involvement, curiosity, urgency, specificity, etc.) and reports which are present, where, and how strongly.

2. **First-Sentence Library** — 20+ proven opener patterns across five concept types (curiosity, story, contrast, statistic, direct challenge) tuned for manufacturing audiences.

3. **Auto-Objection Detection** — Infers likely buyer objections based on the target audience (VP Ops, COO, Plant Manager, IT Director, Supply Chain Director) and checks whether the copy addresses them.

4. **Concept Extraction** — Identifies the core "big idea" in the copy, scores its strength (0-10), and suggests improvements if weak.

5. **Interactive Refinement** — `POST /refine` endpoint for iterative copy improvement with feedback-driven rewrites.

6. **A/B Variant Generation** — `POST /variants` generates 2-10 copy variants with different opener styles, then compares their trigger counts and slippery-slide scores.

## Prerequisites

* [Python](https://www.python.org/) >= 3.10

## Setup

```bash
# Clone the repository
git clone https://github.com/dillonote/On-Time-Edge.git
cd On-Time-Edge

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Copy the example environment file and fill in your values
cp .env.example .env
```

## Running locally

```bash
# Start the development server (auto-reload)
uvicorn main:app --reload

# Start on a specific port
uvicorn main:app --reload --port 8000

# Quick CLI test (template mode, no server needed)
python main.py
```

## Testing

```bash
pytest
```

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/generate` | Generate copy with full Sugarman analysis |
| `POST` | `/refine` | Iteratively refine existing copy |
| `POST` | `/variants` | Generate A/B test variants |
| `GET` | `/triggers` | List all 30 Sugarman triggers |
| `GET` | `/openers` | Browse first-sentence library |
| `GET` | `/objections/{audience}` | View objections for an audience |
| `GET` | `/health` | Health check |

## API Usage

### `POST /generate`

Generate copy with full analysis:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "email_single",
    "offer_name": "On Time Edge Manufacturing Workshop",
    "target_audience": "VP of Operations",
    "primary_outcome": "measurable scheduling improvement in 12-18 months",
    "key_benefits": ["Reduce rework by 40%", "Make constraints visible"],
    "offer_details": "Book a 20-minute walkthrough.",
    "cta": "Schedule a Workshop",
    "provider": "template"
  }'
```

### `POST /refine`

Iteratively improve copy:

```bash
curl -X POST http://localhost:8000/refine \
  -H "Content-Type: application/json" \
  -d '{
    "original_copy": "We help manufacturers schedule better.",
    "feedback": "Make it more urgent, add a specific dollar amount, open with a question",
    "asset_type": "email_single",
    "target_audience": "COO"
  }'
```

### `POST /variants`

Generate A/B test variants:

```bash
curl -X POST http://localhost:8000/variants \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "email_single",
    "offer_name": "On Time Edge APS Implementation",
    "target_audience": "Plant Manager",
    "primary_outcome": "a schedule that survives contact with reality",
    "key_benefits": ["Reduce rework", "Make constraints visible"],
    "offer_details": "Book a 20-minute walkthrough.",
    "num_variants": 3,
    "provider": "template"
  }'
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROVIDER` | Default LLM provider (`template`, `ollama`, `compatible`) | `template` |
| `MODEL` | Model name for LLM providers | `llama3.1` |
| `TEMP` | Temperature for LLM generation | `0.6` |
| `OLLAMA_URL` | Ollama API endpoint | `http://localhost:11434/api/chat` |
| `COMPAT_BASE_URL` | OpenAI-compatible API base URL | *(none)* |
| `COMPAT_API_KEY` | API key for compatible provider | *(none)* |
| `BRAND_PROFILE_JSON` | Path to custom brand profile JSON | *(built-in defaults)* |

## Project Structure

```
On-Time-Edge/
├── main.py             # FastAPI app + all 6 enhancement engines
├── test_main.py        # Test suite (pytest)
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
├── CLAUDE.md           # AI-assisted development guidance
└── README.md           # This file
```

## Contributing

1. Create a feature branch from `main`.
2. Keep changes small and focused.
3. Add or update tests when behavior changes.
4. Open a pull request with a clear description.
