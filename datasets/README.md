# VeritasAI Verification Datasets & Benchmarks

## Overview
This directory contains evaluation benchmarks and training references for fake-news detection and evidence-based claim verification.

## Datasets Included
1. **`benchmark_evaluation.json`**:
   - A curated evaluation dataset of 20 verified real-world news statements and claims.
   - Covers multiple domains: Health, Politics, Climate/Science, Discredited Conspiracies, and Local Reports.
   - Ground truth labels:
     - `SUPPORTED`: Validated factual assertions with multi-source corroboration.
     - `CONTRADICTED`: Debunked assertions with documented ClaimReview entries or scientific refutation.
     - `MISLEADING`: Out-of-context assertions or repurposed media.
     - `INSUFFICIENT`: Genuine uncorroborated local claims where responsible systems must abstain.
   - Used by `scripts/evaluate.py` to evaluate classification metrics (Accuracy, Precision, Recall, F1, Confusion Matrix) and epistemic abstention rates.

## Public Datasets Reference
For full-scale pretraining and fine-tuning:
- **LIAR**: 12.8K human-labeled short statements from PolitiFact (`Creative Commons Attribution-NonCommercial 4.0`).
- **WELFake**: 72K balanced real and fake news articles aggregated from Kaggle, McIntire, and Reuters.
- **FEVER**: Fact Extraction and VERification dataset for claims paired with Wikipedia evidence.
