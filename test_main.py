"""Test suite for On Time Edge Copy Bot v2.0."""
import pytest
from fastapi.testclient import TestClient

from main import (
    app,
    slippery_score,
    detect_triggers,
    extract_concept,
    infer_objections,
    check_objections_addressed,
    get_openers,
    render_opener,
    refine_template,
    lint_copy,
    OTECopyRequest,
    SUGARMAN_TRIGGERS,
    OPENER_LIBRARY,
    AUDIENCE_OBJECTIONS,
)

client = TestClient(app)

# ---- Health ----

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0"

# ---- Triggers endpoint ----

def test_triggers_endpoint():
    resp = client.get("/triggers")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 30
    assert len(data["triggers"]) == 30
    assert data["triggers"][0]["name"] == "Involvement"

# ---- Openers endpoint ----

def test_openers_all():
    resp = client.get("/openers")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == len(OPENER_LIBRARY)
    assert "curiosity" in data["types"]

def test_openers_filtered():
    resp = client.get("/openers?opener_type=story")
    assert resp.status_code == 200
    data = resp.json()
    assert all(o["type"] == "story" for o in data["openers"])

# ---- Objections endpoint ----

def test_objections_known_audience():
    resp = client.get("/objections/plant manager")
    assert resp.status_code == 200
    data = resp.json()
    assert data["resolved_key"] == "plant_manager"
    assert len(data["objections"]) > 0

def test_objections_unknown_audience():
    resp = client.get("/objections/unknown_role")
    assert resp.status_code == 404

# ---- Generate endpoint ----

SAMPLE_REQUEST = {
    "asset_type": "landing_hero",
    "offer_name": "On Time Edge APS Implementation",
    "target_audience": "plant managers",
    "primary_outcome": "a schedule that survives contact with reality",
    "key_benefits": ["Reduce rework", "Make constraints visible", "Align planning with execution"],
    "offer_details": "Book a 20-minute walkthrough.",
    "provider": "template",
}

def test_generate_landing_hero():
    resp = client.post("/generate", json=SAMPLE_REQUEST)
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_type"] == "landing_hero"
    assert "headline" in data["content"]
    assert data["slippery_score"] > 0
    assert "triggers" in data
    assert "concept" in data
    assert "objection_analysis" in data

def test_generate_email_single():
    req = {**SAMPLE_REQUEST, "asset_type": "email_single"}
    resp = client.post("/generate", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["asset_type"] == "email_single"
    assert "subject" in data["content"]
    assert "body" in data["content"]

def test_generate_linkedin_post():
    req = {**SAMPLE_REQUEST, "asset_type": "linkedin_post"}
    resp = client.post("/generate", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert "post" in data["content"]

# ---- Refine endpoint ----

def test_refine_adds_urgency():
    resp = client.post("/refine", json={
        "original_copy": "We help manufacturers schedule better.",
        "feedback": "Make it more urgent",
        "target_audience": "COO",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "Right now" in data["refined_copy"]
    assert data["slippery_score_after"] >= 0

def test_refine_adds_question():
    resp = client.post("/refine", json={
        "original_copy": "Plans break every week.",
        "feedback": "Open with a question",
        "target_audience": "Plant Manager",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "?" in data["refined_copy"]

# ---- Variants endpoint ----

def test_variants_returns_requested_count():
    resp = client.post("/variants", json={
        "asset_type": "email_single",
        "offer_name": "On Time Edge APS",
        "target_audience": "VP of Operations",
        "primary_outcome": "scheduling that works",
        "key_benefits": ["Reduce rework", "Visible constraints"],
        "offer_details": "Book a walkthrough.",
        "num_variants": 4,
        "provider": "template",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["variants"]) == 4
    assert data["best_variant_id"] >= 1

# ---- Unit tests: slippery score ----

def test_slippery_score_empty():
    assert slippery_score("") == 0.0

def test_slippery_score_short_opener():
    text = "Plans break. The schedule was solid Monday. By Wednesday everything changed."
    score = slippery_score(text)
    assert 40 < score < 100

def test_slippery_score_long_opener():
    text = "This is a very long opening sentence that goes on and on without stopping for quite some time and never gets to the point."
    score = slippery_score(text)
    assert score < 50

# ---- Unit tests: trigger detection ----

def test_detect_triggers_finds_involvement():
    triggers = detect_triggers("Your schedule is broken. You need a better plan.")
    names = [t["name"] for t in triggers]
    assert "Involvement" in names

def test_detect_triggers_finds_fear():
    triggers = detect_triggers("Firefighting is costing you money. The risk of inaction is real.")
    names = [t["name"] for t in triggers]
    assert "Fear" in names

def test_detect_triggers_empty():
    triggers = detect_triggers("")
    assert triggers == []

# ---- Unit tests: concept extraction ----

def test_extract_concept_constraints():
    concept = extract_concept("Constraints drive your schedule. Bottleneck management improves throughput.")
    assert concept["primary_concept"] == "Constraint Management"
    assert concept["strength"] > 0

def test_extract_concept_empty():
    concept = extract_concept("Hello world.")
    assert concept["primary_concept"] == "none_detected"

# ---- Unit tests: objection detection ----

def test_infer_objections_plant_manager():
    objs = infer_objections("Plant Manager at a food company")
    assert len(objs) > 0
    assert any("team" in o["objection"].lower() or "shelf" in o["objection"].lower() for o in objs)

def test_infer_objections_unknown_defaults():
    objs = infer_objections("random_role")
    assert len(objs) > 0  # defaults to vp_ops

def test_check_objections_addressed():
    text = "We know adoption is the real problem. That's why we start with your actual constraints, not a demo."
    objs = [{"objection": "We already have a planning tool — adoption is the problem.", "rebuttal_hint": "Address adoption."}]
    results = check_objections_addressed(text, objs)
    assert results[0]["addressed"] is True

# ---- Unit tests: opener library ----

def test_get_openers_all():
    openers = get_openers()
    assert len(openers) == len(OPENER_LIBRARY)

def test_get_openers_filtered():
    openers = get_openers("contrast")
    assert all(o["type"] == "contrast" for o in openers)
    assert len(openers) >= 3

def test_render_opener_replaces_audience():
    opener = {"type": "curiosity", "template": "Here's what nobody tells {audience} about scheduling.", "id": "cur_01"}
    result = render_opener(opener, "COOs")
    assert "COOs" in result
    assert "{audience}" not in result

# ---- Unit tests: refinement ----

def test_refine_template_urgency():
    result = refine_template("Plans break.", "Make it more urgent", "VP of Operations")
    assert "Right now" in result

def test_refine_template_proof():
    result = refine_template("Plans break.", "Add more proof", "COO")
    assert "1,000+" in result

def test_refine_template_no_change():
    original = "Plans break."
    result = refine_template(original, "something unrecognized", "COO")
    assert result == original

# ---- Unit tests: linting ----

def test_lint_catches_banned_term():
    req = OTECopyRequest(
        offer_name="Test", target_audience="test", primary_outcome="test",
        key_benefits=["test"], offer_details="test",
    )
    brand = {"do_not_say": ["IED-Net"]}
    warnings = lint_copy("Check out IED-Net today!", brand, req)
    assert any("Banned term" in w for w in warnings)

def test_lint_catches_risky_phrase():
    req = OTECopyRequest(
        offer_name="Test", target_audience="test", primary_outcome="test",
        key_benefits=["test"], offer_details="test",
    )
    warnings = lint_copy("We are the best in the industry, guaranteed.", {}, req)
    assert any("guaranteed" in w for w in warnings)
    assert any("best" in w for w in warnings)
