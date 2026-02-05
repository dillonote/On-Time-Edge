import os
import json
import re
from typing import Any, Dict, List, Optional, Literal, Tuple

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

Provider = Literal["template", "ollama", "compatible"]
AssetType = Literal[
    "landing_hero",
    "landing_sections",
    "email_single",
    "email_sequence",
    "linkedin_post",
    "google_search_ad",
    "sales_one_pager",
]

# ----------------------------
# On Time Edge brand defaults
# ----------------------------
DEFAULT_BRAND_PROFILE: Dict[str, Any] = {
    "brand_name": "On Time Edge",
    "tagline": "Advanced planning & scheduling for operations teams",
    "voice": [
        "Plainspoken, ops-smart, confident",
        "Specific over hype",
        "Direct-response structure without gimmicks",
        "Respect skeptical buyers",
    ],
    "audience": [
        "Manufacturing and supply chain leaders",
        "Schedulers, planners, operations teams",
        "RevOps / IT stakeholders supporting operational systems",
    ],
    "positioning": [
        "Make planning and scheduling easier to execute",
        "Turn constraints into an actionable plan",
        "Help teams align daily decisions with operational goals",
    ],
    "do_not_say": [
        "IED-Net",  # per your preference
    ],
    "safe_words": [
        # Use these only when supported by inputs; included as vocabulary hints, not claims:
        "schedule",
        "constraints",
        "capacity",
        "throughput",
        "lead time",
        "service levels",
        "planning",
        "execution",
        "variability",
    ],
}

def load_brand_profile() -> Dict[str, Any]:
    """
    Optionally override defaults with a JSON file path in BRAND_PROFILE_JSON.
    """
    path = os.getenv("BRAND_PROFILE_JSON", "").strip()
    if not path:
        return DEFAULT_BRAND_PROFILE
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    # Minimal merge: override keys present in file
    merged = dict(DEFAULT_BRAND_PROFILE)
    merged.update(obj)
    return merged

# ----------------------------
# Request / response
# ----------------------------
class OTECopyRequest(BaseModel):
    asset_type: AssetType = "landing_hero"

    # Product/offer facts (ONLY these may be claimed)
    offer_name: str = Field(..., description="What are we selling? e.g., 'On Time Edge APS Platform' or 'Demo'")
    target_audience: str = Field(..., description="Who is this for? e.g., 'plant schedulers at mid-market manufacturers'")
    primary_outcome: str = Field(..., description="Outcome they want (no numbers unless true).")

    # Provide only REAL facts you can stand behind:
    key_benefits: List[str]
    capabilities: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(
        default_factory=list,
        description="Verifiable facts: integrations, certifications, customer quotes you own, measured results, etc.",
    )
    objections: List[str] = Field(default_factory=list)

    # Offer details (optional)
    offer_details: str = Field(..., description="What do they get / terms / pricing if applicable.")
    guarantee_or_risk_reversal: Optional[str] = Field(default=None, description="Only if true.")
    cta: str = "Book a demo"

    # Style knobs
    tone: str = "confident, ops-smart, specific"
    length: Literal["short", "medium", "long"] = "medium"

    # Guardrails
    banned_terms: List[str] = Field(default_factory=list, description="Extra terms to forbid in the output.")
    required_phrases: List[str] = Field(default_factory=list, description="Phrases that must appear (if any).")

    # LLM settings (only if provider != template)
    provider: Provider = "template"
    model: str = "llama3.1"
    temperature: float = 0.6

class OTECopyResponse(BaseModel):
    asset_type: AssetType
    content: Dict[str, Any]
    warnings: List[str]
    slippery_score: float

# ----------------------------
# Slippery-slide heuristic score
# ----------------------------
def _sentences(text: str) -> List[str]:
    s = re.split(r'(?<=[.!?])\s+', text.strip())
    return [x.strip() for x in s if x.strip()]

def slippery_score(text: str) -> float:
    sents = _sentences(text)
    if not sents:
        return 0.0
    lengths = [len(re.findall(r"\w+", s)) for s in sents]
    avg_len = sum(lengths) / len(lengths)
    long_penalty = sum(1 for L in lengths if L > 24) / len(lengths)
    very_short_bonus = sum(1 for L in lengths if L <= 10) / len(lengths)

    avg_component = max(0.0, 1.0 - abs(avg_len - 14) / 14)
    mix_component = min(1.0, (very_short_bonus + (1.0 - long_penalty)) / 2.0)
    score = 100.0 * (0.6 * avg_component + 0.4 * mix_component)
    return round(max(0.0, min(100.0, score)), 2)

# ----------------------------
# Guardrail / linting
# ----------------------------
STAT_PATTERN = re.compile(r"(\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*x\b|\b\d+(\.\d+)?\s*(days|hours|weeks|months)\b)", re.I)

def lint_copy(
    text: str,
    brand: Dict[str, Any],
    req: OTECopyRequest,
) -> List[str]:
    warnings: List[str] = []

    # 1) banned terms (brand + request)
    banned = set([t.lower() for t in brand.get("do_not_say", [])] + [t.lower() for t in req.banned_terms])
    for term in banned:
        if term and term in text.lower():
            warnings.append(f"Banned term found: '{term}'")

    # 2) required phrases
    for phrase in req.required_phrases:
        if phrase and phrase.lower() not in text.lower():
            warnings.append(f"Required phrase missing: '{phrase}'")

    # 3) numbers/stats not explicitly supported
    # If the output contains a stat-like token, require it to appear in proof_points.
    output_stats = set(m.group(0) for m in STAT_PATTERN.finditer(text))
    proof_blob = " ".join(req.proof_points).lower()
    for s in output_stats:
        if s.lower() not in proof_blob:
            warnings.append(f"Possible invented stat/number: '{s}' (not found in proof_points)")

    # 4) hard claims language check (soft heuristic)
    risky_phrases = ["guaranteed", "always", "never", "best", "number one", "industry-leading"]
    for rp in risky_phrases:
        if rp in text.lower():
            warnings.append(f"Potentially over-absolute claim detected: '{rp}' (consider softening or adding proof)")

    return warnings

# ----------------------------
# Asset templates (no LLM)
# ----------------------------
def template_landing_hero(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    headline = f"Make {req.primary_outcome} feel predictable."
    subhead = (
        f"{brand['brand_name']} helps {req.target_audience} turn constraints into a plan teams can actually run—"
        f"without adding chaos to your day."
    )
    bullets = [b for b in req.key_benefits[:5]]
    proof = req.proof_points[:3]
    proof_line = f"Proof you can point to: " + " • ".join(proof) if proof else ""
    cta = req.cta

    return {
        "headline": headline,
        "subhead": subhead,
        "bullets": bullets,
        "proof_line": proof_line,
        "cta": cta,
        "cta_secondary": "See how it works",
    }

def template_email_single(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"Quick idea for {req.target_audience}"
    opening = "Let me guess—your plan looks good… right up until real life shows up."
    bridge = (
        f"{brand['brand_name']} is built to keep the schedule usable when constraints shift."
        " The goal isn't a prettier plan. It's a plan your team can execute."
    )
    benefits = "\n".join([f"- {b}" for b in req.key_benefits[:5]])
    proof = "\n".join([f"- {p}" for p in req.proof_points[:4]]) if req.proof_points else ""
    objections = req.objections[:2]
    objection_block = ""
    if objections:
        objection_block = "You might be thinking:\n" + "\n".join([f"- {o}" for o in objections]) + "\n\nFair. That's why we keep it practical."

    close = f"If it's worth it, here's the next step:\n{req.cta}\n\n{req.offer_details}"
    return {
        "subject": subject,
        "body": "\n\n".join([opening, bridge, "Here's what that means in practice:", benefits, "A few real facts:", proof, objection_block, close]).strip(),
    }

def template_linkedin_post(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    hook = "The schedule doesn't fail because your team is careless."
    body = (
        "It fails because the world changes faster than your planning cycle.\n\n"
        "So instead of chasing a perfect plan, build a plan your team can *keep using* when constraints shift.\n\n"
        "A practical checklist:\n"
        "• Identify the constraint that actually governs today\n"
        "• Make tradeoffs explicit (capacity, lead time, service)\n"
        "• Keep the next action obvious\n\n"
        f"That's the problem {brand['brand_name']} is designed to help with—grounded in real operational constraints."
    )
    cta = f"If you want, I can share a quick walkthrough. {req.cta}"
    return {"post": "\n\n".join([hook, body, cta]).strip()}

def generate_template(req: OTECopyRequest, brand: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    if req.asset_type == "landing_hero":
        out = template_landing_hero(req, brand)
        text_for_score = " ".join([str(v) for v in out.values() if isinstance(v, (str, list))])
        return out, text_for_score

    if req.asset_type == "email_single":
        out = template_email_single(req, brand)
        return out, out["body"]

    if req.asset_type == "linkedin_post":
        out = template_linkedin_post(req, brand)
        return out, out["post"]

    # Minimal fallback for other asset types:
    out = {
        "headline": f"{brand['brand_name']}: {req.primary_outcome}",
        "body": "\n".join(req.key_benefits),
        "cta": req.cta,
        "offer_details": req.offer_details,
    }
    text_for_score = " ".join([out.get("headline", ""), out.get("body", ""), out.get("cta", "")])
    return out, text_for_score

# ----------------------------
# LLM prompting
# ----------------------------
def build_system_prompt(brand: Dict[str, Any]) -> str:
    # Strong constraints to keep it factual + brand-safe
    return f"""
You are a direct-response copywriter writing for {brand['brand_name']}.
Voice: {", ".join(brand.get("voice", []))}

Hard rules:
- Use ONLY facts provided in the request fields (benefits/capabilities/proof/offer). Do NOT invent stats, customers, certifications, timelines, integrations, guarantees, or outcomes.
- Do NOT use any banned terms from the brand profile.
- Don't say competitors unless given.
- Avoid hype / absolutes. Prefer specific operational language.

Structure guidance (Sugarman-inspired):
- Make the reader keep reading: short lines, curiosity, one idea per sentence.
- Lead with the concept/outcome, then explain mechanism/capabilities.
- Address 1–3 objections.
- Close with a clear CTA and risk reversal (only if provided).

Return STRICT JSON ONLY (no markdown) matching the required schema for the chosen asset type.
""".strip()

def build_user_prompt(req: OTECopyRequest) -> str:
    # Tell the model exactly what to output for each asset type
    schema_map = {
        "landing_hero": {
            "headline_options": ["string", "string", "string", "string", "string"],
            "subhead": "string",
            "bullets": ["string (5-7 bullets)"],
            "proof_line": "string (empty if no proof_points)",
            "cta": "string",
            "cta_secondary": "string",
            "notes": ["string"],
        },
        "landing_sections": {
            "sections": [
                {
                    "title": "string",
                    "body": "string",
                    "bullets": ["string"],
                }
            ],
            "faq": [{"q": "string", "a": "string"}],
            "cta_block": {"headline": "string", "body": "string", "cta": "string"},
            "notes": ["string"],
        },
        "email_single": {
            "subject_options": ["string", "string", "string", "string", "string"],
            "preview_text": "string",
            "body": "string",
            "ps": "string",
            "notes": ["string"],
        },
        "email_sequence": {
            "emails": [
                {"day": "int", "subject": "string", "preview_text": "string", "body": "string"}
            ],
            "notes": ["string"],
        },
        "linkedin_post": {"post_variants": ["string", "string", "string"], "notes": ["string"]},
        "google_search_ad": {
            "headlines": ["string (max 30 chars)", "… up to 15"],
            "descriptions": ["string (max 90 chars)", "… up to 4"],
            "notes": ["string"],
        },
        "sales_one_pager": {
            "headline": "string",
            "who_its_for": "string",
            "problem": "string",
            "solution": "string",
            "key_benefits": ["string"],
            "capabilities": ["string"],
            "proof": ["string"],
            "cta": "string",
            "notes": ["string"],
        },
    }

    desired_schema = schema_map[req.asset_type]

    payload = {
        "asset_type": req.asset_type,
        "offer_name": req.offer_name,
        "target_audience": req.target_audience,
        "primary_outcome": req.primary_outcome,
        "key_benefits": req.key_benefits,
        "capabilities": req.capabilities,
        "proof_points": req.proof_points,
        "objections": req.objections,
        "offer_details": req.offer_details,
        "guarantee_or_risk_reversal": req.guarantee_or_risk_reversal,
        "cta": req.cta,
        "tone": req.tone,
        "length": req.length,
        "banned_terms": req.banned_terms,
        "required_phrases": req.required_phrases,
    }

    return f"""
Create copy for asset_type="{req.asset_type}".

Return STRICT JSON with this schema:
{json.dumps(desired_schema, ensure_ascii=False, indent=2)}

Use ONLY these facts (do not add new facts):
{json.dumps(payload, ensure_ascii=False, indent=2)}
""".strip()

async def call_ollama(messages: List[Dict[str, str]], model: str, temperature: float) -> str:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    payload = {"model": model, "messages": messages, "options": {"temperature": temperature}, "stream": False}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")

async def call_compatible(messages: List[Dict[str, str]], model: str, temperature: float) -> str:
    base = os.getenv("COMPAT_BASE_URL", "").rstrip("/")
    key = os.getenv("COMPAT_API_KEY", "")
    if not base or not key:
        raise RuntimeError("Missing COMPAT_BASE_URL or COMPAT_API_KEY.")
    url = f"{base}/v1/chat/completions"
    payload = {"model": model, "messages": messages, "temperature": temperature}
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

def parse_json(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except Exception:
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if not m:
            raise ValueError("Model did not return valid JSON.")
        return json.loads(m.group(0))

async def generate_llm(req: OTECopyRequest, brand: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    messages = [
        {"role": "system", "content": build_system_prompt(brand)},
        {"role": "user", "content": build_user_prompt(req)},
    ]

    if req.provider == "ollama":
        content = await call_ollama(messages, req.model, req.temperature)
    else:
        content = await call_compatible(messages, req.model, req.temperature)

    obj = parse_json(content)

    # Build text for scoring
    text_for_score = json.dumps(obj, ensure_ascii=False)
    return obj, text_for_score

# ----------------------------
# API
# ----------------------------
app = FastAPI(title="On Time Edge Copy Bot", version="1.0")

@app.post("/generate", response_model=OTECopyResponse)
async def generate(req: OTECopyRequest):
    brand = load_brand_profile()

    if req.provider == "template":
        copy_obj, score_text = generate_template(req, brand)
    else:
        copy_obj, score_text = await generate_llm(req, brand)

    # Lint all string content we can find
    flat_text = score_text
    warnings = lint_copy(flat_text, brand, req)

    return OTECopyResponse(
        asset_type=req.asset_type,
        content=copy_obj,
        warnings=warnings,
        slippery_score=slippery_score(flat_text),
    )

# ----------------------------
# CLI example
# ----------------------------
if __name__ == "__main__":
    import asyncio

    sample = OTECopyRequest(
        asset_type="landing_hero",
        offer_name="On Time Edge (Demo)",
        target_audience="manufacturing schedulers and operations leaders",
        primary_outcome="a schedule your team can keep using when priorities shift",
        key_benefits=[
            "Reduce rework caused by last-minute changes",
            "Make constraints and tradeoffs visible",
            "Align planning decisions with daily execution",
            "Keep stakeholders on the same page",
            "Move faster without guesswork",
        ],
        capabilities=[
            "Constraint-aware planning inputs",
            "Scenario comparisons",
            "Operational schedule views",
        ],
        proof_points=[
            # Put ONLY what you can verify:
            "Built to support operations planning and scheduling workflows",
        ],
        objections=[
            "We already have a planning tool — adoption is the problem",
            "Our constraints change too often for plans to stay relevant",
        ],
        offer_details="Book a 20-minute walkthrough and we'll map your current workflow to a practical next-step plan.",
        guarantee_or_risk_reversal=None,
        cta="Book a demo",
        provider=os.getenv("PROVIDER", "template"),
        model=os.getenv("MODEL", "llama3.1"),
        temperature=float(os.getenv("TEMP", "0.6")),
    )

    async def run():
        # Call the API function directly for quick local test
        resp = await generate(sample)  # type: ignore
        print(json.dumps(resp.model_dump(), ensure_ascii=False, indent=2))

    asyncio.run(run())
