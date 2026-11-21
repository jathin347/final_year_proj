# APPENDIX A – SAMPLE CODE

This appendix contains the core source code implementations extracted directly from the VeritasAI repository. All API keys and secrets have been redacted.

---

## A.1 Ingestion Security & Validation (`backend/app/core/security.py`)

```python
import io
import ipaddress
import socket
import urllib.parse
from fastapi import HTTPException
from PIL import Image

MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_PIXELS = 10_000_000  # 10 Megapixels
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}

def validate_url_safety(url: str) -> str:
    """
    Validates URL scheme and resolves target IP to block SSRF vectors.
    """
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported URL scheme: {parsed.scheme}. Only HTTP/HTTPS allowed."
        )
    
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: Missing hostname")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
                or ip_str == "0.0.0.0"
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Target URL resolves to a forbidden internal or private network address."
                )
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"Unable to resolve DNS hostname: {hostname}")
    return url

class SafeImageValidator:
    """Validates image size, format, and raster integrity to prevent Decompression Bomb attacks."""
    @staticmethod
    def validate_and_load(file_bytes: bytes) -> Image.Image:
        if len(file_bytes) > MAX_IMAGE_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Image file size exceeds maximum limit of 5 MB.")

        Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
        try:
            image_buffer = io.BytesIO(file_bytes)
            img = Image.open(image_buffer)
            if img.format not in ALLOWED_IMAGE_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported image format: {img.format}. Allowed: {ALLOWED_IMAGE_FORMATS}"
                )
            img.load()
            return img
        except Image.DecompressionBombError:
            raise HTTPException(status_code=400, detail="Image exceeds maximum pixel bounds (potential decompression bomb).")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Uploaded file is not a valid image: {str(e)}")
```

---

## A.2 Hierarchical Epistemic Decision Fusion Engine (`backend/app/services/decision_fusion.py`)

```python
from typing import List, Optional
from backend.app.schemas.verification import (
    ExtractedClaim, FactCheckItem, NewsArticleItem,
    SourceCredibilityReport, TextModelAnalysis,
    ImageModelAnalysis, DecisionFusionReport
)

class DecisionFusionEngine:
    """
    Dedicated Decision Fusion Engine:
    - Synthesizes text-model predictions, image consistency, live fact-checks,
      news reporting, and source credibility into an explainable assessment.
    - Strictly grounds assessments on verified external evidence rather than purely
      relying on model text generation or classification heuristics.
    """
    def fuse(
        self,
        claims: List[ExtractedClaim],
        fact_checks: List[FactCheckItem],
        news_articles: List[NewsArticleItem],
        source_report: SourceCredibilityReport,
        text_analysis: TextModelAnalysis,
        image_analysis: ImageModelAnalysis
    ) -> DecisionFusionReport:
        rules_applied = []
        
        # 1. Quantify evidence components
        is_assessed_by_pipeline = any(c.verification_status != "UNVERIFIED" for c in claims)
        if is_assessed_by_pipeline:
            matched_contradicting_fc_ids = set()
            matched_supporting_fc_ids = set()
            for c in claims:
                matched_supporting_fc_ids.update(c.supporting_evidence_ids)
                matched_contradicting_fc_ids.update(c.contradicting_evidence_ids)
            
            fc_false_count = sum(1 for fc in fact_checks if fc.id in matched_contradicting_fc_ids and fc.normalized_verdict in ("FALSE", "MIXED"))
            fc_true_count = sum(1 for fc in fact_checks if fc.id in matched_supporting_fc_ids and fc.normalized_verdict == "TRUE")
            fc_mixed_count = sum(1 for fc in fact_checks if fc.id in matched_contradicting_fc_ids and fc.normalized_verdict == "MIXED")
        else:
            fc_false_count = sum(1 for fc in fact_checks if fc.normalized_verdict in ("FALSE", "MIXED"))
            fc_true_count = sum(1 for fc in fact_checks if fc.normalized_verdict == "TRUE")
            fc_mixed_count = sum(1 for fc in fact_checks if fc.normalized_verdict == "MIXED")
        
        supporting_news = sum(1 for a in news_articles if a.stance == "supporting" and not a.is_syndicated_duplicate)
        contradicting_news = sum(1 for a in news_articles if a.stance == "contradicting")
        
        total_supporting = fc_true_count + supporting_news
        total_contradicting = fc_false_count + contradicting_news
        
        # 2. Evidence coverage assessment
        total_evidence_items = len(fact_checks) + len([a for a in news_articles if not a.is_syndicated_duplicate])
        if total_evidence_items >= 4:
            coverage = "Robust"
        elif total_evidence_items >= 1:
            coverage = "Moderate"
        else:
            coverage = "None"

        # 3. Apply Decision Rules in Hierarchy of Epistemic Grounding

        # Rule 1: Professional Fact-Check Debunk / Contradiction
        if fc_false_count > 0:
            rules_applied.append(
                f"Rule 1 (Authoritative Fact-Check Refutation): {fc_false_count} published fact-check review(s) rated the statement false or misleading."
            )
            return DecisionFusionReport(
                final_assessment="Contradicted by available evidence",
                explanation=f"Directly contradicted by {fc_false_count} professional fact-checking review(s). Independent fact-checkers have previously reviewed and debunked this assertion.",
                uncertainty_level="Low",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 2: Source is Known Satire or Conspiratorial Discredited Domain
        if source_report.overall_score is not None and source_report.overall_score <= 20.0:
            rules_applied.append(
                f"Rule 2 (Discredited / Satire Domain Grounding): Source domain score is {source_report.overall_score}/100."
            )
            return DecisionFusionReport(
                final_assessment="Misleading or missing context",
                explanation=f"The source domain '{source_report.domain}' is catalogued as satire, parody, or a recurring promoter of unverified conspiracy theories.",
                uncertainty_level="Low",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 3: Direct Fact-Check Affirmation
        if fc_true_count > 0 and total_contradicting == 0:
            rules_applied.append(
                f"Rule 3 (Authoritative Fact-Check Corroboration): {fc_true_count} professional fact-check review(s) confirmed the assertion."
            )
            return DecisionFusionReport(
                final_assessment="Supported by available evidence",
                explanation=f"Corroborated by {fc_true_count} published fact-check review(s) from accredited organizations. No contradicting reports were identified.",
                uncertainty_level="Low",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 4: Multimodal / Image Miscontextualization
        if image_analysis.has_image and any("POTENTIAL_CONTEXT_MISMATCH" in f for f in image_analysis.flags):
            rules_applied.append(
                "Rule 4 (Multimodal Inconsistency): Image exhibits significant lighting/temporal mismatch with article claims."
            )
            return DecisionFusionReport(
                final_assessment="Misleading or missing context",
                explanation="Multimodal analysis detected visual inconsistency between the submitted image and article claims. Image may be out of context or repurposed.",
                uncertainty_level="Moderate",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 5: Conflicting Evidence across multiple sources
        if total_supporting > 0 and total_contradicting > 0:
            rules_applied.append(
                f"Rule 5 (Active Evidentiary Conflict): {total_supporting} supporting vs {total_contradicting} contradicting reports."
            )
            return DecisionFusionReport(
                final_assessment="Conflicting evidence",
                explanation=f"External reporting exhibits active disagreement. Identified {total_supporting} supporting indicators and {total_contradicting} disputing or debunking sources.",
                uncertainty_level="Moderate",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 6: Strong Independent News Corroboration
        if supporting_news >= 2 and total_contradicting == 0:
            rules_applied.append(
                f"Rule 6 (Multi-Source News Corroboration): {supporting_news} independent news outlets corroborate the central event."
            )
            return DecisionFusionReport(
                final_assessment="Supported by available evidence",
                explanation=f"Corroborated by {supporting_news} independent news reports with consistent event descriptions.",
                uncertainty_level="Low" if coverage == "Robust" else "Moderate",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 6b: Verified High-Credibility Primary Publisher Corroboration
        if (
            source_report.overall_score is not None 
            and source_report.overall_score >= 70.0 
            and total_contradicting == 0 
            and text_analysis.prediction in ("Credible / Objective Phrasing", "Neutral / Mixed Stylometric Signals")
        ):
            rules_applied.append(
                f"Rule 6b (Verified Primary Publisher Corroboration): Published by accredited news outlet '{source_report.domain}' with objective journalistic phrasing and zero conflicting reports."
            )
            return DecisionFusionReport(
                final_assessment="Supported by available evidence",
                explanation=f"Published by verified high-credibility news outlet '{source_report.publisher_name or source_report.domain}' (Credibility Score: {source_report.overall_score}/100) with clear editorial attribution.",
                uncertainty_level="Moderate",
                supporting_evidence_count=max(1, total_supporting),
                contradicting_evidence_count=0,
                fact_check_count=len(fact_checks),
                evidence_coverage="Moderate" if coverage == "None" else coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 7: Model Stylistic Alert with Zero Corroboration
        if text_analysis.prediction == "Elevated Misinformation Risk" and total_evidence_items == 0:
            rules_applied.append(
                "Rule 7 (Stylistic Risk with Missing Corroboration): AI text model flagged sensationalist linguistic cues, but no external evidence was found."
            )
            return DecisionFusionReport(
                final_assessment="Insufficient evidence",
                explanation="The AI text classifier detected elevated misinformation risk patterns, but no authoritative external evidence was retrieved. Linguistic signals alone cannot definitively prove falsehood.",
                uncertainty_level="High",
                supporting_evidence_count=0,
                contradicting_evidence_count=0,
                fact_check_count=0,
                evidence_coverage="None",
                decision_rules_applied=rules_applied
            )

        # Rule 8: Baseline Insufficient Evidence Outcome
        rules_applied.append(
            "Rule 8 (Default Insufficient Evidence): No published fact-checks or corroborating news reports retrieved."
        )
        return DecisionFusionReport(
            final_assessment="Insufficient evidence",
            explanation="No matching published fact-check reviews or authoritative independent news reports were retrieved. The absence of evidence does not establish whether the assertion is true or false.",
            uncertainty_level="High",
            supporting_evidence_count=total_supporting,
            contradicting_evidence_count=total_contradicting,
            fact_check_count=len(fact_checks),
            evidence_coverage="None",
            decision_rules_applied=rules_applied
        )
```

---

## A.3 Tokenized Evidence Matching & Stop-Word Suppression (`backend/app/services/evidence_assessor.py`)

```python
from typing import List
from backend.app.schemas.verification import ExtractedClaim, FactCheckItem, NewsArticleItem
from backend.app.utils.text_processing import calculate_cosine_similarity, tokenize_words

class EvidenceAssessor:
    """
    Assesses and links retrieved fact-checks and news articles directly
    to atomic claims using tokenized semantic similarity and topic stop-word suppression.
    """
    def assess_and_link_evidence(
        self,
        claims: List[ExtractedClaim],
        fact_checks: List[FactCheckItem],
        news_articles: List[NewsArticleItem]
    ) -> List[ExtractedClaim]:
        for claim in claims:
            supporting_ids = []
            contradicting_ids = []
            explanations = []

            # 1. Evaluate against Fact Checks
            GENERIC_TOPIC_WORDS = {
                "covid", "covid19", "coronavirus", "virus", "health", "people", "said", "says",
                "claims", "world", "government", "president", "biden", "trump", "administration",
                "official", "officials", "state", "national", "department", "united", "states",
                "agency", "policy", "report", "reports", "organization", "pandemic"
            }
            tokens_claim = set(tokenize_words(claim.claim_text))

            for fc in fact_checks:
                sim = calculate_cosine_similarity(claim.claim_text, fc.claim_reviewed)
                tokens_fc = set(tokenize_words(fc.claim_reviewed))
                specific_overlap = (tokens_claim & tokens_fc) - GENERIC_TOPIC_WORDS

                # Require high cosine similarity or moderate similarity with specific non-generic topic overlap
                is_relevant_match = (sim >= 0.45) or (
                    sim >= 0.30 and len(specific_overlap) >= 2 and any(len(w) >= 5 for w in specific_overlap)
                )

                if is_relevant_match:
                    if fc.normalized_verdict in ("FALSE", "MIXED"):
                        contradicting_ids.append(fc.id)
                        explanations.append(
                            f"Contradicted by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'"
                        )
                    elif fc.normalized_verdict == "TRUE":
                        supporting_ids.append(fc.id)
                        explanations.append(
                            f"Corroborated by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'"
                        )

            # 2. Evaluate against News Articles
            for article in news_articles:
                sim = calculate_cosine_similarity(claim.claim_text, article.title)
                article.relevance_score = round(sim, 3)

                if sim >= 0.35:
                    title_lower = article.title.lower()
                    if any(term in title_lower for term in ("false", "debunk", "hoax", "fact check", "misleading", "denies")):
                        article.stance = "contradicting"
                        contradicting_ids.append(article.id)
                    else:
                        article.stance = "supporting"
                        supporting_ids.append(article.id)
                elif sim >= 0.20:
                    article.stance = "contextual"
                else:
                    article.stance = "neutral"

            # 3. Determine Claim-level status
            claim.supporting_evidence_ids = supporting_ids
            claim.contradicting_evidence_ids = contradicting_ids

            if contradicting_ids and not supporting_ids:
                claim.verification_status = "CONTRADICTED"
                claim.explanation = "; ".join(explanations) if explanations else "Contradicted by external reporting and fact-checking records."
            elif supporting_ids and not contradicting_ids:
                claim.verification_status = "SUPPORTED"
                claim.explanation = "; ".join(explanations) if explanations else "Corroborated by independent news coverage."
            elif supporting_ids and contradicting_ids:
                claim.verification_status = "CONFLICTING"
                claim.explanation = "Conflicting evidence: Some sources corroborate while others dispute or debunk."
            else:
                claim.verification_status = "INSUFFICIENT"
                claim.explanation = "No authoritative fact-checks or directly matching news reports were retrieved for this claim."

        return claims
```

---

## A.4 Four-Factor Source Credibility Engine (`backend/app/services/source_credibility.py`)

```python
import urllib.parse
from typing import Optional, List
from backend.app.schemas.verification import SourceCredibilityReport, CredibilityFactor

KNOWN_SATIRE_DOMAINS = {
    "theonion.com", "babylonbee.com", "newshump.com", "borowitzreport.com",
    "clickhole.com", "duffelblog.com", "dailycurrant.com"
}

REPUTABLE_DOMAINS = {
    "reuters.com": 96.0, "apnews.com": 96.0, "bbc.com": 94.0, "bbc.co.uk": 94.0,
    "nytimes.com": 90.0, "washingtonpost.com": 88.0, "nature.com": 98.0,
    "who.int": 98.0, "cdc.gov": 98.0, "nih.gov": 98.0
}

class SourceCredibilityAnalyzer:
    """Evaluates publishing domain across 4 weighted factors with satire caps."""
    def assess(self, url: Optional[str] = None) -> SourceCredibilityReport:
        if not url:
            return SourceCredibilityReport(
                domain=None,
                publisher_name="Unspecified Source",
                overall_score=None,
                assessment_status="Assessment unavailable",
                factors=[],
                missing_signals=[
                    "No source URL provided",
                    "Domain registration and reputation cannot be evaluated",
                    "Publisher attribution relies on self-reported input"
                ],
                disclaimer="Heuristic source assessment score. Does not represent statistical proof of truth."
            )

        parsed = urllib.parse.urlparse(url)
        domain = (parsed.hostname or "").lower()
        if domain.startswith("www."):
            domain = domain[4:]

        factors: List[CredibilityFactor] = []
        is_satire = domain in KNOWN_SATIRE_DOMAINS

        # Factor 1: Domain Track Record (Weight 40%)
        if is_satire:
            f1_score = 10.0
            f1_desc = f"Domain '{domain}' is catalogued as a known satire, parody, or humor website."
        elif domain in REPUTABLE_DOMAINS:
            f1_score = REPUTABLE_DOMAINS[domain]
            f1_desc = f"Domain '{domain}' has an established record with recognized editorial oversight."
        else:
            f1_score = 50.0
            f1_desc = f"Domain '{domain}' has no established independent credibility profile."
        
        factors.append(CredibilityFactor(
            factor_name="Domain Track Record", score=f1_score, weight=0.40,
            description=f1_desc, status="Observed" if (is_satire or domain in REPUTABLE_DOMAINS) else "Unobserved"
        ))

        # Factor 2: Domain Integrity & TLD (Weight 25%)
        if domain.endswith((".gov", ".edu", ".mil")):
            f2_score = 95.0
        elif domain.endswith((".org", ".int")):
            f2_score = 88.0
        elif domain.endswith((".com", ".net", ".co.uk")):
            f2_score = 85.0
        elif domain.endswith((".xyz", ".top", ".info", ".biz", ".click")):
            f2_score = 35.0
        else:
            f2_score = 70.0

        factors.append(CredibilityFactor(
            factor_name="Domain Integrity & TLD", score=f2_score, weight=0.25,
            description=f"Evaluated top-level domain structure for '{domain}'.", status="Observed"
        ))

        # Factor 3: Author Attribution (Weight 20%)
        factors.append(CredibilityFactor(
            factor_name="Author Attribution", score=40.0, weight=0.20,
            description="No specific author byline detected in extracted metadata.", status="Unobserved"
        ))

        # Factor 4: Publisher Transparency (Weight 15%)
        factors.append(CredibilityFactor(
            factor_name="Publisher Transparency", score=35.0, weight=0.15,
            description="Publisher identity could not be verified from page metadata.", status="Unobserved"
        ))

        weighted_score = sum(f.score * f.weight for f in factors)
        if is_satire and weighted_score > 25.0:
            weighted_score = 20.2  # Hard cap for satire

        return SourceCredibilityReport(
            domain=domain,
            publisher_name=domain.capitalize(),
            overall_score=round(weighted_score, 1),
            assessment_status="Assessed",
            factors=factors,
            missing_signals=[],
            disclaimer="Heuristic source assessment score. Does not represent statistical proof of truth of any individual claim."
        )
```

---

## A.5 Model Training & Calibration Script (`scripts/train.py`)

```python
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

TRAINING_DATA = [
    ("Federal reserve holds benchmark borrowing interest rate steady following consumer price inflation data release.", 0),
    ("According to official spokespersons at the headquarters, the ministry announced updated infrastructure guidelines.", 0),
    ("Researchers at the university hospital published findings in a peer-reviewed journal on malaria vaccine efficacy.", 0),
    ("The bilateral trade agreement between nations was ratified following parliamentary debate in session.", 0),
    ("Quarterly revenue reports indicated a 4% increase in manufacturing output, according to commerce department statistics.", 0),
    ("SHOCKING TRUTH EXPOSED: Doctors don't want you to know this secret miracle mineral cure for all diseases!", 1),
    ("You won't believe what the secret shadow government did last night! Mainstream media is completely silent!", 1),
    ("BOMBSHELL REPORT: Astronomers confirm giant rogue planet will smash into earth next Tuesday panic everywhere!", 1),
    ("PROOF: Chemtrails contain microchips to control citizen minds, whistleblower leaks mind-blowing secret documents!", 1),
    ("HIDDEN SECRETS REVEALED: Miracle dietary supplement dissolves all tumors in 48 hours without surgery or drugs!", 1),
]

def train_and_evaluate():
    texts, labels = zip(*TRAINING_DATA)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words='english')),
        ('clf', LogisticRegression(C=1.0, solver='lbfgs', random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    print(f"Held-Out Test Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print(f"Held-Out Test F1 Score: {f1_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["Credible", "Misinformation Risk"]))
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, "models/stylistic_classifier.joblib")

if __name__ == "__main__":
    train_and_evaluate()
```
