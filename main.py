import os
import json
import re
from typing import Any, Dict, List, Optional, Literal, Tuple

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

from consciousness import build_consciousness

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
    "tagline": "Navigate transformation and drive sustainable business value for manufacturing operations",
    "identity": (
        "On Time Edge is a vendor-agnostic manufacturing digital transformation consulting "
        "and implementation firm—not a software product. They help manufacturers select, "
        "implement, integrate, and optimize APS, MES, OEE, and supply chain systems."
    ),
    "voice": [
        "Plainspoken, ops-smart, confident",
        "Specific over hype—use operational language (constraints, throughput, lead time), not buzzwords",
        "Direct-response structure without gimmicks",
        "Respect skeptical buyers—they've heard every vendor pitch",
        "Consultative, not salesy—trusted advisor, not product pusher",
    ],
    "audience": [
        "Manufacturing and supply chain executives",
        "Plant schedulers, planners, and operations leaders",
        "RevOps / IT stakeholders supporting operational systems",
        "Industries: aerospace, automotive, CPG, food & beverage, medical device, metals, pharma, plastics",
    ],
    "positioning": [
        "Vendor-agnostic: pick the right tool for each client, not push one platform",
        "30+ years of APS implementation specialization, 1000+ site implementations across 300+ global companies",
        "90-day time-to-first-value implementation targets",
        "MDIF (Manufacturing Digital Interoperability Framework): proprietary methodology from strategy through execution",
        "Post-implementation partnership—not a build-and-walk-away consultancy",
        "Turn constraints into an actionable plan teams can execute",
    ],
    "do_not_say": [
        "IED-Net",
    ],
    "safe_words": [
        # Use only when supported by inputs; vocabulary hints, not claims:
        "schedule",
        "constraints",
        "capacity",
        "throughput",
        "lead time",
        "service levels",
        "planning",
        "execution",
        "variability",
        "digital transformation",
        "interoperability",
        "vendor-agnostic",
        "time-to-value",
        "integration",
        "MES",
        "OEE",
        "ERP",
        "what-if",
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
    offer_name: str = Field(
        ...,
        description="What are we selling? e.g., 'On Time Edge APS Platform' or 'Demo'",
    )
    target_audience: str = Field(
        ...,
        description="Who is this for? e.g., 'plant schedulers at mid-market manufacturers'",
    )
    primary_outcome: str = Field(
        ..., description="Outcome they want (no numbers unless true)."
    )

    # Provide only REAL facts you can stand behind:
    key_benefits: List[str]
    capabilities: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(
        default_factory=list,
        description="Verifiable facts: integrations, certifications, customer quotes you own, measured results, etc.",
    )
    objections: List[str] = Field(default_factory=list)

    # Offer details (optional)
    offer_details: str = Field(
        ..., description="What do they get / terms / pricing if applicable."
    )
    guarantee_or_risk_reversal: Optional[str] = Field(
        default=None, description="Only if true."
    )
    cta: str = "Book a demo"

    # Style knobs
    tone: str = "confident, ops-smart, specific"
    length: Literal["short", "medium", "long"] = "medium"

    # Guardrails
    banned_terms: List[str] = Field(
        default_factory=list, description="Extra terms to forbid in the output."
    )
    required_phrases: List[str] = Field(
        default_factory=list, description="Phrases that must appear (if any)."
    )

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
# Inspired by Sugarman's principles: short opener, rhythm variation
# (short-medium-long-short), seeds of curiosity, and compression.

CURIOSITY_SEEDS = re.compile(
    r"(but (there's|here's)|let me explain|here's (the|why)|now here comes|read on|"
    r"and yet|truth is|turns out|look,|here's the thing|so,|you see)",
    re.I,
)


def _sentences(text: str) -> List[str]:
    s = re.split(r"(?<=[.!?])\s+", text.strip())
    return [x.strip() for x in s if x.strip()]


def _word_count(s: str) -> int:
    return len(re.findall(r"\w+", s))


def slippery_score(text: str) -> float:
    """
    Score 0-100 estimating how well copy follows the slippery-slide pattern.

    Five components (Sugarman-derived):
    1. Short opener   — first sentence <=10 words (ideally <=5)
    2. Rhythm variety  — adjacent sentences vary in length (not monotone)
    3. Length sweet spot — average sentence length near 8-16 words
    4. Compression      — penalize sentences >24 words; reward <=10
    5. Curiosity seeds  — bucket-brigade transitions and open loops
    """
    sents = _sentences(text)
    if not sents:
        return 0.0

    lengths = [_word_count(s) for s in sents]
    n = len(lengths)

    # 1) Short opener (20 pts) — Sugarman: first sentence extremely short
    first = lengths[0]
    if first <= 5:
        opener_score = 20.0
    elif first <= 10:
        opener_score = 14.0
    elif first <= 16:
        opener_score = 6.0
    else:
        opener_score = 0.0

    # 2) Rhythm variety (25 pts) — adjacent sentences should differ in length
    if n >= 2:
        diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, n)]
        avg_diff = sum(diffs) / len(diffs)
        # Target avg diff ~6 words between neighbors
        rhythm_score = 25.0 * min(1.0, avg_diff / 6.0)
    else:
        rhythm_score = 12.5  # single sentence, neutral

    # 3) Length sweet spot (20 pts) — average near 8-16 words
    avg_len = sum(lengths) / n
    if 8 <= avg_len <= 16:
        avg_score = 20.0
    elif avg_len < 8:
        avg_score = 20.0 * max(0.0, avg_len / 8.0)
    else:
        avg_score = 20.0 * max(0.0, 1.0 - (avg_len - 16) / 16.0)

    # 4) Compression (20 pts) — penalize long, reward short
    long_ratio = sum(1 for L in lengths if L > 24) / n
    short_ratio = sum(1 for L in lengths if L <= 10) / n
    compress_score = 20.0 * min(1.0, (short_ratio + (1.0 - long_ratio)) / 2.0)

    # 5) Curiosity seeds (15 pts) — bucket brigades and open loops
    seed_count = len(CURIOSITY_SEEDS.findall(text))
    # Reward up to ~1 seed per 4 sentences
    target_seeds = max(1, n / 4)
    curiosity_score = 15.0 * min(1.0, seed_count / target_seeds)

    total = opener_score + rhythm_score + avg_score + compress_score + curiosity_score
    return round(max(0.0, min(100.0, total)), 2)


# ----------------------------
# Guardrail / linting
# ----------------------------
STAT_PATTERN = re.compile(
    r"(\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*x\b|\b\d+(\.\d+)?\s*(days|hours|weeks|months)\b)",
    re.I,
)


def lint_copy(
    text: str,
    brand: Dict[str, Any],
    req: OTECopyRequest,
) -> List[str]:
    warnings: List[str] = []

    # 1) banned terms (brand + request)
    banned = set(
        [t.lower() for t in brand.get("do_not_say", [])]
        + [t.lower() for t in req.banned_terms]
    )
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
            warnings.append(
                f"Possible invented stat/number: '{s}' (not found in proof_points)"
            )

    # 4) hard claims language check (soft heuristic)
    risky_phrases = [
        "guaranteed",
        "always",
        "never",
        "best",
        "number one",
        "industry-leading",
    ]
    for rp in risky_phrases:
        if rp in text.lower():
            warnings.append(
                f"Potentially over-absolute claim detected: '{rp}' (consider softening or adding proof)"
            )

    return warnings


# ----------------------------
# Asset templates (no LLM)
# ----------------------------
def template_landing_hero(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    # Sugarman: headline sells the concept/outcome, not the product
    headline = f"Plans break. {req.primary_outcome.capitalize()} shouldn't."
    # Sugarman: subhead adds one benefit + pulls into body
    subhead = (
        f"{brand['brand_name']} helps {req.target_audience} turn constraints "
        f"into a plan teams can actually run. Without adding chaos to your day."
    )
    bullets = [b for b in req.key_benefits[:5]]
    proof = req.proof_points[:3]
    proof_line = " | ".join(proof) if proof else ""
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
    # Sugarman: subject creates curiosity; opening is SHORT
    subject = f"The real reason {req.target_audience} replan every week"
    # Short opener (Sugarman: 2-7 words to pull them in)
    opening = "Plans break. You know this."
    # Bucket brigade + bridge (emotion first)
    bridge = (
        "The schedule looked solid Monday morning. By Wednesday, three things changed and "
        "your team is back to firefighting.\n\n"
        f"Here's the thing: {brand['brand_name']} is built for exactly that moment. "
        "Not a prettier plan. A plan your team can keep running when constraints shift."
    )
    # Benefits with a seed of curiosity
    benefits = "\n".join([f"- {b}" for b in req.key_benefits[:5]])
    benefits_block = "Here's what that looks like in practice:\n" + benefits

    # Proof (only if available)
    proof_block = ""
    if req.proof_points:
        proof_block = "And these aren't hypotheticals:\n" + "\n".join(
            [f"- {p}" for p in req.proof_points[:4]]
        )

    # Sugarman: raise objections proactively, resolve honestly
    objection_block = ""
    if req.objections:
        obj_lines = "\n".join([f'"{o}"' for o in req.objections[:2]])
        objection_block = f"You might be thinking:\n{obj_lines}\n\nFair. That's exactly why we start with your real constraints, not a generic demo."

    # Sugarman: close with clarity, restate benefit, frictionless CTA
    close = f"If this is worth exploring, the next step is simple:\n{req.cta}\n\n{req.offer_details}"

    parts = [opening, bridge, benefits_block]
    if proof_block:
        parts.append(proof_block)
    if objection_block:
        parts.append(objection_block)
    parts.append(close)

    return {
        "subject": subject,
        "body": "\n\n".join(parts).strip(),
    }


def template_linkedin_post(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Dict[str, Any]:
    # Sugarman: short hook (pattern interrupt), then rhythm variation
    hook = "Your schedule isn't the problem."
    body = (
        "The problem is what happens to it by Wednesday.\n\n"
        "Constraints shift. Priorities change. And suddenly your team is replanning "
        "instead of executing.\n\n"
        "Truth is, chasing a perfect plan is a trap. What works is a plan your team "
        "can *keep using* when reality shows up.\n\n"
        "A quick litmus test:\n"
        f"• Can you see today's binding constraint?\n"
        f"• Are tradeoffs explicit (capacity vs. lead time vs. service)?\n"
        f"• Is the next action obvious to the person doing the work?\n\n"
        f"If not, that's the gap. And it's the exact problem "
        f"{brand['brand_name']} helps {req.target_audience} close."
    )
    # Sugarman: CTA should be frictionless and clear
    cta = f"Want a quick walkthrough? {req.cta}"
    return {"post": "\n\n".join([hook, body, cta]).strip()}


def generate_template(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    if req.asset_type == "landing_hero":
        out = template_landing_hero(req, brand)
        text_for_score = " ".join(
            [str(v) for v in out.values() if isinstance(v, (str, list))]
        )
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
    text_for_score = " ".join(
        [out.get("headline", ""), out.get("body", ""), out.get("cta", "")]
    )
    return out, text_for_score


# ----------------------------
# LLM prompting
# ----------------------------
def build_system_prompt(brand: Dict[str, Any]) -> str:
    do_not_say = ", ".join(brand.get("do_not_say", [])) or "(none)"

    consciousness = build_consciousness(brand)

    return f"""{consciousness}

=== BANNED TERMS ===
{do_not_say}

=== OUTPUT FORMAT ===
Return STRICT JSON ONLY (no markdown, no code fences, no commentary) matching the required schema for the chosen asset type.
""".strip()


def build_user_prompt(req: OTECopyRequest) -> str:
    # Schema + asset-specific Sugarman guidance for each type
    schema_map = {
        "landing_hero": {
            "schema": {
                "headline_options": [
                    "string (5 options, concept-first, max 12 words each)"
                ],
                "subhead": "string (1-2 sentences, adds benefit + pulls into body)",
                "bullets": ["string (5-7 bullets, one benefit each, start with verb)"],
                "proof_line": "string (empty if no proof_points)",
                "cta": "string",
                "cta_secondary": "string",
                "notes": ["string"],
            },
            "guidance": (
                "Headlines: sell the outcome/concept, not the product name. Short, punchy, curiosity-driven. "
                "Subhead: one clear benefit sentence + a pull into the bullets. "
                "Bullets: start each with an action verb. One idea per bullet."
            ),
        },
        "landing_sections": {
            "schema": {
                "sections": [
                    {"title": "string", "body": "string", "bullets": ["string"]}
                ],
                "faq": [{"q": "string", "a": "string"}],
                "cta_block": {"headline": "string", "body": "string", "cta": "string"},
                "notes": ["string"],
            },
            "guidance": (
                "Section titles: when read in sequence, they should tell their own coherent story (Sugarman subhead rule). "
                "Section body: open each with a short sentence, vary rhythm, end with a curiosity seed pulling into the next section. "
                "FAQ: answer honestly and concisely. Raise real objections."
            ),
        },
        "email_single": {
            "schema": {
                "subject_options": [
                    "string (5 options, curiosity-driven, max 8 words each)"
                ],
                "preview_text": "string (max 90 chars, extends the subject's curiosity)",
                "body": "string",
                "ps": "string (add one unexpected benefit or restate the CTA differently)",
                "notes": ["string"],
            },
            "guidance": (
                "Subject: create an open loop the reader must open the email to close. "
                "Body: first sentence MUST be 2-7 words. Use bucket brigade transitions between paragraphs. "
                "Weave in 1-2 objections mid-body and resolve them. End with a frictionless CTA. "
                "P.S.: Sugarman's 'second headline'—many readers skip to the P.S. first."
            ),
        },
        "email_sequence": {
            "schema": {
                "emails": [
                    {
                        "day": "int",
                        "subject": "string",
                        "preview_text": "string",
                        "body": "string",
                    }
                ],
                "notes": ["string"],
            },
            "guidance": (
                "Each email should stand alone but build on the sequence arc: "
                "Email 1: Problem recognition (emotion). Email 2: Mechanism/how (logic). "
                "Email 3: Proof + objection handling. Email 4+: Urgency + CTA. "
                "Every email: short opener, varied rhythm, one seed of curiosity pointing to the next."
            ),
        },
        "linkedin_post": {
            "schema": {
                "post_variants": ["string (3 variants, each a complete post)"],
                "notes": ["string"],
            },
            "guidance": (
                "Hook: first line must stop the scroll—short, surprising, or contrarian. "
                "Body: 150-250 words, short paragraphs (1-3 sentences), line breaks between each. "
                "Use 'you' heavily. Include a practical takeaway (checklist, framework, or question). "
                "CTA: soft, conversational. No hard sell on LinkedIn."
            ),
        },
        "google_search_ad": {
            "schema": {
                "headlines": ["string (max 30 chars each, 15 options)"],
                "descriptions": ["string (max 90 chars each, 4 options)"],
                "notes": ["string"],
            },
            "guidance": (
                "Headlines: front-load the benefit or keyword. Every character counts at 30 max. "
                "Descriptions: lead with outcome, end with CTA. 90 chars max—be ruthless. "
                "Specificity wins in search ads: operational language over generic claims."
            ),
        },
        "sales_one_pager": {
            "schema": {
                "headline": "string",
                "who_its_for": "string",
                "problem": "string (2-3 sentences, emotion-first)",
                "solution": "string (2-3 sentences, concept-first then mechanism)",
                "key_benefits": ["string"],
                "capabilities": ["string"],
                "proof": ["string"],
                "cta": "string",
                "notes": ["string"],
            },
            "guidance": (
                "This is a leave-behind document. Headline: concept, not product name. "
                "Problem: start with a short, relatable pain sentence. "
                "Solution: sell the concept first ('a schedule that survives contact with reality'), then the mechanism. "
                "Keep everything scannable—a busy exec will spend 30 seconds on this."
            ),
        },
    }

    entry = schema_map[req.asset_type]
    desired_schema = entry["schema"]
    asset_guidance = entry["guidance"]

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

Asset-specific guidance:
{asset_guidance}

Return STRICT JSON with this schema:
{json.dumps(desired_schema, ensure_ascii=False, indent=2)}

Use ONLY these facts (do not add new facts):
{json.dumps(payload, ensure_ascii=False, indent=2)}
""".strip()


async def call_ollama(
    messages: List[Dict[str, str]], model: str, temperature: float
) -> str:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")


async def call_compatible(
    messages: List[Dict[str, str]], model: str, temperature: float
) -> str:
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


async def generate_llm(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
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
        offer_name="On Time Edge — Production Scheduling Implementation",
        target_audience="manufacturing schedulers and operations leaders",
        primary_outcome="a schedule your team can keep using when priorities shift",
        key_benefits=[
            "Reduce rework caused by last-minute schedule changes",
            "Make constraints and tradeoffs visible before they cause problems",
            "Align planning decisions with daily shop-floor execution",
            "Keep stakeholders on the same page across plants",
            "Move from reactive firefighting to proactive scheduling",
        ],
        capabilities=[
            "Vendor-agnostic APS selection and implementation",
            "Constraint-aware scheduling model built around your actual shop floor",
            "What-if scenario comparisons",
            "ERP/MES/OEE integration",
        ],
        proof_points=[
            "1000+ site implementations across 300+ global companies",
            "90-day time-to-first-value implementation target",
            "Serving aerospace, medical device, food & beverage, and pharma manufacturers",
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
