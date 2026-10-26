from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(tags=["Providers"])

@router.get("/providers/status")
def get_providers_status():
    """
    Returns safe configuration and availability status of external providers
    WITHOUT exposing secrets, tokens, or raw credentials.
    """
    return {
        "providers": [
            {
                "name": "Google Gemini API",
                "purpose": "Structured factual claim extraction and deep contextual reasoning",
                "configured": settings.has_gemini_key,
                "status": "Available" if settings.has_gemini_key else "Unconfigured (Operating in Local NLP Heuristic Fallback Mode)",
                "documentation": "https://ai.google.dev/gemini-api/docs"
            },
            {
                "name": "Google Fact Check Tools API",
                "purpose": "Retrieval of professional published fact-check ClaimReview records",
                "configured": settings.has_fact_check_key,
                "status": "Available" if settings.has_fact_check_key else "Unconfigured (Fact-check reviews will show zero results until key is set)",
                "documentation": "https://developers.google.com/fact-check/tools/api"
            },
            {
                "name": "GDELT Project 2.0 DOC API",
                "purpose": "Live global news retrieval, reporting stance analysis, and deduplication",
                "configured": True, # Publicly accessible without key
                "status": "Available (Public REST Integration)",
                "documentation": "https://www.gdeltproject.org/"
            },
            {
                "name": "Veritas Local Stylometric Ensemble",
                "purpose": "Stylometric, sensationalism, and token attribution analysis",
                "configured": True,
                "status": "Available (In-Memory Inference)",
                "documentation": "Internal AI Module"
            },
            {
                "name": "Veritas Multimodal Image Validator",
                "purpose": "Safe visual attribute and image-text consistency verification",
                "configured": True,
                "status": "Available (PIL / PyTorch)",
                "documentation": "Internal Vision Module"
            }
        ]
    }
