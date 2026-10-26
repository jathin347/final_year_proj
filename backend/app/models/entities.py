import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, JSON, Integer
from backend.app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AnalysisRecord(Base):
    """
    SQLAlchemy Entity representing an individual news verification run.
    """
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    article_url = Column(String(2048), nullable=True)
    headline = Column(String(1024), nullable=False)
    article_summary = Column(Text, nullable=True)
    publisher = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    published_date = Column(String(64), nullable=True)
    
    # Input metadata
    input_type = Column(String(32), default="text") # url, text, headline_only, multimodal
    has_image = Column(Integer, default=0) # 0 or 1
    
    # Verdict & Decision Fusion
    final_assessment = Column(String(64), nullable=False)
    # Categories:
    # "Supported by available evidence", "Contradicted by available evidence",
    # "Misleading or missing context", "Conflicting evidence", "Insufficient evidence", "Analysis unavailable"
    assessment_explanation = Column(Text, nullable=False)
    uncertainty_level = Column(String(32), default="Moderate") # Low, Moderate, High
    
    # Sub-scores
    source_credibility_score = Column(Float, nullable=True)
    source_assessment_status = Column(String(64), nullable=True) # Assessed, Partially assessed, Insufficient source information, Assessment unavailable
    text_model_prediction = Column(String(64), nullable=True)
    text_model_confidence = Column(Float, nullable=True)
    image_text_relevance = Column(Float, nullable=True)
    image_analysis_summary = Column(Text, nullable=True)
    
    # Structured JSON Payloads
    extracted_claims = Column(JSON, default=list)
    fact_check_results = Column(JSON, default=list)
    news_search_results = Column(JSON, default=list)
    source_credibility_breakdown = Column(JSON, default=dict)
    decision_factors = Column(JSON, default=dict)
    latency_breakdown_ms = Column(JSON, default=dict)
    total_latency_ms = Column(Float, default=0.0)
    
    # Execution & System Status
    status = Column(String(32), default="COMPLETED") # COMPLETED, PARTIALLY_COMPLETED, FAILED
    provider_status = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, index=True)
    retrieval_timestamp = Column(String(64), nullable=True)
