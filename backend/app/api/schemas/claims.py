from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedClaim(BaseModel):
    """Structured checkable claim extracted from news text."""
    claim_id: str = Field(description="Unique identifier for the claim (e.g., c1, c2)")
    claim_text: str = Field(description="The exact factual assertion to check")
    importance: str = Field(default="MEDIUM", description="Importance to the article core premise: HIGH, MEDIUM, LOW")
    category: Optional[str] = Field(default="General", description="Category: Politics, Science, Health, Economy, Crime, International, General")
    named_entities: List[str] = Field(default_factory=list, description="Extracted key entities (people, orgs, places)")
    relevant_dates: List[str] = Field(default_factory=list, description="Explicit dates mentioned in the claim")
    relevant_locations: List[str] = Field(default_factory=list, description="Geographic locations tied to the claim")
    search_queries: List[str] = Field(default_factory=list, description="Optimal queries for fact-checking and news search")
    verification_status: str = Field(default="UNVERIFIED", description="Status: SUPPORTED, CONTRADICTED, MISLEADING, CONFLICTING, INSUFFICIENT, UNVERIFIED")
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradicting_evidence_ids: List[str] = Field(default_factory=list)
    explanation: Optional[str] = Field(default=None, description="Reasoning grounding this claim's verification verdict")

class ClaimExtractionRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="Article or text to extract claims from")
    headline: Optional[str] = Field(default=None, max_length=1000)

class ClaimExtractionResponse(BaseModel):
    claims: List[ExtractedClaim]
    count: int
    source_method: str = Field(description="Extraction engine used (e.g. Gemini LLM or Local Rule/NLP Extractor)")
    extraction_time_ms: float
