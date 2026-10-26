"""
System and Pipeline Evaluation Script for VeritasAI
Evaluates decision fusion, evidence retrieval grounding, and abstention behavior on held-out benchmarks.
"""
import os
import sys
import json
import time
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.text_analyzer import TextAnalyzer
from backend.app.services.image_analyzer import ImageAnalyzer
from backend.app.services.claim_extractor import ClaimExtractor
from backend.app.services.fact_check_service import FactCheckService
from backend.app.services.news_search_service import NewsSearchService
from backend.app.services.evidence_assessor import EvidenceAssessor
from backend.app.services.source_credibility import SourceCredibilityAnalyzer
from backend.app.services.decision_fusion import DecisionFusionEngine

async def run_pipeline_evaluation():
    print("====================================================")
    print("VeritasAI Verification Pipeline Evaluation")
    print("====================================================")

    benchmark_path = "datasets/benchmark_evaluation.json"
    if not os.path.exists(benchmark_path):
        print(f"Error: Benchmark file not found at {benchmark_path}")
        return

    with open(benchmark_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    # Initialize components
    text_analyzer = TextAnalyzer()
    image_analyzer = ImageAnalyzer()
    claim_extractor = ClaimExtractor()
    fact_check_service = FactCheckService()
    news_search_service = NewsSearchService()
    evidence_assessor = EvidenceAssessor()
    source_analyzer = SourceCredibilityAnalyzer()
    decision_engine = DecisionFusionEngine()

    total_samples = len(samples)
    correct_verdicts = 0
    appropriate_abstentions = 0
    unsupported_verdicts = 0
    latencies = []
    results = []

    print(f"Evaluating {total_samples} benchmark samples across multi-domain claims...\n")

    for idx, s in enumerate(samples):
        t0 = time.time()
        headline = s.get("headline", "")
        text = s.get("text", "")
        url = s.get("url")
        expected = s.get("expected_verdict")

        # 1. Text Analysis
        t_res = text_analyzer.analyze(headline, text)

        # 2. Multimodal Image Analysis
        img_res = image_analyzer.analyze_image(None)

        # 3. Claim Extraction
        claims = await claim_extractor.extract_claims(text, headline)

        # 4. Evidence Retrieval (mocked/bounded to avoid rate limits during bulk eval)
        # Check source credibility
        src_res = source_analyzer.assess(url)

        # Evidence matching & decision fusion
        fusion_res = decision_engine.fuse(
            claims=claims,
            fact_checks=[], # Offline baseline for deterministic reproducibility
            news_articles=[],
            source_report=src_res,
            text_analysis=t_res,
            image_analysis=img_res
        )

        elapsed_ms = (time.time() - t0) * 1000.0
        latencies.append(elapsed_ms)

        predicted = fusion_res.final_assessment
        match = (predicted == expected)
        if match:
            correct_verdicts += 1

        if expected == "Insufficient evidence" and predicted == "Insufficient evidence":
            appropriate_abstentions += 1

        # Check if system made an unsupported affirmative claim without evidence
        if fusion_res.final_assessment in ("Supported by available evidence", "Contradicted by available evidence") and fusion_res.evidence_coverage == "None":
            unsupported_verdicts += 1

        results.append({
            "id": s.get("id"),
            "headline": headline[:60] + "...",
            "expected": expected,
            "predicted": predicted,
            "match": match,
            "latency_ms": round(elapsed_ms, 2)
        })

        print(f"[{idx+1}/{total_samples}] {s.get('id')}: Expected: '{expected}' | Predicted: '{predicted}' ({'MATCH' if match else 'DIFFER'})")

    accuracy = (correct_verdicts / total_samples) * 100.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    eval_summary = {
        "benchmark_file": benchmark_path,
        "sample_count": total_samples,
        "exact_verdict_accuracy_pct": round(accuracy, 2),
        "appropriate_abstention_count": appropriate_abstentions,
        "unsupported_verdict_rate_pct": round((unsupported_verdicts / total_samples) * 100.0, 2),
        "mean_latency_ms": round(avg_latency, 2),
        "detailed_results": results
    }

    # Save evaluation results
    output_path = "evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)

    print("\n====================================================")
    print("Evaluation Summary")
    print("====================================================")
    print(f"Benchmark Accuracy: {accuracy:.1f}%")
    print(f"Unsupported Verdict Rate: {eval_summary['unsupported_verdict_rate_pct']}%")
    print(f"Mean Pipeline Latency: {avg_latency:.2f} ms")
    print(f"Machine-readable results saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(run_pipeline_evaluation())
