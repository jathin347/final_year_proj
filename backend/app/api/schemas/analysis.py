from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.api.schemas.claims import ExtractedClaim
from backend.app.api.schemas.evidence import FactCheckItem, NewsArticleItem, SourceCredibilityReport

class AnalysisRequest(BaseModel):
    url: Optional[str] = Field(default=None, description="URL of the news article to extract and verify")
    headline: Optional[str] = Field(default=None, max_length=1000, description="Headline of the claim or news item")
    article_text: Optional[str] = Field(default=None, max_length=50000, description="Full body text of the article")
    user_context: Optional[str] = Field(default=None, max_length=2000, description="Optional user context or question")

class TextModelAnalysis(BaseModel):
    model_name: str
    model_version: str
    prediction: str = Field(description="e.g. Credible, Misinformation Risk, Neutral, Inconclusive")
    confidence: float = Field(description="Normalized probability score 0.0 - 1.0")
    stylometric_signals: Dict[str, Any] = Field(default_factory=dict)
    key_attribution_tokens: List[Dict[str, Any]] = Field(default_factory=list)
    inference_time_ms: float
    limitations: str = "Classifier evaluates linguistic and stylistic cues; it does not replace external evidence verification."

class ImageModelAnalysis(BaseModel):
    has_image: bool = False
    image_format: Optional[str] = None
    image_dimensions: Optional[str] = None
    image_text_relevance_score: Optional[float] = None # 0.0 - 1.0
    visual_context_summary: Optional[str] = None
    flags: List[str] = Field(default_factory=list)
    inference_time_ms: float = 0.0
    limitations: str = "Image-text similarity evaluates visual relevance; it does not detect deepfakes or establish photographic authenticity."

class DecisionFusionReport(BaseModel):
    final_assessment: str = Field(
        description="Supported by available evidence, Contradicted by available evidence, Misleading or missing context, Conflicting evidence, Insufficient evidence, Analysis unavailable"
    )
    explanation: str
    uncertainty_level: str = Field(description="Low, Moderate, High")
    supporting_evidence_count: int
    contradicting_evidence_count: int
    fact_check_count: int
    evidence_coverage: str = Field(description="Robust, Moderate, Sparse, None")
    decision_rules_applied: List[str]

class AnalysisResponse(BaseModel):
    id: str
    headline: str
    article_url: Optional[str] = None
    publisher: Optional[str] = None
    domain: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    article_summary: Optional[str] = None
    
    # Verdicts & Explanations
    final_assessment: str
    assessment_explanation: str
    uncertainty_level: str
    
    # Components
    claims: List[ExtractedClaim] = Field(default_factory=list)
    fact_checks: List[FactCheckItem] = Field(default_factory=list)
    news_articles: List[NewsArticleItem] = Field(default_factory=list)
    source_credibility: SourceCredibilityReport
    text_analysis: TextModelAnalysis
    image_analysis: ImageModelAnalysis
    decision_fusion: DecisionFusionReport
    
    # Operational & Audit Metadata
    status: str
    provider_status: Dict[str, str]
    latency_breakdown_ms: Dict[str, float]
    total_latency_ms: float
    retrieval_timestamp: str
    created_at: str

class AnalysisHistorySummary(BaseModel):
    id: str
    headline: str
    article_url: Optional[str] = None
    domain: Optional[str] = None
    final_assessment: str
    source_credibility_score: Optional[float] = None
    total_latency_ms: float
    created_at: str

class PaginatedHistoryResponse(BaseModel):
    items: List[AnalysisHistorySummary]
    total: int
    page: int
    page_size: int
    pages: int
