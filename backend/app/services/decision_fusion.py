from typing import List, Dict, Any, Optional
from backend.app.api.schemas.analysis import (
    DecisionFusionReport,
    TextModelAnalysis,
    ImageModelAnalysis
)
from backend.app.api.schemas.claims import ExtractedClaim
from backend.app.api.schemas.evidence import (
    FactCheckItem,
    NewsArticleItem,
    SourceCredibilityReport
)

class DecisionFusionEngine:
    """
    Dedicated Decision Fusion Engine:
    - Synthesizes text-model predictions, image consistency, live fact-checks,
      news reporting, and source credibility into an explainable assessment.
    - Strictly grounds assessments on verified external evidence rather than purely
      relying on model text generation or classification heuristics.
    - Transparently defines rules applied and uncertainty levels.
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
        fc_false_count = sum(1 for fc in fact_checks if fc.normalized_verdict == "FALSE")
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
                explanation=(
                    f"Directly contradicted by {fc_false_count} professional fact-checking review(s). "
                    "Independent fact-checkers have previously reviewed and debunked this assertion."
                ),
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
                explanation=(
                    f"The source domain '{source_report.domain}' is catalogued as satire, parody, or a recurring promoter "
                    "of unverified conspiracy theories. Content lacks credible journalistic oversight."
                ),
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
                explanation=(
                    f"Corroborated by {fc_true_count} published fact-check review(s) from accredited organizations. "
                    "No contradicting reports were identified."
                ),
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
                explanation=(
                    "Multimodal analysis detected visual inconsistency between the submitted image and article claims "
                    "(e.g., lighting/daylight discrepancy vs claimed event timing). "
                    "Image may be out of context or repurposed."
                ),
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
                explanation=(
                    "External reporting exhibits active disagreement or evolving coverage. "
                    f"Identified {total_supporting} supporting indicators and {total_contradicting} disputing or debunking sources."
                ),
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
                explanation=(
                    f"Corroborated by {supporting_news} independent news reports with consistent event descriptions. "
                    "No published debunks were identified."
                ),
                uncertainty_level="Low" if coverage == "Robust" else "Moderate",
                supporting_evidence_count=total_supporting,
                contradicting_evidence_count=total_contradicting,
                fact_check_count=len(fact_checks),
                evidence_coverage=coverage,
                decision_rules_applied=rules_applied
            )

        # Rule 7: Model Stylistic Alert with Zero Corroboration
        if text_analysis.prediction == "Elevated Misinformation Risk" and total_evidence_items == 0:
            rules_applied.append(
                "Rule 7 (Stylistic Risk with Missing Corroboration): AI text model flagged sensationalist linguistic cues, but no external evidence was found."
            )
            return DecisionFusionReport(
                final_assessment="Insufficient evidence",
                explanation=(
                    "The AI text classifier detected elevated misinformation risk patterns (sensationalist phrasing or clickbait markers), "
                    "but no authoritative external evidence or published fact-checks were retrieved. "
                    "Linguistic signals alone cannot definitively prove falsehood without corroborating external records."
                ),
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
            explanation=(
                "No matching published fact-check reviews or authoritative independent news reports were retrieved. "
                "The absence of evidence does not establish whether the assertion is true or false."
            ),
            uncertainty_level="High",
            supporting_evidence_count=total_supporting,
            contradicting_evidence_count=total_contradicting,
            fact_check_count=len(fact_checks),
            evidence_coverage="None",
            decision_rules_applied=rules_applied
        )
