import pytest
from backend.app.core.security import validate_url_safety, validate_image_file, SecurityException
import io
from PIL import Image

def test_validate_url_safety_valid():
    safe = validate_url_safety("https://en.wikipedia.org/wiki/News")
    assert safe.startswith("https://")

def test_validate_url_safety_invalid_schemes():
    with pytest.raises(SecurityException) as exc:
        validate_url_safety("ftp://example.com/file.txt")
    assert "Unsupported URL scheme" in str(exc.value)

    with pytest.raises(SecurityException) as exc:
        validate_url_safety("file:///etc/passwd")
    assert "Unsupported URL scheme" in str(exc.value)

def test_validate_url_safety_localhost_and_internal_ips():
    # Direct localhost string
    with pytest.raises(SecurityException) as exc:
        validate_url_safety("http://localhost:8000/admin")
    assert "forbidden" in str(exc.value)

    with pytest.raises(SecurityException) as exc:
        validate_url_safety("http://127.0.0.1:8000")
    assert "forbidden" in str(exc.value)

    with pytest.raises(SecurityException) as exc:
        validate_url_safety("http://169.254.169.254/latest/meta-data/")
    assert "forbidden" in str(exc.value)

def test_safe_image_validation_valid():
    # Create valid in-memory PNG
    img = Image.new("RGB", (100, 100), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    data = buf.read()

    validated = validate_image_file(data)
    assert validated.size == (100, 100)
    assert validated.format == "PNG"

def test_safe_image_validation_corrupted_data():
    corrupted = b"NOT_AN_IMAGE_FILE_RANDOM_BYTES"
    with pytest.raises(SecurityException) as exc:
        validate_image_file(corrupted)
    assert "Invalid or corrupted image format" in str(exc.value)

def test_safe_image_validation_oversized():
    # Empty byte limit test
    with pytest.raises(SecurityException) as exc:
        validate_image_file(b"")
    assert "Empty image data" in str(exc.value)
