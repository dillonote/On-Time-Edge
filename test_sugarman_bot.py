"""
Evaluation test suite for the On Time Edge "Sugarman Bot" — the copy-generation
service built on Joseph Sugarman's direct-response (slippery-slide) methodology.

Tests cover:
  1. slippery_score() heuristic scoring
  2. lint_copy() guardrail validation
  3. Template generators (landing_hero, email_single, linkedin_post, fallback)
  4. API endpoint (/generate)
  5. Edge cases and regressions
"""

import pytest
from fastapi.testclient import TestClient

from main import (
    CURIOSITY_SEEDS,
    DEFAULT_BRAND_PROFILE,
    OTECopyRequest,
    _sentences,
    _word_count,
    app,
    build_system_prompt,
    build_user_prompt,
    generate_template,
    lint_copy,
    load_brand_profile,
    slippery_score,
    template_email_single,
    template_landing_hero,
    template_linkedin_post,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def brand():
    return dict(DEFAULT_BRAND_PROFILE)


@pytest.fixture
def sample_request():
    return OTECopyRequest(
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
        cta="Book a demo",
        provider="template",
    )


@pytest.fixture
def client():
    return TestClient(app)


# ===================================================================
# 1. slippery_score() — Sugarman heuristic scoring
# ===================================================================


class TestSlipperyScore:
    """Validate the 0-100 scoring function against known copy patterns."""

    def test_empty_text_returns_zero(self):
        assert slippery_score("") == 0.0
        assert slippery_score("   ") == 0.0

    def test_score_in_range(self):
        text = "Plans break. You know this. Here's the thing: we fix it."
        score = slippery_score(text)
        assert 0.0 <= score <= 100.0

    def test_short_opener_scores_high(self):
        """First sentence <=5 words should earn the full 20-pt opener bonus."""
        short_opener = (
            "Plans break. Your team scrambles to catch up with shifting constraints. "
            "And schedules fall apart by midweek."
        )
        long_opener = (
            "Your team scrambles to catch up with shifting constraints every single week. "
            "Plans break. And schedules fall apart by midweek."
        )
        # Same content, different opener length — short opener should win
        assert slippery_score(short_opener) > slippery_score(long_opener)

    def test_rhythm_variety_rewarded(self):
        """Copy with varied sentence lengths should outscore monotone copy."""
        varied = (
            "Plans break. You know this already from bitter experience. "
            "Fix it. On Time Edge builds schedules that survive contact with reality."
        )
        monotone = (
            "Plans break sometimes. Schedules change often. Teams scramble daily. "
            "Leaders get frustrated. Tools go unused. Meetings drag forever."
        )
        assert slippery_score(varied) > slippery_score(monotone)

    def test_curiosity_seeds_boost_score(self):
        """Bucket-brigade phrases should contribute to the curiosity component."""
        with_seeds = (
            "Plans break. But here's the thing: they don't have to. "
            "Truth is, most schedules fail for one simple reason. "
            "Let me explain."
        )
        without_seeds = (
            "Plans break. They do not have to though. "
            "Most schedules fail for one simple reason. "
            "The reason is poor constraint modeling."
        )
        assert slippery_score(with_seeds) > slippery_score(without_seeds)

    def test_ideal_copy_scores_above_70(self):
        """Well-crafted Sugarman-style copy should score above 70."""
        ideal = (
            "Plans break. You know this. "
            "By Wednesday the schedule is already outdated. "
            "But here's the thing: it doesn't have to be that way. "
            "Fix the constraints. Align the team. Execute."
        )
        assert slippery_score(ideal) >= 70.0

    def test_very_long_sentences_penalized(self):
        """Copy with many >24-word sentences should score lower on compression."""
        long_winded = (
            "In today's rapidly evolving manufacturing landscape organizations face "
            "unprecedented challenges that require sophisticated approaches to scheduling "
            "and supply chain management across multiple plants and facilities. "
            "The complexity of modern production environments demands that operations "
            "leaders adopt new methodologies and frameworks to address the root causes "
            "of disruption and maintain operational excellence throughout the enterprise."
        )
        assert slippery_score(long_winded) < 50.0

    def test_single_sentence_neutral(self):
        """A single sentence should still produce a valid score."""
        score = slippery_score("Plans break.")
        assert 0.0 <= score <= 100.0

    def test_score_is_deterministic(self):
        text = "Plans break. You know this. But here's the thing."
        assert slippery_score(text) == slippery_score(text)


# ===================================================================
# 2. lint_copy() — guardrail validation
# ===================================================================


class TestLintCopy:
    """Verify the guardrail/linting system catches violations."""

    def test_banned_term_from_brand(self, brand, sample_request):
        text = "Our IED-Net platform delivers results."
        warnings = lint_copy(text, brand, sample_request)
        assert any("ied-net" in w.lower() for w in warnings)

    def test_banned_term_from_request(self, brand, sample_request):
        sample_request.banned_terms = ["chaos"]
        text = "Without adding chaos to your day."
        warnings = lint_copy(text, brand, sample_request)
        assert any("chaos" in w.lower() for w in warnings)

    def test_required_phrase_present(self, brand, sample_request):
        sample_request.required_phrases = ["On Time Edge"]
        text = "On Time Edge helps you schedule better."
        warnings = lint_copy(text, brand, sample_request)
        assert not any("required phrase" in w.lower() for w in warnings)

    def test_required_phrase_missing(self, brand, sample_request):
        sample_request.required_phrases = ["On Time Edge"]
        text = "Our platform helps you schedule better."
        warnings = lint_copy(text, brand, sample_request)
        assert any("on time edge" in w.lower() for w in warnings)

    def test_invented_stat_flagged(self, brand, sample_request):
        """Stats not in proof_points should trigger a warning."""
        sample_request.proof_points = []
        text = "We deliver 50% improvement in scheduling accuracy."
        warnings = lint_copy(text, brand, sample_request)
        assert any("invented stat" in w.lower() or "50%" in w for w in warnings)

    def test_known_stat_not_flagged(self, brand, sample_request):
        """Stats present in proof_points should NOT trigger a warning."""
        sample_request.proof_points = [
            "90-day time-to-first-value implementation target"
        ]
        text = "We target 90-day time-to-first-value."
        warnings = lint_copy(text, brand, sample_request)
        stat_warnings = [w for w in warnings if "invented stat" in w.lower()]
        assert len(stat_warnings) == 0

    def test_absolute_claim_warning(self, brand, sample_request):
        for phrase in [
            "guaranteed",
            "always",
            "never",
            "best",
            "number one",
            "industry-leading",
        ]:
            text = f"We are {phrase} in the market."
            warnings = lint_copy(text, brand, sample_request)
            assert any(
                "over-absolute" in w.lower() or phrase in w.lower() for w in warnings
            ), f"Expected warning for absolute claim '{phrase}'"

    def test_clean_copy_no_warnings(self, brand, sample_request):
        """Clean, factual copy should produce zero warnings."""
        text = (
            "Plans break. On Time Edge helps manufacturing schedulers turn "
            "constraints into a plan teams can actually run."
        )
        sample_request.banned_terms = []
        sample_request.required_phrases = []
        warnings = lint_copy(text, brand, sample_request)
        assert warnings == []


# ===================================================================
# 3. Template generators
# ===================================================================


class TestTemplates:
    """Evaluate quality and structure of template-based copy."""

    def test_landing_hero_structure(self, sample_request, brand):
        out = template_landing_hero(sample_request, brand)
        assert "headline" in out
        assert "subhead" in out
        assert "bullets" in out
        assert "cta" in out
        assert "cta_secondary" in out

    def test_landing_hero_headline_is_short(self, sample_request, brand):
        """Sugarman: headline should start with a punchy short phrase."""
        out = template_landing_hero(sample_request, brand)
        assert out["headline"].startswith("Plans break.")

    def test_landing_hero_includes_brand(self, sample_request, brand):
        out = template_landing_hero(sample_request, brand)
        assert brand["brand_name"] in out["subhead"]

    def test_landing_hero_bullets_match_benefits(self, sample_request, brand):
        out = template_landing_hero(sample_request, brand)
        assert len(out["bullets"]) == len(sample_request.key_benefits[:5])
        for bullet in out["bullets"]:
            assert bullet in sample_request.key_benefits

    def test_landing_hero_proof_line(self, sample_request, brand):
        out = template_landing_hero(sample_request, brand)
        assert out["proof_line"]  # non-empty when proof_points provided
        for pp in sample_request.proof_points[:3]:
            assert pp in out["proof_line"]

    def test_landing_hero_no_proof_if_empty(self, sample_request, brand):
        sample_request.proof_points = []
        out = template_landing_hero(sample_request, brand)
        assert out["proof_line"] == ""

    def test_email_single_structure(self, sample_request, brand):
        sample_request.asset_type = "email_single"
        out = template_email_single(sample_request, brand)
        assert "subject" in out
        assert "body" in out

    def test_email_single_short_opener(self, sample_request, brand):
        """Sugarman: email body starts with 2-7 word opener."""
        out = template_email_single(sample_request, brand)
        first_sentence = _sentences(out["body"])[0]
        assert _word_count(first_sentence) <= 7

    def test_email_single_curiosity_seeds(self, sample_request, brand):
        """Email body should contain at least one bucket-brigade transition."""
        out = template_email_single(sample_request, brand)
        assert CURIOSITY_SEEDS.search(out["body"])

    def test_email_single_contains_cta(self, sample_request, brand):
        out = template_email_single(sample_request, brand)
        assert sample_request.cta in out["body"]

    def test_email_single_contains_objections_when_provided(
        self, sample_request, brand
    ):
        out = template_email_single(sample_request, brand)
        # The objection block should be present
        assert "thinking" in out["body"].lower() or any(
            o.lower() in out["body"].lower() for o in sample_request.objections[:2]
        )

    def test_email_single_no_objections_when_empty(self, sample_request, brand):
        sample_request.objections = []
        out = template_email_single(sample_request, brand)
        assert "You might be thinking" not in out["body"]

    def test_linkedin_post_structure(self, sample_request, brand):
        sample_request.asset_type = "linkedin_post"
        out = template_linkedin_post(sample_request, brand)
        assert "post" in out

    def test_linkedin_post_short_hook(self, sample_request, brand):
        """Sugarman: LinkedIn hook should stop the scroll with a short first line."""
        out = template_linkedin_post(sample_request, brand)
        first_line = out["post"].split("\n")[0]
        assert _word_count(first_line) <= 10

    def test_linkedin_post_has_curiosity(self, sample_request, brand):
        out = template_linkedin_post(sample_request, brand)
        assert CURIOSITY_SEEDS.search(out["post"])

    def test_linkedin_post_includes_cta(self, sample_request, brand):
        out = template_linkedin_post(sample_request, brand)
        assert sample_request.cta in out["post"]


class TestGenerateTemplate:
    """Test the generate_template() dispatcher."""

    def test_landing_hero_dispatch(self, sample_request, brand):
        sample_request.asset_type = "landing_hero"
        out, text = generate_template(sample_request, brand)
        assert "headline" in out
        assert isinstance(text, str) and len(text) > 0

    def test_email_single_dispatch(self, sample_request, brand):
        sample_request.asset_type = "email_single"
        out, text = generate_template(sample_request, brand)
        assert "subject" in out
        assert text == out["body"]

    def test_linkedin_post_dispatch(self, sample_request, brand):
        sample_request.asset_type = "linkedin_post"
        out, text = generate_template(sample_request, brand)
        assert "post" in out
        assert text == out["post"]

    def test_fallback_for_unsupported_asset(self, sample_request, brand):
        """Asset types without dedicated templates should get the fallback."""
        sample_request.asset_type = "sales_one_pager"
        out, text = generate_template(sample_request, brand)
        assert "headline" in out
        assert "body" in out
        assert "cta" in out


# ===================================================================
# 4. API endpoint (/generate)
# ===================================================================


class TestGenerateEndpoint:
    """Integration tests for the POST /generate endpoint."""

    def test_landing_hero_success(self, client, sample_request):
        resp = client.post("/generate", json=sample_request.model_dump())
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset_type"] == "landing_hero"
        assert "headline" in data["content"]
        assert isinstance(data["slippery_score"], (int, float))
        assert 0 <= data["slippery_score"] <= 100

    def test_email_single_success(self, client, sample_request):
        payload = sample_request.model_dump()
        payload["asset_type"] = "email_single"
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["asset_type"] == "email_single"
        assert "subject" in data["content"]
        assert "body" in data["content"]

    def test_linkedin_post_success(self, client, sample_request):
        payload = sample_request.model_dump()
        payload["asset_type"] = "linkedin_post"
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "post" in data["content"]

    def test_response_has_warnings_field(self, client, sample_request):
        resp = client.post("/generate", json=sample_request.model_dump())
        data = resp.json()
        assert "warnings" in data
        assert isinstance(data["warnings"], list)

    def test_banned_term_triggers_warning_via_api(self, client, sample_request):
        """The /generate endpoint should surface lint warnings in the response."""
        # The default brand bans "IED-Net", but template output doesn't include it.
        # We can verify the pipeline by adding a required_phrases check instead.
        payload = sample_request.model_dump()
        payload["required_phrases"] = ["DOES_NOT_EXIST_PHRASE"]
        resp = client.post("/generate", json=payload)
        data = resp.json()
        assert any("required phrase" in w.lower() for w in data["warnings"])

    def test_invalid_asset_type_rejected(self, client, sample_request):
        payload = sample_request.model_dump()
        payload["asset_type"] = "nonexistent_type"
        resp = client.post("/generate", json=payload)
        assert resp.status_code == 422  # Pydantic validation error

    def test_missing_required_fields(self, client):
        resp = client.post("/generate", json={"asset_type": "landing_hero"})
        assert resp.status_code == 422


# ===================================================================
# 5. Edge cases and regressions
# ===================================================================


class TestHelpers:
    """Unit tests for internal helper functions."""

    def test_sentences_split(self):
        text = "Plans break. You know this! Do you? Yes."
        sents = _sentences(text)
        assert len(sents) == 4

    def test_sentences_empty_string(self):
        assert _sentences("") == []

    def test_sentences_no_terminal_punctuation(self):
        """Text without sentence-ending punctuation returns as one chunk."""
        sents = _sentences("No punctuation here")
        assert len(sents) == 1

    def test_word_count(self):
        assert _word_count("Plans break.") == 2
        assert _word_count("one two three four five") == 5
        assert _word_count("") == 0


class TestCuriositySeeds:
    """Verify the curiosity-seed regex matches expected phrases."""

    @pytest.mark.parametrize(
        "phrase",
        [
            "But here's the thing",
            "But there's more",
            "Let me explain",
            "Here's the deal",
            "Here's why",
            "Now here comes",
            "Read on",
            "And yet",
            "Truth is",
            "Turns out",
            "Look,",
            "Here's the thing",
            "So,",
            "You see",
        ],
    )
    def test_known_seeds_detected(self, phrase):
        assert CURIOSITY_SEEDS.search(phrase), (
            f"'{phrase}' should match CURIOSITY_SEEDS"
        )


class TestBrandProfile:
    """Verify brand profile loading and defaults."""

    def test_default_profile_has_required_keys(self):
        profile = load_brand_profile()
        for key in [
            "brand_name",
            "tagline",
            "identity",
            "voice",
            "audience",
            "positioning",
            "do_not_say",
            "safe_words",
        ]:
            assert key in profile

    def test_default_brand_name(self):
        assert load_brand_profile()["brand_name"] == "On Time Edge"


class TestSystemPrompt:
    """Verify the system prompt encodes Sugarman principles correctly."""

    def test_prompt_mentions_sugarman(self, brand):
        prompt = build_system_prompt(brand)
        assert "sugarman" in prompt.lower()

    def test_prompt_contains_guardrails(self, brand):
        prompt = build_system_prompt(brand)
        assert "FACTUAL GUARDRAILS" in prompt

    def test_prompt_lists_banned_terms(self, brand):
        prompt = build_system_prompt(brand)
        for term in brand["do_not_say"]:
            assert term in prompt

    def test_prompt_mentions_slippery_slide(self, brand):
        prompt = build_system_prompt(brand)
        assert "SLIPPERY-SLIDE" in prompt

    def test_prompt_has_twelve_principles(self, brand):
        prompt = build_system_prompt(brand)
        for i in range(1, 13):
            assert f"{i}." in prompt, f"Principle #{i} not found in system prompt"


class TestUserPrompt:
    """Verify user prompt construction for each asset type."""

    @pytest.mark.parametrize(
        "asset_type",
        [
            "landing_hero",
            "landing_sections",
            "email_single",
            "email_sequence",
            "linkedin_post",
            "google_search_ad",
            "sales_one_pager",
        ],
    )
    def test_user_prompt_for_each_asset_type(self, sample_request, asset_type):
        sample_request.asset_type = asset_type
        prompt = build_user_prompt(sample_request)
        assert asset_type in prompt
        assert "STRICT JSON" in prompt
        assert sample_request.offer_name in prompt


class TestSlipperyScoreEdgeCases:
    """Additional edge-case tests for the scoring function."""

    def test_all_short_sentences(self):
        """All <=5-word sentences: max opener, but monotone rhythm."""
        text = "Plans break. Fix them. Start now. Do it. Win big."
        score = slippery_score(text)
        assert 30.0 <= score <= 80.0  # Good opener/compression, weak rhythm

    def test_only_curiosity_seeds(self):
        """Text that's mostly bucket brigades."""
        text = "But here's the thing. Truth is, it works. And yet, they don't see it. Look, just try."
        score = slippery_score(text)
        assert score > 0.0

    def test_extremely_long_text(self):
        """Long text should not crash or produce out-of-range scores."""
        text = (
            ". ".join(["This is sentence number " + str(i) for i in range(200)]) + "."
        )
        score = slippery_score(text)
        assert 0.0 <= score <= 100.0


class TestTemplateScoreQuality:
    """
    Evaluate that the built-in templates themselves score well on the
    Sugarman slippery-slide metric — the bot should practice what it preaches.
    """

    def test_landing_hero_score(self, sample_request, brand):
        _, text = generate_template(sample_request, brand)
        score = slippery_score(text)
        assert score >= 50.0, f"Landing hero scored only {score}/100"

    def test_email_single_score(self, sample_request, brand):
        sample_request.asset_type = "email_single"
        _, text = generate_template(sample_request, brand)
        score = slippery_score(text)
        assert score >= 50.0, f"Email single scored only {score}/100"

    def test_linkedin_post_score(self, sample_request, brand):
        sample_request.asset_type = "linkedin_post"
        _, text = generate_template(sample_request, brand)
        score = slippery_score(text)
        assert score >= 50.0, f"LinkedIn post scored only {score}/100"

    def test_templates_pass_own_lint(self, sample_request, brand):
        """Every template should produce zero lint warnings with standard inputs."""
        for asset in ["landing_hero", "email_single", "linkedin_post"]:
            sample_request.asset_type = asset
            _, text = generate_template(sample_request, brand)
            warnings = lint_copy(text, brand, sample_request)
            assert warnings == [], f"{asset} template produced warnings: {warnings}"
