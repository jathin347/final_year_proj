import time
import httpx
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import quote_plus
from backend.app.api.schemas.evidence import NewsArticleItem
from backend.app.utils.url_validation import extract_domain
from backend.app.utils.text_processing import calculate_cosine_similarity
from backend.app.core.logging import logger

class NewsSearchService:
    """
    Live News Retrieval via GDELT 2.0 DOC API:
    - Official Docs: https://www.gdeltproject.org/
    - Endpoint: https://api.gdeltproject.org/api/v2/doc/doc
    - Retrieves real-time global news coverage associated with claims.
    - Implements syndication deduplication to prevent wire reprints from masquerading as independent corroboration.
    """
    GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, timeout_seconds: float = 10.0):
        self.timeout = timeout_seconds

    async def search_news(self, query: str, max_records: int = 10) -> List[NewsArticleItem]:
        if not query or len(query.strip()) < 3:
            return []

        clean_query = query.strip()
        retrieval_time = datetime.now(timezone.utc).isoformat()
        
        # Build GDELT query with English filter and recent timeframe
        # GDELT syntax: query with quotes or keywords
        encoded_query = f'"{clean_query}"' if len(clean_query.split()) <= 4 else clean_query
        
        params = {
            "query": encoded_query,
            "mode": "artlist",
            "maxrecords": str(min(max_records, 20)),
            "format": "json",
            "sort": "DateDesc"
        }

        articles: List[NewsArticleItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.GDELT_API_URL, params=params)
                
                # GDELT occasionally returns empty body or plain text if no matches found
                if resp.status_code != 200 or not resp.text.strip():
                    logger.info(f"GDELT returned HTTP {resp.status_code} for query '{query}'")
                    # Try a relaxed search with top keywords if strict search yielded nothing
                    if '"' in encoded_query:
                        return await self.search_news(clean_query.replace('"', ''), max_records=max_records)
                    return []

                # Handle GDELT plain text HTML error responses gracefully
                if resp.text.startswith("<") or not resp.text.startswith("{"):
                    logger.info(f"GDELT returned non-JSON response for query '{query}'. (Likely no records matched)")
                    return []

                data = resp.json()
                raw_articles = data.get("articles", [])
                
                # Parse and deduplicate
                seen_titles = []
                for item in raw_articles:
                    title = item.get("title", "").strip()
                    url = item.get("url", "").strip()
                    domain = item.get("domain", "") or extract_domain(url)
                    seen_date_raw = item.get("seendate", "")
                    
                    if not title or not url:
                        continue
                        
                    # Format GDELT seendate (e.g. 20241026T143000Z)
                    pub_date = self._format_gdelt_date(seen_date_raw)
                    
                    # Detect syndication duplicates using title similarity
                    is_duplicate = False
                    for existing_title in seen_titles:
                        if calculate_cosine_similarity(title, existing_title) > 0.85:
                            is_duplicate = True
                            break
                            
                    if not is_duplicate:
                        seen_titles.append(title)

                    articles.append(NewsArticleItem(
                        id=f"news_{uuid.uuid4().hex[:8]}",
                        title=title,
                        publisher=domain.upper() if domain else "Unknown Publisher",
                        domain=domain,
                        url=url,
                        publication_date=pub_date,
                        snippet=f"Retrieved via GDELT global news monitor for query '{query}'.",
                        search_query=query,
                        retrieval_timestamp=retrieval_time,
                        stance="neutral",
                        relevance_score=round(calculate_cosine_similarity(query, title), 3),
                        is_syndicated_duplicate=is_duplicate
                    ))

                return articles

        except httpx.TimeoutException:
            logger.warning(f"GDELT query timed out for '{query}'")
            return []
        except Exception as e:
            logger.error(f"Error fetching from GDELT: {str(e)}")
            return []

    def _format_gdelt_date(self, raw_date: str) -> Optional[str]:
        if not raw_date or len(raw_date) < 8:
            return None
        try:
            # GDELT format: YYYYMMDDTHHMMSSZ or YYYYMMDD
            year = raw_date[0:4]
            month = raw_date[4:6]
            day = raw_date[6:8]
            return f"{year}-{month}-{day}"
        except Exception:
            return raw_date
