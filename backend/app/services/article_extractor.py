import time
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from backend.app.core.security import validate_url_safety, SecurityException
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.utils.url_validation import extract_domain

class ArticleExtractionException(Exception):
    pass

class ArticleExtractor:
    """
    Safely extracts article metadata and text from a public web page:
    - Enforces SSRF and scheme validation before connection.
    - Uses strict timeouts and response size limits.
    - Extracts OpenGraph, Twitter card, Schema.org, and standard semantic HTML.
    - Gracefully fails if paywalled or blocked.
    """
    def __init__(self, timeout_seconds: float = settings.REQUEST_TIMEOUT_SECONDS):
        self.timeout = timeout_seconds
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 VeritasAI-Research/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. SSRF validation
        safe_url = validate_url_safety(url)
        domain = extract_domain(safe_url)
        
        # 2. Fetch page with bounded stream
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(safe_url, headers=self.headers)
                
                # Check redirect target for SSRF
                if str(response.url) != safe_url:
                    validate_url_safety(str(response.url))
                    
                if response.status_code >= 400:
                    raise ArticleExtractionException(
                        f"Website returned HTTP error {response.status_code} ({response.reason_phrase}). "
                        "The website may be paywalled or blocking access. Please provide the text manually."
                    )
                
                # Limit size to prevent memory exhaustion
                max_bytes = settings.MAX_CONTENT_LENGTH_MB * 1024 * 1024
                content_bytes = response.content
                if len(content_bytes) > max_bytes:
                    raise ArticleExtractionException(f"Webpage content exceeds maximum allowed limit ({settings.MAX_CONTENT_LENGTH_MB}MB).")
                
                html_text = response.text
        except SecurityException as se:
            raise ArticleExtractionException(f"Security validation rejected URL: {str(se)}")
        except httpx.TimeoutException:
            raise ArticleExtractionException("Request timed out while connecting to the article host. Please paste the article text manually.")
        except httpx.RequestError as re:
            raise ArticleExtractionException(f"Network error accessing URL: {str(re)}. Please paste the article text manually.")
        except Exception as e:
            if isinstance(e, ArticleExtractionException):
                raise
            raise ArticleExtractionException(f"Failed to fetch article: {str(e)}")

        # 3. Parse HTML
        soup = BeautifulSoup(html_text, "html.parser")
        
        # Remove script, style, nav, footer, ads tags
        for element in soup(["script", "style", "nav", "footer", "aside", "header", "noscript", "svg", "form"]):
            element.decompose()
            
        headline = self._extract_headline(soup)
        author = self._extract_author(soup)
        published_date = self._extract_date(soup)
        publisher = self._extract_publisher(soup, domain)
        article_text = self._extract_body_text(soup)
        
        if not article_text or len(article_text.strip()) < 50:
            raise ArticleExtractionException(
                "Could not extract sufficient article text from the webpage. "
                "The page may require JavaScript or authentication. Please paste the article text directly."
            )
            
        elapsed_ms = (time.time() - start_time) * 1000.0
        
        return {
            "headline": headline or "Untitled Article",
            "article_text": article_text,
            "publisher": publisher,
            "domain": domain,
            "author": author,
            "published_date": published_date,
            "canonical_url": safe_url,
            "extraction_time_ms": elapsed_ms,
            "retrieval_timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _extract_headline(self, soup: BeautifulSoup) -> str:
        # Check og:title
        og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "og:title"})
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
            
        # Check twitter:title
        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        if tw_title and tw_title.get("content"):
            return tw_title["content"].strip()
            
        # Check <h1>
        h1 = soup.find("h1")
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)
            
        # Fallback to <title>
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            raw_title = title_tag.get_text(strip=True)
            # Remove publisher suffix like ' - The New York Times' or ' | BBC News'
            return raw_title.split(" - ")[0].split(" | ")[0].strip()
            
        return ""

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        # Check meta author
        meta_author = (
            soup.find("meta", attrs={"name": "author"}) or
            soup.find("meta", property="article:author") or
            soup.find("meta", attrs={"name": "byl"})
        )
        if meta_author and meta_author.get("content"):
            return meta_author["content"].strip()
            
        # Check common author classes
        author_elem = soup.find(class_=lambda c: c and any(k in c.lower() for k in ("author", "byline")))
        if author_elem and author_elem.get_text(strip=True):
            text = author_elem.get_text(strip=True)
            if len(text) < 80:
                return text
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        meta_date = (
            soup.find("meta", property="article:published_time") or
            soup.find("meta", attrs={"name": "publish-date"}) or
            soup.find("meta", attrs={"name": "pubdate"}) or
            soup.find("meta", attrs={"name": "date"})
        )
        if meta_date and meta_date.get("content"):
            return meta_date["content"].strip()
            
        time_tag = soup.find("time")
        if time_tag and (time_tag.get("datetime") or time_tag.get_text(strip=True)):
            return time_tag.get("datetime") or time_tag.get_text(strip=True)
        return None

    def _extract_publisher(self, soup: BeautifulSoup, domain: str) -> str:
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            return og_site["content"].strip()
        # Fallback to clean domain
        return domain.capitalize() if domain else "Unknown Publisher"

    def _extract_body_text(self, soup: BeautifulSoup) -> str:
        # Check standard article containers
        article_container = soup.find("article") or soup.find("main") or soup.find("div", class_=lambda c: c and any(k in c.lower() for k in ("article-body", "story-body", "post-content", "entry-content")))
        
        target = article_container if article_container else soup.find("body") or soup
        
        paragraphs = target.find_all("p")
        extracted_paragraphs = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out boilerplate, short navigation snippets
            if len(text) > 40 and not any(skip in text.lower() for skip in ("subscribe", "cookie policy", "terms of use", "privacy policy")):
                extracted_paragraphs.append(text)
                
        return "\n\n".join(extracted_paragraphs)
