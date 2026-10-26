import time
from fastapi import APIRouter, HTTPException
from backend.app.api.schemas.claims import ClaimExtractionRequest, ClaimExtractionResponse
from backend.app.api.schemas.evidence import (
    FactCheckSearchRequest,
    NewsSearchRequest,
    FactCheckItem,
    NewsArticleItem
)
from backend.app.services.claim_extractor import ClaimExtractor
from backend.app.services.fact_check_service import FactCheckService
from backend.app.services.news_search_service import NewsSearchService

router = APIRouter(tags=["Claims & Evidence"])

claim_extractor = ClaimExtractor()
fact_check_service = FactCheckService()
news_search_service = NewsSearchService()

@router.post("/claims/extract", response_model=ClaimExtractionResponse)
async def extract_claims_endpoint(request: ClaimExtractionRequest):
    """Extract checkable factual statements from article text and headline."""
    start_time = time.time()
    claims = await claim_extractor.extract_claims(request.text, request.headline)
    elapsed_ms = (time.time() - start_time) * 1000.0

    method = "Gemini LLM" if claim_extractor.gemini_key else "Local Heuristic NLP Extractor"

    return ClaimExtractionResponse(
        claims=claims,
        count=len(claims),
        source_method=method,
        extraction_time_ms=round(elapsed_ms, 2)
    )

@router.post("/fact-check/search", response_model=list[FactCheckItem])
async def search_fact_checks_endpoint(request: FactCheckSearchRequest):
    """Direct search of Google Fact Check Tools API for claims."""
    return await fact_check_service.search_claims(request.query, request.language_code or "en")

@router.post("/news/search", response_model=list[NewsArticleItem])
async def search_news_endpoint(request: NewsSearchRequest):
    """Direct search of GDELT 2.0 DOC API for news reporting."""
    return await news_search_service.search_news(request.query, request.max_records or 10)
