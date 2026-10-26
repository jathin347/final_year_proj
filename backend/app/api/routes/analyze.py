import time
import asyncio
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.entities import AnalysisRecord
from backend.app.repositories.analysis_repository import AnalysisRepository
from backend.app.api.schemas.analysis import AnalysisResponse, TextModelAnalysis, ImageModelAnalysis, DecisionFusionReport
from backend.app.api.schemas.evidence import SourceCredibilityReport
from backend.app.services.article_extractor import ArticleExtractor, ArticleExtractionException
from backend.app.services.text_analyzer import TextAnalyzer
from backend.app.services.image_analyzer import ImageAnalyzer
from backend.app.services.claim_extractor import ClaimExtractor
from backend.app.services.fact_check_service import FactCheckService
from backend.app.services.news_search_service import NewsSearchService
from backend.app.services.evidence_assessor import EvidenceAssessor
from backend.app.services.source_credibility import SourceCredibilityAnalyzer
from backend.app.services.decision_fusion import DecisionFusionEngine
from backend.app.core.config import settings
from backend.app.core.logging import logger

router = APIRouter(tags=["Analysis"])

# Service singletons
article_extractor = ArticleExtractor()
text_analyzer = TextAnalyzer()
image_analyzer = ImageAnalyzer()
claim_extractor = ClaimExtractor()
fact_check_service = FactCheckService()
news_search_service = NewsSearchService()
evidence_assessor = EvidenceAssessor()
source_credibility_analyzer = SourceCredibilityAnalyzer()
decision_fusion_engine = DecisionFusionEngine()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_news_item(
    url: Optional[str] = Form(None),
    headline: Optional[str] = Form(None),
    article_text: Optional[str] = Form(None),
    user_context: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Main Real-Time Verification Orchestration Endpoint:
    Executes the end-to-end multi-stage pipeline:
    1. Input validation & SSRF protection
    2. Article extraction & metadata parsing
    3. AI stylometric text analysis
    4. Safe multimodal image analysis
    5. Factual claim extraction
    6. Live Google Fact Check retrieval
    7. Live GDELT news search & deduplication
    8. Claim-evidence stance matching
    9. Transparent source credibility scoring
    10. Epistemic decision fusion
    11. SQLite audit persistence
    """
    total_start_time = time.time()
    latencies = {}
    provider_status = {}

    # 1. Input Validation
    if not url and not headline and not article_text:
        raise HTTPException(
            status_code=400,
            detail="At least one input parameter (article URL, headline, or article text) must be provided."
        )

    # 2. Article Extraction
    extracted_headline = headline or ""
    extracted_body = article_text or ""
    domain = None
    publisher = None
    author = None
    published_date = None

    t0 = time.time()
    if url:
        try:
            art_data = await article_extractor.extract_from_url(url)
            domain = art_data.get("domain")
            publisher = art_data.get("publisher")
            author = art_data.get("author")
            published_date = art_data.get("published_date")
            
            # Use extracted text if user didn't manually supply
            if not extracted_headline:
                extracted_headline = art_data.get("headline", "")
            if not extracted_body:
                extracted_body = art_data.get("article_text", "")
                
            provider_status["article_extractor"] = "SUCCESS"
        except ArticleExtractionException as aee:
            logger.warning(f"Article extraction warning: {str(aee)}")
            provider_status["article_extractor"] = f"FAILED: {str(aee)}"
            if not extracted_headline and not extracted_body:
                raise HTTPException(status_code=422, detail=str(aee))
    latencies["article_extraction_ms"] = round((time.time() - t0) * 1000.0, 2)

    # Fallback headline
    if not extracted_headline and extracted_body:
        extracted_headline = extracted_body[:100].strip() + ("..." if len(extracted_body) > 100 else "")

    # 3. Safe Multimodal Image Analysis
    t0 = time.time()
    image_bytes = None
    if image:
        try:
            image_bytes = await image.read()
        except Exception as e:
            logger.warning(f"Failed to read image stream: {str(e)}")
            
    image_result = image_analyzer.analyze_image(image_bytes, extracted_headline, extracted_body)
    latencies["image_analysis_ms"] = round((time.time() - t0) * 1000.0, 2)
    provider_status["image_analyzer"] = "SUCCESS" if image_result.has_image else "NO_IMAGE_PROVIDED"

    # 4. AI Stylometric Text Analysis
    t0 = time.time()
    text_analysis = text_analyzer.analyze(extracted_headline, extracted_body)
    latencies["text_model_ms"] = round((time.time() - t0) * 1000.0, 2)
    provider_status["text_model"] = "SUCCESS"

    # 5. Factual Claim Extraction
    t0 = time.time()
    claims = await claim_extractor.extract_claims(extracted_body, extracted_headline)
    latencies["claim_extraction_ms"] = round((time.time() - t0) * 1000.0, 2)
    provider_status["claim_extractor"] = "GEMINI_API" if settings.has_gemini_key else "LOCAL_NLP_FALLBACK"

    # 6. Live Evidence Retrieval (Google Fact Check & GDELT News)
    # Search for each extracted claim's primary query (or headline if no claims)
    t0 = time.time()
    fact_checks = []
    news_articles = []
    
    search_queries = []
    if claims:
        for c in claims[:3]: # Limit to top 3 claims
            for q in c.search_queries[:2]:
                if q and q not in search_queries:
                    search_queries.append(q)
    elif extracted_headline:
        search_queries.append(extracted_headline)

    # Asynchronous parallel retrieval for Fact Check and News
    async def fetch_fc():
        all_fc = []
        for q in search_queries:
            results = await fact_check_service.search_claims(q)
            all_fc.extend(results)
        return all_fc

    async def fetch_news():
        all_news = []
        for q in search_queries:
            results = await news_search_service.search_news(q, max_records=6)
            all_news.extend(results)
        return all_news

    fc_results, news_results = await asyncio.gather(fetch_fc(), fetch_news(), return_exceptions=True)

    if isinstance(fc_results, list):
        fact_checks = fc_results
        provider_status["google_fact_check"] = "ACTIVE" if settings.has_fact_check_key else "UNCONFIGURED_EMPTY"
    else:
        logger.error(f"Fact check retrieval error: {str(fc_results)}")
        provider_status["google_fact_check"] = f"ERROR: {str(fc_results)}"

    if isinstance(news_results, list):
        news_articles = news_results
        provider_status["gdelt_news"] = "ACTIVE"
    else:
        logger.error(f"GDELT news retrieval error: {str(news_results)}")
        provider_status["gdelt_news"] = f"ERROR: {str(news_results)}"

    latencies["evidence_retrieval_ms"] = round((time.time() - t0) * 1000.0, 2)

    # 7. Claim-Evidence Matching Engine
    t0 = time.time()
    updated_claims = evidence_assessor.match_claims_with_evidence(claims, fact_checks, news_articles)
    latencies["claim_matching_ms"] = round((time.time() - t0) * 1000.0, 2)

    # 8. Source Credibility Assessment
    t0 = time.time()
    source_report = source_credibility_analyzer.assess(url, publisher, author)
    latencies["source_assessment_ms"] = round((time.time() - t0) * 1000.0, 2)
    provider_status["source_credibility"] = source_report.assessment_status

    # 9. Decision Fusion
    t0 = time.time()
    fusion_report = decision_fusion_engine.fuse(
        updated_claims,
        fact_checks,
        news_articles,
        source_report,
        text_analysis,
        image_result
    )
    latencies["decision_fusion_ms"] = round((time.time() - t0) * 1000.0, 2)

    total_latency_ms = round((time.time() - total_start_time) * 1000.0, 2)
    retrieval_time = datetime.now(timezone.utc).isoformat()

    # 10. Persistence
    repo = AnalysisRepository(db)
    record = AnalysisRecord(
        article_url=url,
        headline=extracted_headline,
        article_summary=(extracted_body[:300] + "...") if len(extracted_body) > 300 else extracted_body,
        publisher=publisher or source_report.publisher_name,
        domain=domain or source_report.domain,
        author=author,
        published_date=published_date,
        input_type="multimodal" if image_result.has_image else ("url" if url else "text"),
        has_image=1 if image_result.has_image else 0,
        final_assessment=fusion_report.final_assessment,
        assessment_explanation=fusion_report.explanation,
        uncertainty_level=fusion_report.uncertainty_level,
        source_credibility_score=source_report.overall_score,
        source_assessment_status=source_report.assessment_status,
        text_model_prediction=text_analysis.prediction,
        text_model_confidence=text_analysis.confidence,
        image_text_relevance=image_result.image_text_relevance_score,
        image_analysis_summary=image_result.visual_context_summary,
        extracted_claims=[c.model_dump() for c in updated_claims],
        fact_check_results=[fc.model_dump() for fc in fact_checks],
        news_search_results=[na.model_dump() for na in news_articles],
        source_credibility_breakdown=source_report.model_dump(),
        decision_factors=fusion_report.model_dump(),
        latency_breakdown_ms=latencies,
        total_latency_ms=total_latency_ms,
        status="COMPLETED",
        provider_status=provider_status,
        retrieval_timestamp=retrieval_time
    )
    saved = repo.create(record)

    return AnalysisResponse(
        id=saved.id,
        headline=extracted_headline,
        article_url=url,
        publisher=publisher or source_report.publisher_name,
        domain=domain or source_report.domain,
        author=author,
        published_date=published_date,
        article_summary=record.article_summary,
        final_assessment=fusion_report.final_assessment,
        assessment_explanation=fusion_report.explanation,
        uncertainty_level=fusion_report.uncertainty_level,
        claims=updated_claims,
        fact_checks=fact_checks,
        news_articles=news_articles,
        source_credibility=source_report,
        text_analysis=text_analysis,
        image_analysis=image_result,
        decision_fusion=fusion_report,
        status="COMPLETED",
        provider_status=provider_status,
        latency_breakdown_ms=latencies,
        total_latency_ms=total_latency_ms,
        retrieval_timestamp=retrieval_time,
        created_at=saved.created_at.isoformat()
    )
