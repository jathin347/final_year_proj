import pytest
import asyncio
from backend.app.services.text_analyzer import TextAnalyzer
from backend.app.services.claim_extractor import ClaimExtractor
from backend.app.services.source_credibility import SourceCredibilityAnalyzer
from backend.app.services.evidence_assessor import EvidenceAssessor
from backend.app.services.decision_fusion import DecisionFusionEngine
from backend.app.services.image_analyzer import ImageAnalyzer
from backend.app.api.schemas.evidence import FactCheckItem, NewsArticleItem

def test_text_analyzer_sensationalism_and_attribution():
    analyzer = TextAnalyzer()
    
    # Sensationalist text
    headline_fake = "SHOCKING TRUTH: DOCTORS DON'T WANT YOU TO KNOW THIS MIRACLE CURE!!"
    body_fake = "You won't believe what happens next. The secret cabal exposed!"
    res_fake = analyzer.analyze(headline_fake, body_fake)
    
    assert res_fake.prediction == "Elevated Misinformation Risk"
    assert res_fake.stylometric_signals["clickbait_detected"] is True
    assert res_fake.stylometric_signals["all_caps_word_ratio"] > 0.1
    assert any(t["token"] == "miracle" for t in res_fake.key_attribution_tokens)

    # Credible objective text
    headline_real = "Federal Reserve announces interest rate stabilization following inflation data"
    body_real = "According to official reports published by researchers, data shows steady economic growth."
    res_real = analyzer.analyze(headline_real, body_real)
    
    assert res_real.prediction == "Credible / Objective Phrasing"
    assert res_real.confidence >= 0.5
    assert res_real.stylometric_signals["attribution_density"] > 0.0

@pytest.mark.asyncio
async def test_claim_extractor_local_nlp():
    extractor = ClaimExtractor()
    headline = "WHO announces 40% reduction in global malaria cases by 2025"
    text = "In a press conference held on October 12, 2024 in Geneva, researchers confirmed significant progress."
    
    claims = await extractor.extract_claims(text, headline)
    assert len(claims) >= 1
    primary_claim = claims[0]
    assert "malaria" in primary_claim.claim_text.lower()
    assert primary_claim.importance == "HIGH"
    assert primary_claim.category in ("Health", "General")
    assert len(primary_claim.search_queries) > 0

def test_source_credibility_reputable_and_flagged():
    analyzer = SourceCredibilityAnalyzer()
    
    # Reputable news domain
    rep_report = analyzer.assess("https://www.reuters.com/world/article123", publisher_name="Reuters", author="Jane Doe")
    assert rep_report.overall_score is not None
    assert rep_report.overall_score >= 85.0
    assert rep_report.assessment_status == "Assessed"
    assert rep_report.domain == "reuters.com"

    # Flagged satire domain
    sat_report = analyzer.assess("https://theonion.com/article/funny-fake-story", publisher_name="The Onion")
    assert sat_report.overall_score is not None
    assert sat_report.overall_score <= 25.0
    assert sat_report.assessment_status == "Assessed"

    # Missing URL
    none_report = analyzer.assess(None)
    assert none_report.overall_score is None
    assert none_report.assessment_status == "Assessment unavailable"

def test_decision_fusion_rules():
    fusion_engine = DecisionFusionEngine()
    text_analyzer = TextAnalyzer()
    image_analyzer = ImageAnalyzer()
    source_analyzer = SourceCredibilityAnalyzer()

    # Rule 1: Direct Fact Check False Contradiction
    claim = ClaimExtractor()._extract_with_local_nlp("Drinking bleach cures virus")[0]
    fact_check = FactCheckItem(
        id="fc_test1",
        claim_reviewed="Drinking bleach cures virus",
        fact_checker_publisher="Snopes",
        review_title="Fact Check: Bleach does not cure virus",
        review_url="https://snopes.com/fact-check/bleach",
        original_rating="Pants on Fire",
        normalized_verdict="FALSE",
        retrieval_timestamp="2026-10-26T12:00:00Z"
    )
    
    text_analysis = text_analyzer.analyze("Drinking bleach cures virus", "")
    image_analysis = image_analyzer.analyze_image(None)
    source_report = source_analyzer.assess("https://random-blog.xyz")

    verdict_report = fusion_engine.fuse(
        claims=[claim],
        fact_checks=[fact_check],
        news_articles=[],
        source_report=source_report,
        text_analysis=text_analysis,
        image_analysis=image_analysis
    )

    assert verdict_report.final_assessment == "Contradicted by available evidence"
    assert verdict_report.contradicting_evidence_count >= 1
    assert verdict_report.uncertainty_level == "Low"
    assert "Rule 1" in verdict_report.decision_rules_applied[0]

def test_decision_fusion_insufficient_evidence():
    fusion_engine = DecisionFusionEngine()
    text_analyzer = TextAnalyzer()
    image_analyzer = ImageAnalyzer()
    source_analyzer = SourceCredibilityAnalyzer()

    text_analysis = text_analyzer.analyze("Some obscure local event occurred", "")
    image_analysis = image_analyzer.analyze_image(None)
    source_report = source_analyzer.assess(None)

    verdict_report = fusion_engine.fuse(
        claims=[],
        fact_checks=[],
        news_articles=[],
        source_report=source_report,
        text_analysis=text_analysis,
        image_analysis=image_analysis
    )

    assert verdict_report.final_assessment == "Insufficient evidence"
    assert verdict_report.evidence_coverage == "None"
    assert verdict_report.uncertainty_level == "High"
