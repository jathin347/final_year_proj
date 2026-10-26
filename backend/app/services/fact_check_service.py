import time
import httpx
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.api.schemas.evidence import FactCheckItem
from backend.app.core.config import settings
from backend.app.core.logging import logger

class FactCheckService:
    """
    Live Integration with Google Fact Check Tools API:
    - Official Docs: https://developers.google.com/fact-check/tools/api
    - Searches ClaimReview structured database for verified checks by accredited publishers.
    - Preserves verbatim ratings (e.g., 'Pants on Fire', 'False', 'Mostly True').
    - Handles missing API keys, rate limits, timeouts, and empty results gracefully.
    - Never fabricates synthetic fact-checks.
    """
    BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def __init__(self):
        self.api_key = settings.GOOGLE_FACT_CHECK_API_KEY.strip() if settings.GOOGLE_FACT_CHECK_API_KEY else ""

    async def search_claims(self, query: str, language_code: str = "en") -> List[FactCheckItem]:
        if not query or len(query.strip()) < 3:
            return []

        if not self.api_key:
            logger.info("GOOGLE_FACT_CHECK_API_KEY not configured. Skipping live Fact Check API query.")
            return []

        retrieval_time = datetime.now(timezone.utc).isoformat()
        params = {
            "query": query.strip(),
            "languageCode": language_code,
            "key": self.api_key,
            "pageSize": 5
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                
                if response.status_code == 403:
                    logger.warning("Google Fact Check API 403: Invalid or unauthorized API key.")
                    return []
                if response.status_code == 429:
                    logger.warning("Google Fact Check API 429: Rate limit quota exceeded.")
                    return []
                if response.status_code != 200:
                    logger.warning(f"Google Fact Check API returned HTTP {response.status_code}")
                    return []

                data = response.json()
                raw_claims = data.get("claims", [])
                
                results: List[FactCheckItem] = []
                for claim in raw_claims:
                    original_claim = claim.get("text", "")
                    claim_date = claim.get("claimDate")
                    reviews = claim.get("claimReview", [])
                    
                    for rev in reviews:
                        publisher_info = rev.get("publisher", {})
                        publisher_name = publisher_info.get("name", "Unknown Fact Checker")
                        publisher_site = publisher_info.get("site", "")
                        review_title = rev.get("title", "")
                        review_url = rev.get("url", "")
                        review_date = rev.get("reviewDate")
                        textual_rating = rev.get("textualRating", "Unrated")

                        normalized = self._normalize_rating(textual_rating)

                        results.append(FactCheckItem(
                            id=f"fc_{uuid.uuid4().hex[:8]}",
                            claim_reviewed=original_claim or query,
                            fact_checker_publisher=publisher_name,
                            publisher_site=publisher_site,
                            review_title=review_title or f"Fact Check by {publisher_name}",
                            review_url=review_url,
                            publication_date=review_date,
                            original_rating=textual_rating,
                            normalized_verdict=normalized,
                            claim_date=claim_date,
                            retrieval_timestamp=retrieval_time
                        ))
                        
                return results

        except httpx.TimeoutException:
            logger.warning(f"Timeout querying Google Fact Check API for query '{query}'")
            return []
        except Exception as e:
            logger.error(f"Error querying Google Fact Check API: {str(e)}")
            return []

    def _normalize_rating(self, raw_rating: str) -> str:
        """
        Maps publisher-specific ratings to standardized indicator
        WITHOUT overwriting the original rating.
        """
        r = raw_rating.lower().strip()
        
        # False indicators
        if any(term in r for term in (
            "false", "fake", "pants on fire", "incorrect", "hoax", "inaccurate",
            "debunked", "misleading", "distorts", "fabricated", "four pinocchios"
        )):
            return "FALSE"
            
        # True indicators
        if any(term in r for term in ("true", "correct", "accurate", "verified", "geppetto checkmark")):
            return "TRUE"
            
        # Mixed / Half-true indicators
        if any(term in r for term in ("mixture", "half true", "partly true", "mostly false", "mostly true", "unproven")):
            return "MIXED"
            
        return "UNPROVEN"
