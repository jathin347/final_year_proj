import ipaddress
import socket
from urllib.parse import urlparse
import io
from PIL import Image
from backend.app.core.config import settings
from backend.app.core.logging import logger

DISALLOWED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),    # Private RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),   # Private RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("224.0.0.0/4"),      # Multicast
    ipaddress.ip_network("240.0.0.0/4"),      # Reserved
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

class SecurityException(Exception):
    """Exception raised for security policy violations."""
    pass

def validate_url_safety(url: str) -> str:
    """
    Validates a URL against SSRF attacks:
    1. Enforces http or https scheme.
    2. Validates hostname exists.
    3. Resolves DNS to IP addresses and checks against private/loopback/link-local ranges.
    """
    if not url or not isinstance(url, str):
        raise SecurityException("URL must be a non-empty string.")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise SecurityException(f"Unsupported URL scheme '{parsed.scheme}'. Only http and https are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SecurityException("URL does not contain a valid hostname.")

    if not settings.ENABLE_SSRF_PROTECTION:
        return url

    # Block localhost string variations
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal", "169.254.169.254"):
        raise SecurityException(f"Requests to local or metadata host '{hostname}' are forbidden.")

    # Resolve hostname to IP addresses
    try:
        resolved_ips = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise SecurityException(f"Unable to resolve DNS for hostname '{hostname}': {str(e)}")

    for item in resolved_ips:
        ip_str = item[4][0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            for network in DISALLOWED_NETWORKS:
                if ip_obj in network:
                    logger.warning(f"SSRF block: Host '{hostname}' resolved to forbidden IP '{ip_str}' in '{network}'")
                    raise SecurityException(f"Access to internal or reserved IP address '{ip_str}' is forbidden.")
        except ValueError:
            continue

    return url

def validate_image_file(file_bytes: bytes, mime_type: str = "") -> Image.Image:
    """
    Validates image data:
    1. Enforces size limit.
    2. Enforces allowed MIME / format.
    3. Safely decodes image via PIL without executing arbitrary scripts.
    4. Enforces sane dimension bounds to prevent decompression bombs.
    """
    if not file_bytes:
        raise SecurityException("Empty image data provided.")

    if len(file_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise SecurityException(f"Image size exceeds maximum allowed limit of {settings.MAX_IMAGE_SIZE_BYTES / (1024*1024):.1f}MB.")

    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()  # Verify integrity
        # Re-open for actual processing because verify() corrupts the file descriptor for subsequent reads
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise SecurityException(f"Invalid or corrupted image format: {str(e)}")

    format_lower = (image.format or "").lower()
    allowed_formats = {"jpeg", "jpg", "png", "webp"}
    if format_lower not in allowed_formats:
        raise SecurityException(f"Image format '{image.format}' is not supported. Permitted formats: JPEG, PNG, WEBP.")

    width, height = image.size
    if width > 6000 or height > 6000:
        raise SecurityException(f"Image dimensions {width}x{height} exceed maximum permitted limit (6000x6000).")

    return image
