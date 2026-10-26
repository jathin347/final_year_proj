from typing import Dict, Any, List
from backend.app.api.schemas.analysis import (
    TextModelAnalysis,
    ImageModelAnalysis,
    DecisionFusionReport
)
from backend.app.api.schemas.evidence import SourceCredibilityReport

class ExplanationService:
    """
    Transparent Explainability Service:
    - Synthesizes model limitations, evidentiary basis, and uncertainty drivers.
    - Clarifies difference between AI linguistic heuristics and external factual verification.
    """
    @staticmethod
    def generate_methodology_disclaimer() -> str:
        return (
            "VeritasAI uses a hybrid verification pipeline combining stylometric AI modeling, "
            "live Google Fact Check queries, GDELT global news monitoring, and source transparency heuristics. "
            "A model prediction reflects linguistic patterns and cannot prove factual veracity without external evidence."
        )

    @staticmethod
    def format_audit_summary(
        decision: DecisionFusionReport,
        text_analysis: TextModelAnalysis,
        source_report: SourceCredibilityReport
    ) -> Dict[str, Any]:
        return {
            "verdict": decision.final_assessment,
            "uncertainty": decision.uncertainty_level,
            "applied_rules": decision.decision_rules_applied,
            "model_attribution_tokens": [t["token"] for t in text_analysis.key_attribution_tokens[:5]],
            "source_status": source_report.assessment_status,
            "source_score": source_report.overall_score
        }
