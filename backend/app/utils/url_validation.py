from urllib.parse import urlparse
import re

def extract_domain(url: str) -> str:
    """Extracts clean registered domain or hostname from URL."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        # Remove port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]
        # Strip common subdomains like 'www.', 'm.', 'mobile.'
        netloc = re.sub(r'^(www\.|m\.|mobile\.)', '', netloc)
        return netloc
    except Exception:
        return ""

def is_valid_http_url(url: str) -> bool:
    """Checks if a URL has valid http/https structure."""
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False
