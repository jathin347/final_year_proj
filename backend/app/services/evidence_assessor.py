import time
from typing import List, Dict, Any, Tuple
from backend.app.api.schemas.claims import ExtractedClaim
from backend.app.api.schemas.evidence import FactCheckItem, NewsArticleItem
from backend.app.utils.text_processing import calculate_cosine_similarity, tokenize_words

class EvidenceAssessor:
    """
    Evidence-Claim Matching Engine:
    - Compares extracted claims against retrieved fact-checks and news articles.
    - Classifies relationship into SUPPORTING, CONTRADICTING, CONTEXTUAL, or NEUTRAL.
    - Updates claim verification status based on genuine evidence grounding.
    - Never fabricates quotations or evidence links.
    """
    def __init__(self):
        pass

    def match_claims_with_evidence(
        self,
        claims: List[ExtractedClaim],
        fact_checks: List[FactCheckItem],
        news_articles: List[NewsArticleItem]
    ) -> List[ExtractedClaim]:
        if not claims:
            return []

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
                    if fc.normalized_verdict == "FALSE":
                        contradicting_ids.append(fc.id)
                        explanations.append(
                            f"Contradicted by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'"
                        )
                    elif fc.normalized_verdict == "TRUE":
                        supporting_ids.append(fc.id)
                        explanations.append(
                            f"Corroborated by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'"
                        )
                    elif fc.normalized_verdict == "MIXED":
                        contradicting_ids.append(fc.id)
                        explanations.append(
                            f"Flagged as mixed/partly false by {fc.fact_checker_publisher} ('{fc.original_rating}')"
                        )

            # 2. Evaluate against News Articles
            for article in news_articles:
                sim = calculate_cosine_similarity(claim.claim_text, article.title)
                article.relevance_score = round(sim, 3)

                # Assess stance based on title keywords and similarity
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
