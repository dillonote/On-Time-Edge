import os
import json
import re
import random
from typing import Any, Dict, List, Optional, Literal, Tuple

import httpx
from fastapi import FastAPI, HTTPException
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
    raw = os.getenv("BRAND_PROFILE_JSON", "").strip()
    if not raw:
        return DEFAULT_BRAND_PROFILE
    # Try parsing as inline JSON first
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Fall back to treating it as a file path
        if not os.path.isfile(raw):
            return DEFAULT_BRAND_PROFILE
        with open(raw, "r", encoding="utf-8") as f:
            obj = json.load(f)
    merged = dict(DEFAULT_BRAND_PROFILE)
    merged.update(obj)
    return merged


# ----------------------------
# Enhancement 1: Sugarman's 30 Psychological Triggers
# ----------------------------
SUGARMAN_TRIGGERS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Involvement",
        "description": "Make the reader participate mentally",
        "patterns": [r"\byou\b", r"\byour\b", r"\bimagine\b", r"\bpicture this\b"],
    },
    {
        "id": 2,
        "name": "Honesty",
        "description": "Admit limitations, share dirty laundry",
        "patterns": [
            r"\bhonestly\b",
            r"\btruth is\b",
            r"\bfrankly\b",
            r"\blet's be real\b",
            r"\bwe('re| are) not\b",
            r"\bwe don't\b",
        ],
    },
    {
        "id": 3,
        "name": "Integrity",
        "description": "Show consistency and trustworthiness",
        "patterns": [
            r"\btrack record\b",
            r"\bconsistently\b",
            r"\byear after year\b",
            r"\bsince \d{4}\b",
            r"\b\d+\+ (years|sites|implementations)\b",
        ],
    },
    {
        "id": 4,
        "name": "Credibility",
        "description": "Establish believability through proof",
        "patterns": [
            r"\bproven\b",
            r"\bverified\b",
            r"\bcertified\b",
            r"\bindependently\b",
            r"\bcase study\b",
            r"\bpeer-reviewed\b",
        ],
    },
    {
        "id": 5,
        "name": "Value Justification",
        "description": "Show the purchase is worth the price",
        "patterns": [
            r"\bROI\b",
            r"\bpays for itself\b",
            r"\bworth\b",
            r"\bvalue\b",
            r"\bsaves?\b",
            r"\bfor (just|only)\b",
        ],
    },
    {
        "id": 6,
        "name": "Greed",
        "description": "Appeal to getting more for less",
        "patterns": [
            r"\bfree\b",
            r"\bbonus\b",
            r"\bno cost\b",
            r"\bcomplimentary\b",
            r"\bat no\b",
            r"\bincluded\b",
        ],
    },
    {
        "id": 7,
        "name": "Desire to Belong",
        "description": "Reference peer groups and community",
        "patterns": [
            r"\bjoin\b",
            r"\bother (manufacturers|plants|companies)\b",
            r"\bleading\b",
            r"\bpeers\b",
            r"\bcommunity\b",
        ],
    },
    {
        "id": 8,
        "name": "Curiosity",
        "description": "Create open loops and tease information",
        "patterns": [
            r"\bhere's (the|why)\b",
            r"\bbut (there's|here's)\b",
            r"\bthat's (not|just) the\b",
            r"\bsurprising\b",
            r"\bunexpected\b",
            r"\bwhat if\b",
        ],
    },
    {
        "id": 9,
        "name": "Urgency",
        "description": "Create time pressure",
        "patterns": [
            r"\bright now\b",
            r"\btoday\b",
            r"\bdon't wait\b",
            r"\bbefore\b",
            r"\blimited\b",
            r"\bwhile\b",
            r"\bimmediately\b",
        ],
    },
    {
        "id": 10,
        "name": "Fear",
        "description": "Highlight risk of inaction",
        "patterns": [
            r"\brisk\b",
            r"\bfalling behind\b",
            r"\bcost of (doing nothing|inaction)\b",
            r"\bcan't afford\b",
            r"\bunplanned downtime\b",
            r"\bfirefighting\b",
        ],
    },
    {
        "id": 11,
        "name": "Instant Gratification",
        "description": "Promise quick results",
        "patterns": [
            r"\b(in|within) \d+ (days|hours|minutes|weeks)\b",
            r"\bquick\b",
            r"\bimmediat(e|ely)\b",
            r"\bfast\b",
            r"\btoday\b",
            r"\bright away\b",
        ],
    },
    {
        "id": 12,
        "name": "Exclusivity",
        "description": "Make the reader feel special",
        "patterns": [
            r"\bexclusive\b",
            r"\bselect(ed)?\b",
            r"\binvitation\b",
            r"\bprivate\b",
            r"\bonly for\b",
        ],
    },
    {
        "id": 13,
        "name": "Simplicity",
        "description": "Make it sound easy and clear",
        "patterns": [
            r"\bsimple\b",
            r"\beasy\b",
            r"\bstraightforward\b",
            r"\bjust\b",
            r"\bno (hassle|fuss|complexity)\b",
            r"\bplug.and.play\b",
        ],
    },
    {
        "id": 14,
        "name": "Specificity",
        "description": "Use concrete numbers and details",
        "patterns": [
            r"\b\d+%\b",
            r"\b\d+ (plants?|sites?|companies|implementations)\b",
            r"\b\d+-day\b",
            r"\b\d+-minute\b",
            r"\$\d",
        ],
    },
    {
        "id": 15,
        "name": "Familiarity",
        "description": "Reference known brands or concepts",
        "patterns": [
            r"\bPlanetTogether\b",
            r"\bKinaxis\b",
            r"\bSAP\b",
            r"\bOracle\b",
            r"\bERP\b",
            r"\bMES\b",
        ],
    },
    {
        "id": 16,
        "name": "Hope",
        "description": "Paint a positive future state",
        "patterns": [
            r"\bimagine\b",
            r"\bpicture\b",
            r"\bwhat if\b",
            r"\bfinally\b",
            r"\bat last\b",
            r"\binstead of\b",
        ],
    },
    {
        "id": 17,
        "name": "Storytelling",
        "description": "Narrative structure and anecdotes",
        "patterns": [
            r"\bwhen we\b",
            r"\bone (client|manufacturer|plant)\b",
            r"\blast (week|month|year|quarter)\b",
            r"\bfor example\b",
            r"\bhere's what happened\b",
        ],
    },
    {
        "id": 18,
        "name": "Authority",
        "description": "Establish expert positioning",
        "patterns": [
            r"\b\d+\+ years\b",
            r"\bexpert\b",
            r"\bspecialist\b",
            r"\bindustry\b",
            r"\bframework\b",
            r"\bmethodology\b",
            r"\bMDIF\b",
        ],
    },
    {
        "id": 19,
        "name": "Proof of Value",
        "description": "Show tangible results",
        "patterns": [
            r"\breduced?\b.*\b\d+%\b",
            r"\bsaved?\b.*\b\d+\b",
            r"\bimproved?\b.*\b\d+\b",
            r"\bdelivered\b",
            r"\bachieved\b",
            r"\bmeasurable\b",
        ],
    },
    {
        "id": 20,
        "name": "Emotion",
        "description": "Evoke feelings (frustration, relief, pride)",
        "patterns": [
            r"\bfrustrat(ed|ing|ion)\b",
            r"\bpainful\b",
            r"\brelief\b",
            r"\bconfiden(ce|t)\b",
            r"\bexhausting\b",
            r"\bchaos\b",
        ],
    },
    {
        "id": 21,
        "name": "Linking",
        "description": "Connect to something reader already believes",
        "patterns": [
            r"\byou (already|know)\b",
            r"\blike (you|your)\b",
            r"\bjust like\b",
            r"\bthe same way\b",
        ],
    },
    {
        "id": 22,
        "name": "Consistency",
        "description": "Appeal to reader's self-image",
        "patterns": [
            r"\byou're the (kind|type) of\b",
            r"\bas a\b.*\byou\b",
            r"\byou (believe|value|care)\b",
        ],
    },
    {
        "id": 23,
        "name": "Satisfaction Conviction",
        "description": "Guarantee or risk-reversal language",
        "patterns": [
            r"\bguarantee\b",
            r"\brisk.free\b",
            r"\bno.obligation\b",
            r"\bmoney.back\b",
            r"\bnothing to lose\b",
        ],
    },
    {
        "id": 24,
        "name": "Current Fad",
        "description": "Reference trending topics",
        "patterns": [
            r"\bAI\b",
            r"\bdigital (twin|thread|transformation)\b",
            r"\bIndustry 4\.0\b",
            r"\bsmart (factory|manufacturing)\b",
            r"\bIIoT\b",
        ],
    },
    {
        "id": 25,
        "name": "Guilt",
        "description": "Make inaction feel irresponsible",
        "patterns": [
            r"\bshould\b",
            r"\bowe it\b",
            r"\byour team (deserves?|needs?)\b",
            r"\bresponsib(le|ility)\b",
        ],
    },
    {
        "id": 26,
        "name": "Mental Engagement",
        "description": "Rhetorical questions and thought exercises",
        "patterns": [
            r"\?$",
            r"\bask yourself\b",
            r"\bthink about\b",
            r"\bconsider\b",
            r"\bhow (many|much|often)\b.*\?",
        ],
    },
    {
        "id": 27,
        "name": "Reciprocity",
        "description": "Give value before asking",
        "patterns": [
            r"\bfree (guide|audit|assessment|consultation)\b",
            r"\bno.strings\b",
            r"\bour gift\b",
            r"\bcomplimentary\b",
        ],
    },
    {
        "id": 28,
        "name": "Objection Raising",
        "description": "Preemptively address concerns",
        "patterns": [
            r"\byou might (be thinking|wonder)\b",
            r"\bfair (point|question|concern)\b",
            r"\byes,? but\b",
            r"\bskeptical\b",
        ],
    },
    {
        "id": 29,
        "name": "Social Proof",
        "description": "Evidence that others trust you",
        "patterns": [
            r"\b\d+\+? (companies|manufacturers|plants|sites|clients)\b",
            r"\btrusted by\b",
            r"\bworking with\b",
            r"\bthey (chose|use|rely)\b",
        ],
    },
    {
        "id": 30,
        "name": "Scarcity",
        "description": "Limited availability",
        "patterns": [
            r"\blimited\b",
            r"\bonly \d+\b",
            r"\bfew remaining\b",
            r"\bfilling (up|fast)\b",
            r"\bspots?\b",
        ],
    },
]


def detect_triggers(text: str) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    for trigger in SUGARMAN_TRIGGERS:
        matches: List[str] = []
        for pattern in trigger["patterns"]:
            for m in re.finditer(pattern, text, re.I | re.MULTILINE):
                matches.append(m.group(0))
        if matches:
            strength = (
                "strong"
                if len(matches) >= 3
                else "moderate"
                if len(matches) >= 2
                else "light"
            )
            found.append(
                {
                    "id": trigger["id"],
                    "name": trigger["name"],
                    "description": trigger["description"],
                    "match_count": len(matches),
                    "matches": matches[:5],
                    "strength": strength,
                }
            )
    return found


# ----------------------------
# Enhancement 2: First-Sentence Library
# ----------------------------
OpenerType = Literal["curiosity", "story", "contrast", "statistic", "direct_challenge"]

OPENER_LIBRARY: List[Dict[str, Any]] = [
    # Curiosity openers
    {
        "type": "curiosity",
        "template": "Here's what nobody tells {audience} about scheduling.",
        "id": "cur_01",
    },
    {
        "type": "curiosity",
        "template": "There's a pattern hiding in your production data.",
        "id": "cur_02",
    },
    {
        "type": "curiosity",
        "template": "The real bottleneck isn't where you think.",
        "id": "cur_03",
    },
    {
        "type": "curiosity",
        "template": "Something breaks between Monday's plan and Wednesday's reality.",
        "id": "cur_04",
    },
    {
        "type": "curiosity",
        "template": "Your schedule has a blind spot.",
        "id": "cur_05",
    },
    # Story openers
    {
        "type": "story",
        "template": "A plant manager called us last quarter with a familiar problem.",
        "id": "str_01",
    },
    {
        "type": "story",
        "template": "Last month, a scheduling team rewrote their plan 14 times in one week.",
        "id": "str_02",
    },
    {
        "type": "story",
        "template": "Three plants. Three different ERP systems. One deadline.",
        "id": "str_03",
    },
    {
        "type": "story",
        "template": "The schedule was perfect at 7 AM. By noon, it was fiction.",
        "id": "str_04",
    },
    # Contrast openers
    {
        "type": "contrast",
        "template": "Most scheduling tools show you what should happen. None show you what will.",
        "id": "con_01",
    },
    {
        "type": "contrast",
        "template": "Your ERP thinks in days. Your shop floor thinks in minutes.",
        "id": "con_02",
    },
    {
        "type": "contrast",
        "template": "Plans break. Execution doesn't have to.",
        "id": "con_03",
    },
    {
        "type": "contrast",
        "template": "You have data. What you don't have is a decision.",
        "id": "con_04",
    },
    {
        "type": "contrast",
        "template": "Spreadsheets plan. Constraints decide.",
        "id": "con_05",
    },
    # Statistic openers
    {
        "type": "statistic",
        "template": "The average plant replans 3x per week. How about yours?",
        "id": "sta_01",
    },
    {
        "type": "statistic",
        "template": "80% of schedule changes happen in the first 48 hours.",
        "id": "sta_02",
    },
    {
        "type": "statistic",
        "template": "1,000+ implementations taught us one thing.",
        "id": "sta_03",
    },
    {
        "type": "statistic",
        "template": "90 days. That's our target for first measurable value.",
        "id": "sta_04",
    },
    # Direct challenge openers
    {
        "type": "direct_challenge",
        "template": "Stop replanning. Start executing.",
        "id": "dir_01",
    },
    {
        "type": "direct_challenge",
        "template": "Your schedule is a guess. Let's fix that.",
        "id": "dir_02",
    },
    {
        "type": "direct_challenge",
        "template": "If your plan doesn't survive Tuesday, it's not a plan.",
        "id": "dir_03",
    },
    {
        "type": "direct_challenge",
        "template": "You don't need another tool. You need a constraint-aware plan.",
        "id": "dir_04",
    },
    {
        "type": "direct_challenge",
        "template": "Firefighting isn't a strategy.",
        "id": "dir_05",
    },
]


def get_openers(opener_type: Optional[str] = None) -> List[Dict[str, Any]]:
    if opener_type:
        return [o for o in OPENER_LIBRARY if o["type"] == opener_type]
    return OPENER_LIBRARY


def render_opener(opener: Dict[str, Any], audience: str = "manufacturers") -> str:
    return opener["template"].replace("{audience}", audience)


# ----------------------------
# Enhancement 3: Auto-Objection Detection
# ----------------------------
AUDIENCE_OBJECTIONS: Dict[str, List[Dict[str, str]]] = {
    "vp_ops": [
        {
            "objection": "We already have a planning tool — adoption is the problem.",
            "rebuttal_hint": "Address change management and user adoption approach.",
        },
        {
            "objection": "We can't pause production for a new system rollout.",
            "rebuttal_hint": "Emphasize parallel implementation and 90-day phased approach.",
        },
        {
            "objection": "How is this different from what SAP/Oracle already offers?",
            "rebuttal_hint": "Highlight vendor-agnostic approach and constraint-aware scheduling vs. MRP.",
        },
        {
            "objection": "Our constraints change too fast for any plan to stay relevant.",
            "rebuttal_hint": "Explain real-time constraint recalculation and what-if scenarios.",
        },
        {
            "objection": "We've been burned by consultants before.",
            "rebuttal_hint": "Mention post-implementation partnership model and measurable milestones.",
        },
    ],
    "coo": [
        {
            "objection": "What's the ROI timeline?",
            "rebuttal_hint": "Reference 90-day time-to-first-value and measurable KPIs.",
        },
        {
            "objection": "We have 5 plants — can this scale?",
            "rebuttal_hint": "Reference 1000+ site implementations and multi-plant experience.",
        },
        {
            "objection": "I need board-level metrics, not shop-floor details.",
            "rebuttal_hint": "Bridge operational improvements to EBITDA, OEE, and service-level metrics.",
        },
        {
            "objection": "Our digital transformation budget is already committed.",
            "rebuttal_hint": "Position as integration/optimization of existing investments, not net-new spend.",
        },
    ],
    "plant_manager": [
        {
            "objection": "My team won't learn another system.",
            "rebuttal_hint": "Emphasize simplicity, training approach, and building on existing workflows.",
        },
        {
            "objection": "I need results this quarter, not next year.",
            "rebuttal_hint": "Highlight 90-day phased approach with early quick wins.",
        },
        {
            "objection": "Our shop floor is too chaotic for a structured plan.",
            "rebuttal_hint": "Explain constraint-aware scheduling handles variability by design.",
        },
        {
            "objection": "We've tried APS before and it sat on the shelf.",
            "rebuttal_hint": "Differentiate implementation approach: start with real constraints, not theoretical models.",
        },
    ],
    "it_director": [
        {
            "objection": "How does this integrate with our existing ERP/MES stack?",
            "rebuttal_hint": "Reference MDIF framework and proven integrations with major platforms.",
        },
        {
            "objection": "We don't have bandwidth for another integration project.",
            "rebuttal_hint": "Explain that On Time Edge handles integration — not your IT team.",
        },
        {
            "objection": "What about data security and on-prem requirements?",
            "rebuttal_hint": "Address deployment flexibility — cloud, on-prem, or hybrid.",
        },
        {
            "objection": "Who supports this after go-live?",
            "rebuttal_hint": "Highlight post-implementation partnership model.",
        },
    ],
    "supply_chain_director": [
        {
            "objection": "Our supply chain visibility is already lacking.",
            "rebuttal_hint": "Position as improving visibility through constraint-aware planning.",
        },
        {
            "objection": "We need end-to-end, not just production scheduling.",
            "rebuttal_hint": "Explain MDIF covers supply chain planning through shop-floor execution.",
        },
        {
            "objection": "Demand is too volatile for APS to work.",
            "rebuttal_hint": "Explain what-if scenarios and rapid replanning capabilities.",
        },
    ],
}

# Map common audience strings to objection keys
AUDIENCE_KEY_MAP: Dict[str, str] = {
    "vp of operations": "vp_ops",
    "vp ops": "vp_ops",
    "vp operations": "vp_ops",
    "coo": "coo",
    "chief operating officer": "coo",
    "plant manager": "plant_manager",
    "plant managers": "plant_manager",
    "it director": "it_director",
    "it": "it_director",
    "cio": "it_director",
    "supply chain director": "supply_chain_director",
    "supply chain": "supply_chain_director",
    "supply chain manager": "supply_chain_director",
}


def _resolve_audience_key(audience: str) -> Optional[str]:
    audience_lower = audience.lower().strip()
    for phrase, key in AUDIENCE_KEY_MAP.items():
        if phrase in audience_lower:
            return key
    return None


def infer_objections(audience: str) -> List[Dict[str, str]]:
    key = _resolve_audience_key(audience)
    if key and key in AUDIENCE_OBJECTIONS:
        return AUDIENCE_OBJECTIONS[key]
    return AUDIENCE_OBJECTIONS.get("vp_ops", [])


def check_objections_addressed(
    text: str, objections: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    text_lower = text.lower()
    for obj in objections:
        keywords = re.findall(r"\b\w{4,}\b", obj["objection"].lower())
        keyword_hits = sum(1 for kw in keywords if kw in text_lower)
        addressed = keyword_hits >= max(2, len(keywords) // 3)
        results.append(
            {
                "objection": obj["objection"],
                "rebuttal_hint": obj["rebuttal_hint"],
                "addressed": addressed,
                "keyword_coverage": f"{keyword_hits}/{len(keywords)}",
            }
        )
    return results


# ----------------------------
# Enhancement 4: Concept Extraction
# ----------------------------
CONCEPT_PATTERNS: List[Dict[str, Any]] = [
    {
        "label": "operational_transformation",
        "patterns": [
            r"\btransform\b",
            r"\bfrom .* to\b",
            r"\binstead of\b",
            r"\bshift from\b",
        ],
        "weight": 2,
    },
    {
        "label": "constraint_management",
        "patterns": [
            r"\bconstraint",
            r"\bbottleneck",
            r"\bcapacity\b",
            r"\bthroughput\b",
        ],
        "weight": 2,
    },
    {
        "label": "visibility_clarity",
        "patterns": [
            r"\bvisib(le|ility)\b",
            r"\btransparen",
            r"\bclear\b",
            r"\bsee\b",
            r"\bblind spot\b",
        ],
        "weight": 1.5,
    },
    {
        "label": "speed_agility",
        "patterns": [
            r"\b(fast|quick|rapid|agile)\b",
            r"\breal.time\b",
            r"\b\d+ (days?|hours?|minutes?)\b",
        ],
        "weight": 1.5,
    },
    {
        "label": "reliability_trust",
        "patterns": [
            r"\breliab",
            r"\btrust\b",
            r"\bconfiden",
            r"\bproven\b",
            r"\bconsistent\b",
        ],
        "weight": 1.5,
    },
    {
        "label": "execution_focus",
        "patterns": [
            r"\bexecut",
            r"\bactionable\b",
            r"\bshop.floor\b",
            r"\brun\b",
            r"\bdeliver\b",
        ],
        "weight": 1,
    },
]


def extract_concept(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    scores: Dict[str, float] = {}
    for concept in CONCEPT_PATTERNS:
        match_count = 0
        for pattern in concept["patterns"]:
            match_count += len(re.findall(pattern, text_lower))
        scores[concept["label"]] = match_count * concept["weight"]

    if not any(scores.values()):
        return {
            "primary_concept": "none_detected",
            "strength": 0,
            "suggestion": "Copy lacks a clear central idea. Try leading with a single transformation or outcome.",
        }

    primary = max(scores, key=lambda k: scores[k])
    strength_raw = scores[primary]
    strength = min(10, round(strength_raw * 1.5, 1))

    suggestions: Dict[str, str] = {
        "operational_transformation": "Strong transformation angle. Make the before/after contrast more vivid.",
        "constraint_management": "Good constraint focus. Tie constraints directly to business outcomes (revenue, OTD).",
        "visibility_clarity": "Visibility is your hook. Quantify what becomes visible (e.g., 'see your binding constraint in 3 clicks').",
        "speed_agility": "Speed sells. Pair the speed claim with a specific proof point.",
        "reliability_trust": "Trust angle is working. Add a specific proof point or customer reference.",
        "execution_focus": "Execution is the concept. Contrast with 'planning theater' or unused reports.",
    }

    return {
        "primary_concept": primary.replace("_", " ").title(),
        "strength": strength,
        "all_scores": {
            k.replace("_", " ").title(): round(v, 1)
            for k, v in sorted(scores.items(), key=lambda x: -x[1])
        },
        "suggestion": suggestions.get(
            primary,
            "Concept detected. Consider strengthening with more specific language.",
        )
        if strength < 7
        else "Strong concept presence. Copy has a clear big idea.",
    }


# ----------------------------
# Request / response models
# ----------------------------
class OTECopyRequest(BaseModel):
    asset_type: AssetType = "landing_hero"
    offer_name: str = Field(..., description="What are we selling?")
    target_audience: str = Field(..., description="Who is this for?")
    primary_outcome: str = Field(..., description="Outcome they want.")
    key_benefits: List[str]
    capabilities: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(default_factory=list)
    objections: List[str] = Field(default_factory=list)
    offer_details: str = Field(..., description="What do they get / terms.")
    guarantee_or_risk_reversal: Optional[str] = Field(default=None)
    cta: str = "Book a demo"
    tone: str = "confident, ops-smart, specific"
    length: Literal["short", "medium", "long"] = "medium"
    banned_terms: List[str] = Field(default_factory=list)
    required_phrases: List[str] = Field(default_factory=list)
    provider: Provider = "template"
    model: str = "llama3.1"
    temperature: float = 0.6


class OTECopyResponse(BaseModel):
    asset_type: AssetType
    content: Dict[str, Any]
    warnings: List[str]
    slippery_score: float
    triggers: List[Dict[str, Any]] = Field(default_factory=list)
    concept: Dict[str, Any] = Field(default_factory=dict)
    objection_analysis: List[Dict[str, Any]] = Field(default_factory=list)


class RefineRequest(BaseModel):
    original_copy: str = Field(..., description="The copy text to refine.")
    feedback: str = Field(
        ..., description="What to improve (e.g., 'more urgent, open with question')."
    )
    asset_type: AssetType = "email_single"
    target_audience: str = "manufacturing operations leaders"
    provider: Provider = "template"
    model: str = "llama3.1"
    temperature: float = 0.6


class RefineResponse(BaseModel):
    original_copy: str
    refined_copy: str
    feedback_applied: str
    slippery_score_before: float
    slippery_score_after: float
    triggers_before: int
    triggers_after: int


class VariantRequest(BaseModel):
    asset_type: AssetType = "email_single"
    offer_name: str = Field(default="On Time Edge APS Implementation")
    target_audience: str = Field(default="manufacturing operations leaders")
    primary_outcome: str = Field(
        default="a schedule that survives contact with reality"
    )
    key_benefits: List[str] = Field(
        default_factory=lambda: ["Reduce rework", "Make constraints visible"]
    )
    proof_points: List[str] = Field(default_factory=list)
    offer_details: str = Field(default="Book a 20-minute walkthrough.")
    cta: str = "Book a demo"
    num_variants: int = Field(default=3, ge=2, le=10)
    provider: Provider = "template"
    model: str = "llama3.1"
    temperature: float = 0.6


class VariantResult(BaseModel):
    variant_id: int
    opener_type: str
    opener_text: str
    content: Dict[str, Any]
    slippery_score: float
    trigger_count: int


class VariantResponse(BaseModel):
    variants: List[VariantResult]
    best_variant_id: int
    comparison_summary: str


# ----------------------------
# Slippery-slide heuristic score
# ----------------------------
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
    sents = _sentences(text)
    if not sents:
        return 0.0

    lengths = [_word_count(s) for s in sents]
    n = len(lengths)

    first = lengths[0]
    if first <= 5:
        opener_score = 20.0
    elif first <= 10:
        opener_score = 14.0
    elif first <= 16:
        opener_score = 6.0
    else:
        opener_score = 0.0

    if n >= 2:
        diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, n)]
        avg_diff = sum(diffs) / len(diffs)
        rhythm_score = 25.0 * min(1.0, avg_diff / 6.0)
    else:
        rhythm_score = 12.5

    avg_len = sum(lengths) / n
    if 8 <= avg_len <= 16:
        avg_score = 20.0
    elif avg_len < 8:
        avg_score = 20.0 * max(0.0, avg_len / 8.0)
    else:
        avg_score = 20.0 * max(0.0, 1.0 - (avg_len - 16) / 16.0)

    long_ratio = sum(1 for L in lengths if L > 24) / n
    short_ratio = sum(1 for L in lengths if L <= 10) / n
    compress_score = 20.0 * min(1.0, (short_ratio + (1.0 - long_ratio)) / 2.0)

    seed_count = len(CURIOSITY_SEEDS.findall(text))
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


def lint_copy(text: str, brand: Dict[str, Any], req: OTECopyRequest) -> List[str]:
    warnings: List[str] = []
    banned = set(
        [t.lower() for t in brand.get("do_not_say", [])]
        + [t.lower() for t in req.banned_terms]
    )
    for term in banned:
        if term and term in text.lower():
            warnings.append(f"Banned term found: '{term}'")
    for phrase in req.required_phrases:
        if phrase and phrase.lower() not in text.lower():
            warnings.append(f"Required phrase missing: '{phrase}'")
    output_stats = set(m.group(0) for m in STAT_PATTERN.finditer(text))
    proof_blob = " ".join(req.proof_points).lower()
    for s in output_stats:
        if s.lower() not in proof_blob:
            warnings.append(
                f"Possible invented stat/number: '{s}' (not found in proof_points)"
            )
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
            warnings.append(f"Potentially over-absolute claim detected: '{rp}'")
    return warnings


# ----------------------------
# Asset templates (no LLM)
# ----------------------------
def template_landing_hero(req: OTECopyRequest, brand: Dict[str, Any]) -> Dict[str, Any]:
    headline = f"Plans break. {req.primary_outcome.capitalize()} shouldn't."
    subhead = (
        f"{brand['brand_name']} helps {req.target_audience} turn constraints "
        f"into a plan teams can actually run. Without adding chaos to your day."
    )
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
    subject = f"The real reason {req.target_audience} replan every week"
    opening = "Plans break. You know this."
    bridge = (
        "The schedule looked solid Monday morning. By Wednesday, three things changed and "
        "your team is back to firefighting.\n\n"
        f"Here's the thing: {brand['brand_name']} is built for exactly that moment. "
        "Not a prettier plan. A plan your team can keep running when constraints shift."
    )
    benefits = "\n".join([f"- {b}" for b in req.key_benefits[:5]])
    benefits_block = "Here's what that looks like in practice:\n" + benefits
    proof_block = ""
    if req.proof_points:
        proof_block = "And these aren't hypotheticals:\n" + "\n".join(
            [f"- {p}" for p in req.proof_points[:4]]
        )
    objection_block = ""
    if req.objections:
        obj_lines = "\n".join([f'"{o}"' for o in req.objections[:2]])
        objection_block = f"You might be thinking:\n{obj_lines}\n\nFair. That's exactly why we start with your real constraints, not a generic demo."
    close = f"If this is worth exploring, the next step is simple:\n{req.cta}\n\n{req.offer_details}"
    parts = [opening, bridge, benefits_block]
    if proof_block:
        parts.append(proof_block)
    if objection_block:
        parts.append(objection_block)
    parts.append(close)
    return {"subject": subject, "body": "\n\n".join(parts).strip()}


def template_linkedin_post(
    req: OTECopyRequest, brand: Dict[str, Any]
) -> Dict[str, Any]:
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
# Enhancement 5: Template-based refinement
# ----------------------------
def refine_template(original: str, feedback: str, audience: str) -> str:
    refined = original
    feedback_lower = feedback.lower()

    # Apply feedback-driven rewrites
    if "urgent" in feedback_lower or "urgency" in feedback_lower:
        if not refined.startswith("Right now"):
            refined = "Right now, your competitors are gaining ground.\n\n" + refined

    if "question" in feedback_lower or "open with" in feedback_lower:
        sents = _sentences(refined)
        if sents and not sents[0].endswith("?"):
            refined = (
                f"What if your {audience} could stop firefighting and start executing?\n\n"
                + refined
            )

    if (
        "shorter" in feedback_lower
        or "concise" in feedback_lower
        or "tighter" in feedback_lower
    ):
        sents = _sentences(refined)
        refined = " ".join(s for s in sents if _word_count(s) <= 20)

    if (
        "proof" in feedback_lower
        or "evidence" in feedback_lower
        or "credib" in feedback_lower
    ):
        refined += "\n\n1,000+ implementations across 300+ global companies. 90-day time-to-first-value."

    if (
        "dollar" in feedback_lower
        or "cost" in feedback_lower
        or "money" in feedback_lower
    ):
        refined += "\n\nEvery week of unplanned downtime costs your plant real money — money that constraint-aware scheduling can recover."

    if "objection" in feedback_lower:
        refined += (
            '\n\nYou might be thinking: "We\'ve tried planning tools before." '
            "Fair. That's why we start with your actual constraints, not a generic model."
        )

    if "cta" in feedback_lower or "call to action" in feedback_lower:
        refined += "\n\nBook a 20-minute walkthrough — no pitch, just your constraints mapped to a practical next step."

    return refined.strip()


# ----------------------------
# Enhancement 6: Variant generation
# ----------------------------
def generate_variant_with_opener(
    req: VariantRequest,
    opener: Dict[str, Any],
    brand: Dict[str, Any],
) -> Dict[str, Any]:
    opener_text = render_opener(opener, req.target_audience)
    bridge = (
        f"\n\n{brand['brand_name']} helps {req.target_audience} turn constraints "
        f"into a plan teams can actually run.\n\n"
    )
    benefits = "\n".join([f"- {b}" for b in req.key_benefits[:5]])
    body = opener_text + bridge + benefits + f"\n\n{req.cta}\n\n{req.offer_details}"

    return {
        "subject": f"Re: {req.primary_outcome}",
        "body": body.strip(),
    }


# ----------------------------
# LLM prompting
# ----------------------------
def build_system_prompt(brand: Dict[str, Any]) -> str:
    identity = brand.get("identity", "")
    voice = ", ".join(brand.get("voice", []))
    do_not_say = ", ".join(brand.get("do_not_say", [])) or "(none)"

    return f"""
You are a direct-response copywriter writing for {brand["brand_name"]}.
{identity}

Voice: {voice}
Banned terms: {do_not_say}

=== FACTUAL GUARDRAILS (non-negotiable) ===
- Use ONLY facts provided in the request fields. Do NOT invent stats, customers, certifications, timelines, integrations, guarantees, or outcomes.
- Do NOT use any banned terms.
- Do NOT name competitors unless explicitly provided.
- Avoid absolutes ("guaranteed", "always", "never", "best", "number one", "industry-leading") unless quoting a proof_point verbatim.
- If proof_points is empty, do NOT fabricate social proof.

=== SUGARMAN SLIPPERY-SLIDE METHOD ===
1. THE SLIDE: Every element gets the next element read.
2. SHORT OPENER: First sentence 2-7 words.
3. SELL THE CONCEPT, NOT THE PRODUCT.
4. SEEDS OF CURIOSITY: Open loops every 3-4 paragraphs.
5. BUCKET BRIGADE TRANSITIONS: "Look," / "Truth is," / "So," / "Here's the thing:"
6. SENTENCE RHYTHM: Vary deliberately. Short. Medium. Long. Short.
7. ONE IDEA PER SENTENCE.
8. EMOTION FIRST, LOGIC SECOND.
9. OBJECTIONS INSIDE THE FLOW.
10. SPECIFICITY OVER HYPE.
11. EDIT BY SUBTRACTION.
12. CLOSE WITH CLARITY.

=== OUTPUT FORMAT ===
Return STRICT JSON ONLY (no markdown, no code fences, no commentary).
""".strip()


def build_user_prompt(req: OTECopyRequest) -> str:
    schema_map = {
        "landing_hero": {
            "schema": {
                "headline_options": ["string"],
                "subhead": "string",
                "bullets": ["string"],
                "proof_line": "string",
                "cta": "string",
                "cta_secondary": "string",
            },
            "guidance": "Headlines: sell the outcome. Subhead: one benefit + pull. Bullets: start with verb.",
        },
        "landing_sections": {
            "schema": {
                "sections": [
                    {"title": "string", "body": "string", "bullets": ["string"]}
                ],
                "faq": [{"q": "string", "a": "string"}],
                "cta_block": {"headline": "string", "body": "string", "cta": "string"},
            },
            "guidance": "Section titles tell a story. Open each with short sentence. End with curiosity seed.",
        },
        "email_single": {
            "schema": {
                "subject_options": ["string"],
                "preview_text": "string",
                "body": "string",
                "ps": "string",
            },
            "guidance": "Subject: open loop. Body: first sentence 2-7 words. Weave in objections. P.S. is the second headline.",
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
                ]
            },
            "guidance": "Email 1: emotion. Email 2: logic. Email 3: proof. Email 4+: urgency.",
        },
        "linkedin_post": {
            "schema": {"post_variants": ["string"]},
            "guidance": "Hook stops the scroll. 150-250 words. Soft CTA.",
        },
        "google_search_ad": {
            "schema": {
                "headlines": ["string (max 30 chars)"],
                "descriptions": ["string (max 90 chars)"],
            },
            "guidance": "Front-load benefit. Specificity over generics.",
        },
        "sales_one_pager": {
            "schema": {
                "headline": "string",
                "who_its_for": "string",
                "problem": "string",
                "solution": "string",
                "key_benefits": ["string"],
                "capabilities": ["string"],
                "proof": ["string"],
                "cta": "string",
            },
            "guidance": "Scannable. Headline: concept. Problem: short pain. Solution: concept then mechanism.",
        },
    }
    entry = schema_map[req.asset_type]
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
    }
    return f"""
Create copy for asset_type="{req.asset_type}".
Guidance: {entry["guidance"]}
Schema: {json.dumps(entry["schema"], ensure_ascii=False, indent=2)}
Facts: {json.dumps(payload, ensure_ascii=False, indent=2)}
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
    text_for_score = json.dumps(obj, ensure_ascii=False)
    return obj, text_for_score


# ----------------------------
# API
# ----------------------------
app = FastAPI(title="On Time Edge Copy Bot", version="2.0")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0"}


@app.get("/triggers")
async def list_triggers():
    return {
        "count": len(SUGARMAN_TRIGGERS),
        "triggers": [
            {"id": t["id"], "name": t["name"], "description": t["description"]}
            for t in SUGARMAN_TRIGGERS
        ],
    }


@app.get("/openers")
async def list_openers(opener_type: Optional[str] = None):
    openers = get_openers(opener_type)
    return {
        "count": len(openers),
        "types": ["curiosity", "story", "contrast", "statistic", "direct_challenge"],
        "openers": openers,
    }


@app.get("/objections/{audience}")
async def get_objections(audience: str):
    key = _resolve_audience_key(audience)
    if key and key in AUDIENCE_OBJECTIONS:
        return {
            "audience": audience,
            "resolved_key": key,
            "objections": AUDIENCE_OBJECTIONS[key],
        }
    available = list(AUDIENCE_OBJECTIONS.keys())
    raise HTTPException(
        status_code=404,
        detail=f"Unknown audience '{audience}'. Available: {available}",
    )


@app.post("/generate", response_model=OTECopyResponse)
async def generate(req: OTECopyRequest):
    brand = load_brand_profile()

    if req.provider == "template":
        copy_obj, score_text = generate_template(req, brand)
    else:
        copy_obj, score_text = await generate_llm(req, brand)

    flat_text = score_text
    warnings = lint_copy(flat_text, brand, req)
    triggers = detect_triggers(flat_text)
    concept = extract_concept(flat_text)
    audience_objections = infer_objections(req.target_audience)
    objection_analysis = check_objections_addressed(flat_text, audience_objections)

    return OTECopyResponse(
        asset_type=req.asset_type,
        content=copy_obj,
        warnings=warnings,
        slippery_score=slippery_score(flat_text),
        triggers=triggers,
        concept=concept,
        objection_analysis=objection_analysis,
    )


@app.post("/refine", response_model=RefineResponse)
async def refine(req: RefineRequest):
    score_before = slippery_score(req.original_copy)
    triggers_before = len(detect_triggers(req.original_copy))

    if req.provider == "template":
        refined = refine_template(req.original_copy, req.feedback, req.target_audience)
    else:
        brand = load_brand_profile()
        messages = [
            {"role": "system", "content": build_system_prompt(brand)},
            {
                "role": "user",
                "content": (
                    f"Refine this copy based on the feedback.\n\n"
                    f"Original:\n{req.original_copy}\n\n"
                    f"Feedback:\n{req.feedback}\n\n"
                    f"Target audience: {req.target_audience}\n"
                    f"Asset type: {req.asset_type}\n\n"
                    f"Return the refined copy as plain text (not JSON)."
                ),
            },
        ]
        if req.provider == "ollama":
            refined = await call_ollama(messages, req.model, req.temperature)
        else:
            refined = await call_compatible(messages, req.model, req.temperature)

    score_after = slippery_score(refined)
    triggers_after = len(detect_triggers(refined))

    return RefineResponse(
        original_copy=req.original_copy,
        refined_copy=refined,
        feedback_applied=req.feedback,
        slippery_score_before=score_before,
        slippery_score_after=score_after,
        triggers_before=triggers_before,
        triggers_after=triggers_after,
    )


@app.post("/variants", response_model=VariantResponse)
async def variants(req: VariantRequest):
    brand = load_brand_profile()
    opener_types = ["curiosity", "story", "contrast", "statistic", "direct_challenge"]

    results: List[VariantResult] = []
    for i in range(req.num_variants):
        otype = opener_types[i % len(opener_types)]
        available = [o for o in OPENER_LIBRARY if o["type"] == otype]
        opener = random.choice(available)
        opener_text = render_opener(opener, req.target_audience)

        if req.provider == "template":
            content = generate_variant_with_opener(req, opener, brand)
            score_text = content.get("body", "")
        else:
            copy_req = OTECopyRequest(
                asset_type=req.asset_type,
                offer_name=req.offer_name,
                target_audience=req.target_audience,
                primary_outcome=req.primary_outcome,
                key_benefits=req.key_benefits,
                proof_points=req.proof_points,
                offer_details=req.offer_details,
                cta=req.cta,
                provider=req.provider,
                model=req.model,
                temperature=req.temperature,
            )
            content, score_text = await generate_llm(copy_req, brand)

        score = slippery_score(score_text)
        trigger_count = len(detect_triggers(score_text))

        results.append(
            VariantResult(
                variant_id=i + 1,
                opener_type=otype,
                opener_text=opener_text,
                content=content,
                slippery_score=score,
                trigger_count=trigger_count,
            )
        )

    best = max(results, key=lambda r: r.slippery_score + r.trigger_count * 2)
    scores = [
        f"V{r.variant_id} ({r.opener_type}): slide={r.slippery_score}, triggers={r.trigger_count}"
        for r in results
    ]

    return VariantResponse(
        variants=results,
        best_variant_id=best.variant_id,
        comparison_summary="Variant scores: " + " | ".join(scores),
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
        resp = await generate(sample)
        print(json.dumps(resp.model_dump(), ensure_ascii=False, indent=2))

    asyncio.run(run())
