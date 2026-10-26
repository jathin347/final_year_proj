import sys
import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.models.database import get_db
from backend.app.core.config import settings

router = APIRouter(tags=["Health"])

START_TIME = time.time()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint returning application, database, and environment status."""
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    uptime = time.time() - START_TIME

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "python_version": sys.version.split()[0],
        "uptime_seconds": round(uptime, 1),
        "environment": "production" if not settings.DEBUG else "development"
    }

@router.get("/metrics")
def operational_metrics(db: Session = Depends(get_db)):
    """Returns genuine operational metrics from the database."""
    from backend.app.models.entities import AnalysisRecord
    
    total_analyses = db.query(AnalysisRecord).count()
    completed = db.query(AnalysisRecord).filter(AnalysisRecord.status == "COMPLETED").count()
    
    # Calculate average latency from completed records
    records = db.query(AnalysisRecord.total_latency_ms).filter(AnalysisRecord.total_latency_ms > 0).all()
    avg_latency = (sum(r[0] for r in records) / len(records)) if records else 0.0

    return {
        "total_verification_requests": total_analyses,
        "completed_requests": completed,
        "average_pipeline_latency_ms": round(avg_latency, 2),
        "gemini_configured": settings.has_gemini_key,
        "google_fact_check_configured": settings.has_fact_check_key,
        "gdelt_provider_status": "ONLINE (REST API)"
    }
