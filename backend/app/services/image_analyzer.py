import time
import io
import math
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageStat
import numpy as np
from backend.app.core.security import validate_image_file, SecurityException
from backend.app.api.schemas.analysis import ImageModelAnalysis
from backend.app.core.logging import logger

class ImageAnalyzer:
    """
    Multimodal Image Verification Service:
    - Safely decodes and validates image inputs.
    - Extracts visual context and structural features.
    - Estimates semantic relevance between image attributes and article content.
    - Discloses limitations: Does not claim deepfake detection without forensic models.
    """
    def __init__(self):
        pass

    def analyze_image(
        self,
        image_bytes: Optional[bytes],
        headline: str = "",
        article_text: str = ""
    ) -> ImageModelAnalysis:
        if not image_bytes:
            return ImageModelAnalysis(
                has_image=False,
                visual_context_summary="No image was provided with this article submission.",
                flags=[]
            )

        start_time = time.time()
        try:
            # 1. Safe decode and validate
            image = validate_image_file(image_bytes)
            width, height = image.size
            img_format = image.format or "UNKNOWN"
            
            # Convert to RGB for analysis if needed
            if image.mode != "RGB":
                rgb_img = image.convert("RGB")
            else:
                rgb_img = image

            # 2. Extract visual statistics
            stat = ImageStat.Stat(rgb_img)
            mean_rgb = stat.mean[:3]
            brightness = sum(mean_rgb) / 3.0 # 0 to 255
            
            # Grayscale variance for edge/detail richness
            gray_img = rgb_img.convert("L")
            gray_stat = ImageStat.Stat(gray_img)
            contrast = gray_stat.stddev[0] # standard deviation as contrast proxy
            
            # 3. Analyze image-text contextual relationship
            relevance_score, visual_summary, flags = self._assess_image_text_consistency(
                rgb_img, headline, article_text, brightness, contrast
            )
            
            elapsed_ms = (time.time() - start_time) * 1000.0
            
            return ImageModelAnalysis(
                has_image=True,
                image_format=img_format,
                image_dimensions=f"{width}x{height}",
                image_text_relevance_score=round(relevance_score, 3),
                visual_context_summary=visual_summary,
                flags=flags,
                inference_time_ms=round(elapsed_ms, 2)
            )
        except SecurityException as se:
            logger.warning(f"Image security rejection: {str(se)}")
            return ImageModelAnalysis(
                has_image=False,
                visual_context_summary=f"Image rejected by security filter: {str(se)}",
                flags=["SECURITY_REJECTION"]
            )
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return ImageModelAnalysis(
                has_image=False,
                visual_context_summary=f"Image processing failed: {str(e)}",
                flags=["PROCESSING_ERROR"]
            )

    def _assess_image_text_consistency(
        self,
        img: Image.Image,
        headline: str,
        text: str,
        brightness: float,
        contrast: float
    ) -> Tuple[float, str, List[str]]:
        """
        Calculates image-text relevance signals based on visual parameters
        and text keywords (e.g. night/day, color schemes, diagram vs photo).
        """
        flags = []
        full_text = f"{headline} {text}".lower()
        
        # Check night/dark text cues vs brightness
        has_night_cues = any(w in full_text for w in ("night", "darkness", "midnight", "evening", "dark"))
        has_bright_cues = any(w in full_text for w in ("sunny", "daylight", "bright afternoon", "noon"))
        
        relevance = 0.70 # Baseline neutral-positive relevance for user-provided image
        
        if has_night_cues and brightness > 190:
            flags.append("POTENTIAL_CONTEXT_MISMATCH: Text references night/darkness, but image has high daytime brightness.")
            relevance -= 0.25
        elif has_bright_cues and brightness < 60:
            flags.append("POTENTIAL_CONTEXT_MISMATCH: Text references bright daylight, but image is predominantly dark.")
            relevance -= 0.25

        if contrast < 15:
            flags.append("LOW_DETAIL: Image exhibits very low visual variance or flat color distribution.")
            relevance -= 0.15

        relevance = max(0.1, min(0.95, relevance))
        
        summary = (
            f"Image ({img.width}x{img.height}, {img.format}) analyzed. "
            f"Visual brightness: {brightness:.1f}/255, Contrast variance: {contrast:.1f}. "
            f"Assessed image-text consistency score: {relevance:.2f}. "
            f"Note: Image relevance does not independently verify photographic provenance or historical capture date."
        )
        
        return relevance, summary, flags
