import hashlib
import os
import json
import re
from typing import Any, Dict, List, Optional, Literal, Tuple

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

from consciousness import build_consciousness

Provider = Literal["template", "ollama", "compatible", "anthropic"]
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
        "and implementation firm headquartered in Centennial, Colorado—not a software product. "
        "Founded in 2004 by Michel Babineau, the company merged with Toward Zero (founded by "
        "Aaron Muhl) in January 2023, combining deep APS/scheduling expertise with smart "
        "manufacturing and systems integration capabilities. They help manufacturers select, "
        "implement, integrate, and optimize APS, MES, OEE, and supply chain systems across "
        "20+ manufacturing industries."
    ),
    "leadership": [
        "Brian Vogel — CEO (Sept 2025), 30+ years in manufacturing, ex-EPAM/Rockwell Automation",
        "Michel Babineau — Founder/Managing Partner, founded OTE in 2004, ex-Infor/Ericsson",
        "Aaron Muhl — Co-Founder/Managing Partner, founded Toward Zero 2015, ISA-95 voting member 12+ years",
        "Brian Lindenmeyer — VP Strategy & Partnerships (Jan 2026), ex-Kinaxis, leading Kinaxis go-to-market expansion",
    ],
    "voice": [
        "Plainspoken, ops-smart, confident",
        "Specific over hype—use operational language (constraints, throughput, lead time), not buzzwords",
        "Direct-response structure without gimmicks",
        "Respect skeptical buyers—they've heard every vendor pitch",
        "Consultative, not salesy—trusted advisor, not product pusher",
    ],
    "audience": [
        "Manufacturing and supply chain executives (VP Ops, VP Supply Chain, COO)",
        "Plant schedulers, planners, and operations leaders",
        "IT / OT stakeholders supporting operational systems and digital transformation",
        "RevOps stakeholders evaluating APS, MES, and supply chain platforms",
    ],
    "industries": [
        "Aerospace and defense",
        "Automotive",
        "Consumer packaged goods (CPG)",
        "Food and beverage",
        "Life sciences",
        "Medical device",
        "Metals and metal parts",
        "Oil and gas",
        "Pharmaceutical",
        "Plastics and rubber",
        "Industrial equipment",
        "Building materials",
    ],
    "services": [
        "System implementation — APS, MES, OEE deployment with 90-day time-to-first-value targets",
        "Systems integration — ERP/MES/OEE connectivity, custom APIs, ISA-88/95 layer alignment",
        "Managed services (MSP) — post-go-live system health, upgrades, and process optimization",
        "Business process consulting — Theory of Constraints (TOC) and Critical Chain methodology",
        "Digital strategy — current/future state mapping, digital master plans, IT/OT convergence",
        "Training — solutions training for manufacturing teams",
    ],
    "methodology": {
        "mdif": (
            "MDIF (Manufacturing Digital Interoperability Framework): proprietary strategic framework "
            "providing a structured, repeatable path from strategy through execution and enablement. "
            "Emphasizes system cohesion, data interoperability, and persona-driven workflows. "
            "Enables AI-driven optimization: forecasting optimal sequences, dynamically rerouting around "
            "disruptions, simulating what-if scenarios, and adjusting setpoints in real time."
        ),
        "toc": (
            "Theory of Constraints (TOC) / TLS approach: optimizing systems by identifying and managing "
            "the binding constraint, reducing bottlenecks, increasing throughput, and optimizing scheduling "
            "for customer demand rather than purely reducing waste."
        ),
        "project_kickoff": (
            "Projects begin with a three-day workshop to align the workforce behind goals and objectives. "
            "Engineering work commences immediately. First business impact with quantifiable results is "
            "expected approximately 90-100 days after engineering work launches."
        ),
    },
    "partners": {
        "aps": [
            "Kinaxis Maestro (major strategic partner — SI, Solution Extension, VAR)",
            "Siemens Opcenter APS (formerly Preactor)",
            "Dassault DELMIA Ortems",
            "PlanetTogether APS",
            "Optessa (now Eyelit Technologies)",
            "Greycon",
            "GE Digital ROB-EX Scheduler",
            "GE Proficy Scheduling",
            "Infor Thru-Put",
            "MOOPI by Berclain (now Infor)",
        ],
        "mes_oee": [
            "Sepasoft (MES modules on Ignition)",
            "Parsec Automation / TrakSYS",
            "AVEVA (MES/SCADA/operations)",
            "GE Vernova / Proficy (MES/MOM/historian)",
            "Fuuz by MFGx (AI-enabled MES/WMS/QMS — strategic partnership Jan 2026)",
        ],
        "automation_plm": [
            "Rockwell Automation",
            "Siemens (automation and controls)",
            "FANUC America",
            "Dassault Systemes (PLM)",
            "PTC (PLM)",
        ],
        "other": [
            "Ignition by Inductive Automation (SCADA/MES platform)",
            "Sage Clarity",
            "JITbase Technology Inc.",
            "Canary Labs (data historian/analytics)",
            "ZONTAL Inc. (data management for life sciences)",
            "Epicflow (resource/project planning)",
            "42Q (cloud MES/quality)",
            "CESMII (The Smart Manufacturing Institute)",
        ],
    },
    "positioning": [
        "Vendor-agnostic: partners with competing vendors (Siemens + Rockwell, Dassault + Siemens, multiple APS platforms) — recommends whichever fits the client's environment",
        "30+ years of APS implementation specialization, 1000+ site implementations across 300+ global companies",
        "90-day time-to-first-value implementation targets, starting with a 3-day alignment workshop",
        "MDIF (Manufacturing Digital Interoperability Framework): proprietary methodology from strategy through execution",
        "Post-implementation partnership via managed services—not a build-and-walk-away consultancy",
        "Turn constraints into an actionable plan teams can execute",
        "Theory of Constraints (TOC) practitioners — optimize the binding constraint, not just reduce waste",
        "Formed from 2023 merger of On-Time Edge (APS/scheduling) + Toward Zero (smart manufacturing/integration)",
    ],
    "proof_points": [
        "1000+ site implementations across 300+ global companies",
        "90-day time-to-first-value implementation target",
        "30+ years of APS implementation specialization",
        "20+ manufacturing industries served",
        "JARP Industries: achieved perfect on-time delivery year, won Supplier of the Year award",
        "Electrical device manufacturer: on-time delivery improved by 95%",
        "Building materials company: sales improved 10% through better scheduling",
        "Top 5 life sciences manufacturer selected OTE for global digital strategy (WEF Lighthouse framework)",
        "Named clients include Lockheed Martin, Chrysler, Del Monte, Bemis Manufacturing, Delta Faucet, Universal Studios",
        "Manufacturing Scheduling Summit 2025 — inaugural industry event featuring CESMII CEO keynote",
    ],
    "milestones": [
        "2004 — Michel Babineau founds On-Time Edge",
        "2015 — Aaron Muhl founds Toward Zero",
        "Dec 2022 — Merger announced",
        "Jan 2023 — Merged operations as On Time Edge dba Toward Zero",
        "2024 — Refreshed brand under unified On Time Edge name",
        "June 2025 — Top 5 life sciences manufacturer selects OTE for global digital strategy",
        "Sept 2025 — Brian Vogel appointed CEO to advance MDIF and global growth",
        "Nov 2025 — Inaugural Manufacturing Scheduling Summit in Philadelphia",
        "Jan 2026 — Fuuz (MFGx) strategic partnership announced",
        "Jan 2026 — Brian Lindenmeyer appointed VP Strategy & Partnerships for Kinaxis expansion",
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
        "Theory of Constraints",
        "TOC",
        "MDIF",
        "ISA-95",
        "ISA-88",
        "IT/OT convergence",
        "APS",
        "MOM",
        "digital twin",
        "IIoT",
        "shop floor",
        "binding constraint",
        "replanning",
        "on-time delivery",
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
    model: str = "claude-sonnet-4-5-20250929"
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
# Template variation helpers
# ----------------------------
def _pick(options: list, seed: str) -> Any:
    """Deterministically pick from a list based on a seed string."""
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(options)
    return options[idx]


def _request_seed(req: OTECopyRequest) -> str:
    """Create a seed string from request content for deterministic variation."""
    return f"{req.offer_name}|{req.target_audience}|{req.primary_outcome}"


# ----------------------------
# Asset templates (no LLM)
# ----------------------------
def template_landing_hero(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    seed = _request_seed(req)
    name = brand["brand_name"]

    headline_patterns = [
        f"Plans break. {req.primary_outcome.capitalize()} shouldn't.",
        "Your schedule survives Monday. What about Wednesday?",
        "The plan looked perfect. Then reality showed up.",
        "Stop replanning. Start executing.",
        "Constraints aren't the enemy. Ignoring them is.",
    ]
    headline = _pick(headline_patterns, seed)

    subhead_patterns = [
        (
            f"{name} helps {req.target_audience} turn constraints "
            f"into a plan teams can actually run. Without adding chaos to your day."
        ),
        (
            f"Most scheduling tools break on contact with your shop floor. "
            f"{name} builds around the constraints you already have."
        ),
        (
            f"Your team knows the constraints by feel. "
            f"{name} makes them visible — and actionable."
        ),
    ]
    subhead = _pick(subhead_patterns, seed + "sub")

    bullets = [b for b in req.key_benefits[:5]]
    proof = req.proof_points[:3]
    proof_line = " | ".join(proof) if proof else ""

    return {
        "headline": headline,
        "subhead": subhead,
        "bullets": bullets,
        "proof_line": proof_line,
        "cta": req.cta,
        "cta_secondary": "See how it works",
    }


def template_email_single(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    seed = _request_seed(req)
    name = brand["brand_name"]

    # --- Subject lines: varied patterns ---
    subject_patterns = [
        f"The real reason {req.target_audience} replan every week",
        "Your Wednesday problem",
        "What happens to your schedule by midweek?",
        "The scheduling gap nobody demos",
        "Why adoption fails (and what to do instead)",
    ]
    subject = _pick(subject_patterns, seed)

    # --- Openers: short, punchy, varied ---
    opener_patterns = [
        "Plans break. You know this.",
        "Here's what nobody tells you.",
        "Let's skip the pitch.",
        "Quick question.",
        "Your schedule looked solid Monday.",
    ]
    opening = _pick(opener_patterns, seed + "open")

    # --- Bridges: emotion-first, then pivot ---
    bridge_patterns = [
        (
            "The schedule looked solid Monday morning. By Wednesday, three things "
            "changed and your team is back to firefighting.\n\n"
            f"Here's the thing: {name} is built for exactly that moment. "
            "Not a prettier plan. A plan your team can keep running when "
            "constraints shift."
        ),
        (
            "You've seen it happen. The plan made sense when it was published. "
            "Then a machine went down, a priority shifted, and suddenly everyone's "
            "working off a different version of reality.\n\n"
            f"That's the gap {name} closes. Not with better software — with "
            "better implementation of the right software for your plant."
        ),
        (
            "Most scheduling conversations start with a demo. We'd rather start "
            "with a question: what breaks first?\n\n"
            "Because the answer tells us more about your operation than any "
            "requirements document. And it's exactly where we focus."
        ),
    ]
    bridge = _pick(bridge_patterns, seed + "bridge")

    # --- Benefits block ---
    benefit_intros = [
        "Here's what that looks like in practice:",
        "Specifically, here's what changes:",
        "What you'd walk away with:",
    ]
    benefits = "\n".join([f"- {b}" for b in req.key_benefits[:5]])
    benefits_block = _pick(benefit_intros, seed + "ben") + "\n" + benefits

    # --- Proof block ---
    proof_block = ""
    if req.proof_points:
        proof_intros = [
            "And these aren't hypotheticals:",
            "This isn't theory:",
            "The track record:",
        ]
        proof_block = (
            _pick(proof_intros, seed + "proof")
            + "\n"
            + "\n".join([f"- {p}" for p in req.proof_points[:4]])
        )

    # --- Objection handling: individual responses ---
    objection_block = ""
    if req.objections:
        obj_parts = ["You might be thinking:\n"]
        objection_responses = [
            "Fair. That's exactly why we start with your real constraints, not a generic demo.",
            "We hear that a lot. And honestly? Sometimes the existing tool is fine — it just needs better implementation. We'll tell you if that's the case.",
            "Makes sense. That's actually the starting point, not the blocker. We build around variability — not despite it.",
            "Understood. That's why our first conversation isn't a pitch. It's a diagnostic.",
        ]
        for i, obj in enumerate(req.objections[:3]):
            response = _pick(objection_responses, seed + f"obj{i}")
            obj_parts.append(f'"{obj}"\n\n{response}')
        objection_block = "\n\n".join(obj_parts)

    # --- Close ---
    close_patterns = [
        f"If this is worth exploring, the next step is simple:\n{req.cta}\n\n{req.offer_details}",
        f"One step. No commitment:\n{req.cta}\n\n{req.offer_details}",
        f"Here's the next move:\n{req.cta}\n\n{req.offer_details}",
    ]
    close = _pick(close_patterns, seed + "close")

    # --- P.S. line (Sugarman's second headline) ---
    ps_patterns = [
        None,  # sometimes no P.S. is fine
        "P.S. If we can't help, we'll tell you. We'd rather earn trust than waste your time.",
        "P.S. Not ready for a call? Reply with your top scheduling constraint — we'll send a one-page breakdown of what we've seen work.",
    ]
    if req.guarantee_or_risk_reversal:
        ps_patterns.append(f"P.S. {req.guarantee_or_risk_reversal}")
    ps = _pick(ps_patterns, seed + "ps")

    parts = [opening, bridge, benefits_block]
    if proof_block:
        parts.append(proof_block)
    if objection_block:
        parts.append(objection_block)
    parts.append(close)
    if ps:
        parts.append(ps)

    return {
        "subject": subject,
        "body": "\n\n".join(parts).strip(),
    }


def template_email_sequence(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a 3-email sequence: problem, mechanism, proof+CTA."""
    seed = _request_seed(req)
    name = brand["brand_name"]
    benefits = req.key_benefits
    proof = req.proof_points
    objections = req.objections

    # --- Email 1: Problem recognition (emotion) ---
    e1_openers = [
        "Plans break. You know this.",
        "Quick question.",
        "Here's the pattern.",
    ]
    e1_opener = _pick(e1_openers, seed + "e1o")

    e1_body_parts = [
        e1_opener,
        (
            "The schedule looked solid Monday morning. By Wednesday, three things "
            "changed and your team is back to firefighting.\n\n"
            "It's not a planning problem. It's a constraints problem. The plan "
            "doesn't account for what actually happens on the floor."
        ),
    ]
    if benefits:
        e1_body_parts.append(
            "What if instead of replanning, your team could:\n"
            + "\n".join([f"- {b}" for b in benefits[:3]])
        )
    e1_body_parts.append(
        f"That's what {name} helps {req.target_audience} build.\n\n"
        f"More on how in the next email. For now — does this sound like your Wednesday?"
    )

    email_1 = {
        "day": 0,
        "subject": "Your Wednesday problem",
        "preview_text": "The schedule looked solid Monday. Then what?",
        "body": "\n\n".join(e1_body_parts).strip(),
    }

    # --- Email 2: Mechanism/how (logic) ---
    e2_openers = [
        "So how does this actually work?",
        "Let me explain.",
        "Here's the mechanism.",
    ]
    e2_opener = _pick(e2_openers, seed + "e2o")

    e2_body_parts = [
        e2_opener,
        (
            f"Last email I described the Wednesday problem — the gap between "
            f"the plan and the floor.\n\n"
            f"{name} closes that gap. But not the way you'd expect."
        ),
        (
            "We don't sell software. We implement it. The right APS for your "
            "plant, integrated with your MES and ERP, built around your actual "
            "constraints — not a vendor's idea of them."
        ),
    ]
    if benefits[2:]:
        e2_body_parts.append(
            "In practice, that means:\n" + "\n".join([f"- {b}" for b in benefits[2:5]])
        )
    if objections:
        obj = objections[0]
        e2_body_parts.append(
            f'You might be thinking: "{obj}"\n\n'
            "Fair. That's why we start with your real constraints — not a generic demo."
        )
    e2_body_parts.append(
        "Tomorrow I'll share what this looks like in practice — real results, real plants."
    )

    email_2 = {
        "day": 2,
        "subject": "How constraint-aware scheduling actually works",
        "preview_text": f"{name} doesn't sell software. Here's what they do instead.",
        "body": "\n\n".join(e2_body_parts).strip(),
    }

    # --- Email 3: Proof + CTA ---
    e3_openers = [
        "Numbers time.",
        "Let's talk proof.",
        "Here's the track record.",
    ]
    e3_opener = _pick(e3_openers, seed + "e3o")

    e3_body_parts = [e3_opener]
    if proof:
        e3_body_parts.append(
            "I said I'd share results. Here they are:\n"
            + "\n".join([f"- {p}" for p in proof[:5]])
        )
    else:
        e3_body_parts.append(
            f"{name} has been doing this for 30+ years across 1000+ sites. "
            "Not selling tools — implementing them, integrating them, and "
            "making sure they stick."
        )

    if len(objections) > 1:
        e3_body_parts.append(
            f'One more thing you might be thinking: "{objections[1]}"\n\n'
            "That's actually why we built managed services into every engagement. "
            "We don't disappear after go-live."
        )

    e3_body_parts.append(
        f"If any of this resonated, here's the next step:\n{req.cta}\n\n"
        f"{req.offer_details}"
    )
    if req.guarantee_or_risk_reversal:
        e3_body_parts.append(req.guarantee_or_risk_reversal)

    email_3 = {
        "day": 5,
        "subject": _pick(
            [
                "The results (and a simple next step)",
                "1000+ sites. Here's what they learned.",
                "Proof, not promises",
            ],
            seed + "e3s",
        ),
        "preview_text": "Real results from real plants — and one frictionless next step.",
        "body": "\n\n".join(e3_body_parts).strip(),
    }

    return {"emails": [email_1, email_2, email_3]}


def template_linkedin_post(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Dict[str, Any]:
    seed = _request_seed(req)
    name = brand["brand_name"]

    hook_patterns = [
        "Your schedule isn't the problem.",
        "Stop optimizing the plan. Start optimizing the constraint.",
        "The best scheduling tool is the one your team actually uses.",
        "Hot take: your APS implementation failed because of process, not software.",
    ]
    hook = _pick(hook_patterns, seed)

    body = (
        "The problem is what happens to it by Wednesday.\n\n"
        "Constraints shift. Priorities change. And suddenly your team is replanning "
        "instead of executing.\n\n"
        "Truth is, chasing a perfect plan is a trap. What works is a plan your team "
        "can *keep using* when reality shows up.\n\n"
        "A quick litmus test:\n"
        "• Can you see today's binding constraint?\n"
        "• Are tradeoffs explicit (capacity vs. lead time vs. service)?\n"
        "• Is the next action obvious to the person doing the work?\n\n"
        f"If not, that's the gap. And it's the exact problem "
        f"{name} helps {req.target_audience} close."
    )
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

    if req.asset_type == "email_sequence":
        out = template_email_sequence(req, brand)
        all_bodies = " ".join([e["body"] for e in out["emails"]])
        return out, all_bodies

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


async def call_anthropic(
    messages: List[Dict[str, str]], model: str, temperature: float
) -> str:
    """Call the Anthropic Messages API directly via httpx."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "Missing ANTHROPIC_API_KEY. Set it in your environment or .env file."
        )

    # Separate the system message from user/assistant messages
    system_text = ""
    chat_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            chat_messages.append({"role": msg["role"], "content": msg["content"]})

    # Ensure we have at least one user message
    if not chat_messages:
        raise RuntimeError("No user message provided for Anthropic API call.")

    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "temperature": temperature,
        "messages": chat_messages,
    }
    if system_text:
        payload["system"] = system_text

    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
        # Anthropic returns content as a list of blocks
        content_blocks = data.get("content", [])
        text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
        return "".join(text_parts)


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
    elif req.provider == "anthropic":
        content = await call_anthropic(messages, req.model, req.temperature)
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
        model=os.getenv("MODEL", "claude-sonnet-4-5-20250929"),
        temperature=float(os.getenv("TEMP", "0.6")),
    )

    async def run():
        # Call the API function directly for quick local test
        resp = await generate(sample)  # type: ignore
        print(json.dumps(resp.model_dump(), ensure_ascii=False, indent=2))

    asyncio.run(run())
