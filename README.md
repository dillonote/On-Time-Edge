# On Time Edge

A FastAPI service for generating brand-safe marketing copy with built-in guardrails. Supports template-based generation and LLM-powered copy (via Ollama or OpenAI-compatible APIs).

## Prerequisites

- [Python](https://www.python.org/) >= 3.10

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

## Linting & formatting

```bash
ruff check .
ruff format --check .
```

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `BRAND_PROFILE_JSON` | Path to a JSON file that overrides default brand settings | _(uses built-in defaults)_ |
| `OLLAMA_URL` | Ollama API endpoint (when `provider=ollama`) | `http://localhost:11434/api/chat` |
| `COMPAT_BASE_URL` | OpenAI-compatible API base URL (when `provider=compatible`) | _(none)_ |
| `COMPAT_API_KEY` | API key for the compatible provider | _(none)_ |
| `PROVIDER` | Default LLM provider for CLI mode (`template`, `ollama`, `compatible`) | `template` |
| `MODEL` | Model name for LLM providers | `llama3.1` |
| `TEMP` | Temperature for LLM generation | `0.6` |

## Project structure

```
On-Time-Edge/
├── main.py             # FastAPI application and copy generation logic
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── CLAUDE.md           # AI-assisted development guidance
└── README.md           # This file
```

## API usage

### `POST /generate`

Send a JSON body with copy generation parameters. See `OTECopyRequest` in `main.py` for the full schema. Minimal example:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "landing_hero",
    "offer_name": "On Time Edge (Demo)",
    "target_audience": "manufacturing schedulers",
    "primary_outcome": "a schedule your team can keep using",
    "key_benefits": ["Reduce rework", "Make constraints visible"],
    "offer_details": "Book a 20-minute walkthrough.",
    "provider": "template"
  }'
```

## Contributing

1. Create a feature branch from `main`.
2. Keep changes small and focused.
3. Add or update tests when behavior changes.
4. Open a pull request with a clear description of what changed and why.

## License

See [LICENSE](LICENSE) for details.
