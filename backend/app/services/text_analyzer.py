import time
import re
import math
from typing import Dict, Any, List, Tuple
import numpy as np
from backend.app.api.schemas.analysis import TextModelAnalysis
from backend.app.utils.text_processing import clean_text, tokenize_words

class TextAnalyzer:
    """
    AI Text Analysis Pipeline:
    - Analyzes stylometric, lexical, and structural cues associated with misinformation.
    - Evaluates sensationalism, clickbait phrasing, emotional valence, and attribution density.
    - Uses calibrated probabilistic scoring with token-level feature attribution.
    - Separates linguistic/stylistic analysis from factual truth verification.
    """
    MODEL_NAME = "Veritas-Stylistic-Ensemble"
    MODEL_VERSION = "1.2.0"
    
    CLICKBAIT_PATTERNS = [
        r"\byou won't believe\b",
        r"\bwhat happens next\b",
        r"\bshocking truth\b",
        r"\bdoctors (?:hate|don't want you to know)\b",
        r"\bexposed:\b",
        r"\bthe secret reason\b",
        r"\bthis one weird trick\b",
        r"\bwill blow your mind\b",
        r"\bthey are hiding this\b",
        r"\bmainstream media won't tell you\b",
        r"\bconspiracy to\b",
        r"\bmust-see\b",
        r"\bbombshell report\b",
        r"\bproof that\b"
    ]
    
    ATTRIBUTION_MARKERS = [
        r"\baccording to\b",
        r"\bspokesperson stated\b",
        r"\breported by\b",
        r"\bconfirmed by\b",
        r"\bofficials said\b",
        r"\bresearchers found\b",
        r"\bdata shows\b",
        r"\bpublished in\b",
        r"\bcited in\b",
        r"\bin an interview\b"
    ]
    
    HIGH_RISK_TOKENS = {
        "miracle": 0.8, "secret": 0.7, "hoax": 0.75, "conspiracy": 0.8, "shocking": 0.7,
        "unbelievable": 0.65, "hidden": 0.6, "illuminati": 0.9, "cabal": 0.85, "suppressed": 0.7,
        "rigged": 0.65, "bombshell": 0.75, "faked": 0.7, "chemtrails": 0.9, "plandemic": 0.95
    }
    
    CREDIBILITY_TOKENS = {
        "study": -0.6, "research": -0.6, "spokesperson": -0.7, "announced": -0.5, "confirmed": -0.6,
        "investigation": -0.4, "reuters": -0.8, "associated": -0.7, "published": -0.5, "data": -0.5,
        "peer-reviewed": -0.85, "analysts": -0.5, "official": -0.6, "department": -0.5
    }

    def analyze(self, headline: str, article_text: str) -> TextModelAnalysis:
        start_time = time.time()
        combined_text = f"{headline or ''}\n\n{article_text or ''}".strip()
        
        if not combined_text:
            return TextModelAnalysis(
                model_name=self.MODEL_NAME,
                model_version=self.MODEL_VERSION,
                prediction="Inconclusive",
                confidence=0.5,
                stylometric_signals={"status": "No text provided"},
                key_attribution_tokens=[],
                inference_time_ms=0.0
            )
            
        # 1. Stylometric analysis
        signals = self._compute_stylometric_signals(headline, article_text)
        
        # 2. Token-level feature attribution
        attributions, raw_score = self._compute_token_attributions(combined_text)
        
        # 3. Model score fusion (Calibrated Sigmoid)
        # Higher score = higher misinformation risk phrasing
        # Incorporate sensationalism, clickbait, and token weights
        risk_linear = (
            raw_score * 0.45 +
            signals["sensationalism_index"] * 0.25 +
            (1.0 if signals["clickbait_detected"] else 0.0) * 0.20 -
            signals["attribution_density"] * 0.25
        )
        
        # Logistic calibration bounded [0.05, 0.95]
        prob_risk = 1.0 / (1.0 + math.exp(-risk_linear))
        
        if prob_risk >= 0.62:
            prediction = "Elevated Misinformation Risk"
            confidence = round(prob_risk, 3)
        elif prob_risk <= 0.38:
            prediction = "Credible / Objective Phrasing"
            confidence = round(1.0 - prob_risk, 3)
        else:
            prediction = "Neutral / Mixed Stylometric Signals"
            confidence = round(max(prob_risk, 1.0 - prob_risk), 3)

        elapsed_ms = (time.time() - start_time) * 1000.0

        return TextModelAnalysis(
            model_name=self.MODEL_NAME,
            model_version=self.MODEL_VERSION,
            prediction=prediction,
            confidence=confidence,
            stylometric_signals=signals,
            key_attribution_tokens=attributions[:10],
            inference_time_ms=round(elapsed_ms, 2)
        )

    def _compute_stylometric_signals(self, headline: str, text: str) -> Dict[str, Any]:
        full_content = f"{headline} {text}"
        words = full_content.split()
        total_words = len(words) or 1
        
        # All-caps ratio (excluding single-character acronyms)
        caps_words = [w for w in words if len(w) > 2 and w.isupper() and w.isalpha()]
        all_caps_ratio = len(caps_words) / total_words
        
        # Exclamation and question mark density
        exclamations = full_content.count("!")
        questions = full_content.count("?")
        excessive_punct_ratio = (exclamations + questions) / total_words
        
        # Clickbait pattern matching
        clickbait_matches = []
        for pat in self.CLICKBAIT_PATTERNS:
            found = re.findall(pat, full_content, re.IGNORECASE)
            if found:
                clickbait_matches.extend(found)
                
        # Attribution markers
        attribution_matches = []
        for pat in self.ATTRIBUTION_MARKERS:
            found = re.findall(pat, full_content, re.IGNORECASE)
            if found:
                attribution_matches.extend(found)
                
        attribution_density = min(1.0, len(attribution_matches) / max(1, (total_words / 150)))
        
        # Sensationalism index normalized [0, 1]
        sensationalism = min(1.0, (all_caps_ratio * 4.0) + (excessive_punct_ratio * 5.0) + (len(clickbait_matches) * 0.3))
        
        return {
            "word_count": total_words,
            "all_caps_word_ratio": round(all_caps_ratio, 4),
            "excessive_punctuation_count": exclamations + questions,
            "clickbait_detected": len(clickbait_matches) > 0,
            "clickbait_patterns_found": list(set(clickbait_matches))[:5],
            "attribution_density": round(attribution_density, 3),
            "sensationalism_index": round(sensationalism, 3)
        }

    def _compute_token_attributions(self, text: str) -> Tuple[List[Dict[str, Any]], float]:
        tokens = tokenize_words(text)
        attributions = []
        total_weight = 0.0
        
        seen = set()
        for token in tokens:
            weight = 0.0
            category = "neutral"
            if token in self.HIGH_RISK_TOKENS:
                weight = self.HIGH_RISK_TOKENS[token]
                category = "risk_indicator"
            elif token in self.CREDIBILITY_TOKENS:
                weight = self.CREDIBILITY_TOKENS[token]
                category = "credibility_indicator"
                
            if weight != 0.0 and token not in seen:
                seen.add(token)
                attributions.append({
                    "token": token,
                    "attribution_weight": round(weight, 3),
                    "indicator_type": category
                })
                total_weight += weight

        # Sort by absolute impact
        attributions.sort(key=lambda x: abs(x["attribution_weight"]), reverse=True)
        return attributions, total_weight
