from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import math
from backend.app.models.database import get_db
from backend.app.repositories.analysis_repository import AnalysisRepository
from backend.app.api.schemas.analysis import (
    AnalysisResponse,
    PaginatedHistoryResponse,
    AnalysisHistorySummary
)

router = APIRouter(tags=["History & Reports"])

@router.get("/history", response_model=PaginatedHistoryResponse)
def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Retrieves paginated verification history."""
    repo = AnalysisRepository(db)
    items, total = repo.list_paginated(page=page, page_size=page_size)

    summaries = [
        AnalysisHistorySummary(
            id=item.id,
            headline=item.headline,
            article_url=item.article_url,
            domain=item.domain,
            final_assessment=item.final_assessment,
            source_credibility_score=item.source_credibility_score,
            total_latency_ms=item.total_latency_ms,
            created_at=item.created_at.isoformat() if item.created_at else ""
        )
        for item in items
    ]

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedHistoryResponse(
        items=summaries,
        total=total,
        page=page,
        page_size=page_size,
        pages=total_pages
    )

@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_by_id(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieves a full analysis report by ID."""
    repo = AnalysisRepository(db)
    record = repo.get_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Analysis report '{analysis_id}' not found.")

    return AnalysisResponse(
        id=record.id,
        headline=record.headline,
        article_url=record.article_url,
        publisher=record.publisher,
        domain=record.domain,
        author=record.author,
        published_date=record.published_date,
        article_summary=record.article_summary,
        final_assessment=record.final_assessment,
        assessment_explanation=record.assessment_explanation,
        uncertainty_level=record.uncertainty_level or "Moderate",
        claims=record.extracted_claims or [],
        fact_checks=record.fact_check_results or [],
        news_articles=record.news_search_results or [],
        source_credibility=record.source_credibility_breakdown or {
            "assessment_status": record.source_assessment_status or "Assessment unavailable",
            "overall_score": record.source_credibility_score,
            "factors": [],
            "missing_signals": []
        },
        text_analysis={
            "model_name": "Veritas-Stylistic-Ensemble",
            "model_version": "1.2.0",
            "prediction": record.text_model_prediction or "Inconclusive",
            "confidence": record.text_model_confidence or 0.5,
            "stylometric_signals": {},
            "key_attribution_tokens": [],
            "inference_time_ms": 0.0
        },
        image_analysis={
            "has_image": bool(record.has_image),
            "image_text_relevance_score": record.image_text_relevance,
            "visual_context_summary": record.image_analysis_summary,
            "flags": []
        },
        decision_fusion=record.decision_factors or {
            "final_assessment": record.final_assessment,
            "explanation": record.assessment_explanation,
            "uncertainty_level": record.uncertainty_level or "Moderate",
            "supporting_evidence_count": 0,
            "contradicting_evidence_count": 0,
            "fact_check_count": len(record.fact_check_results or []),
            "evidence_coverage": "Moderate",
            "decision_rules_applied": []
        },
        status=record.status,
        provider_status=record.provider_status or {},
        latency_breakdown_ms=record.latency_breakdown_ms or {},
        total_latency_ms=record.total_latency_ms,
        retrieval_timestamp=record.retrieval_timestamp or "",
        created_at=record.created_at.isoformat() if record.created_at else ""
    )

@router.delete("/history/{analysis_id}")
def delete_history_record(analysis_id: str, db: Session = Depends(get_db)):
    """Deletes an analysis history record."""
    repo = AnalysisRepository(db)
    success = repo.delete(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Analysis report '{analysis_id}' not found.")
    return {"message": f"Analysis report '{analysis_id}' deleted successfully.", "deleted_id": analysis_id}
