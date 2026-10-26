from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FactCheckItem(BaseModel):
    """Result from Google Fact Check Tools API or registered fact-checker."""
    id: str
    claim_reviewed: str
    fact_checker_publisher: str
    publisher_site: Optional[str] = None
    review_title: str
    review_url: str
    publication_date: Optional[str] = None
    original_rating: str = Field(description="Preserved verbatim rating from original publisher")
    normalized_verdict: str = Field(description="Normalized indicator: FALSE, TRUE, MIXED, UNPROVEN")
    claim_date: Optional[str] = None
    retrieval_timestamp: str

class NewsArticleItem(BaseModel):
    """Relevant news article retrieved via live search (GDELT / News API)."""
    id: str
    title: str
    publisher: str
    domain: str
    url: str
    publication_date: Optional[str] = None
    snippet: Optional[str] = None
    search_query: str
    retrieval_timestamp: str
    stance: str = Field(default="neutral", description="supporting, contradicting, contextual, neutral")
    relevance_score: float = Field(default=0.0, description="Semantic or lexical similarity score")
    is_syndicated_duplicate: bool = False

class CredibilityFactor(BaseModel):
    factor_name: str
    score: float = Field(description="Score component from 0 to 100")
    weight: float = Field(description="Weight in the overall heuristic score")
    description: str
    status: str = Field(description="Observed, Partially observed, Unobserved")

class SourceCredibilityReport(BaseModel):
    domain: Optional[str] = None
    publisher_name: Optional[str] = None
    overall_score: Optional[float] = Field(default=None, description="0 to 100 score or None if insufficient info")
    assessment_status: str = Field(
        description="Assessed, Partially assessed, Insufficient source information, Assessment unavailable"
    )
    factors: List[CredibilityFactor] = Field(default_factory=list)
    missing_signals: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default="Heuristic source assessment score. Does not represent statistical proof of truth of any individual claim."
    )

class FactCheckSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    language_code: Optional[str] = "en"

class NewsSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    max_records: Optional[int] = 10
