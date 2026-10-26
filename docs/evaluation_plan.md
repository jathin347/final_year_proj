# VeritasAI Evaluation Plan & Benchmark Methodology

## 1. Evaluation Objectives
The evaluation suite independently measures:
1. **Linguistic Stylometric Classifier Performance**: Accuracy, Precision, Recall, F1-Score, and Confusion Matrix on held-out test splits.
2. **Decision Fusion & Grounding Accuracy**: Alignment between the fused epistemic verdict and ground-truth validation labels.
3. **Epistemic Abstention & Unsupported Verdict Rates**: Evaluating whether the system responsibly abstains with "Insufficient evidence" when evidence is absent, rather than generating unsupported claims.
4. **Operational Latency**: Per-module latency breakdown and end-to-end processing time.

---

## 2. Classifier Evaluation Metrics

Evaluated via `python scripts/train.py`:
- **Training Samples**: 30 (stratified balanced classes)
- **Held-Out Test Samples**: 10 (stratified balanced classes)
- **Data Leakage Safeguard**: Feature extraction (TF-IDF vectorizer) is strictly fitted on the training split only.

### Measured Classifier Results:
```
Held-Out Test Accuracy: 90.00%
Held-Out Test F1 Score: 0.9091

Classification Report:
                     precision    recall  f1-score   support

           Credible       1.00      0.80      0.89         5
Misinformation Risk       0.83      1.00      0.91         5

           accuracy                           0.90        10
          macro avg       0.92      0.90      0.90        10
       weighted avg       0.92      0.90      0.90        10

Confusion Matrix:
[[4 1]
 [0 5]]
```

---

## 3. End-to-End Pipeline & Abstention Evaluation

Evaluated via `python scripts/evaluate.py`:
- **Dataset**: `datasets/benchmark_evaluation.json` (8 diverse real-world multi-domain cases).
- **Unsupported Verdict Rate**: Defined as the percentage of cases where the pipeline returned an affirmative confirmation (`Supported by available evidence` or `Contradicted by available evidence`) despite zero external evidence being available.
- **Measured Unsupported Verdict Rate**: **0.0%** (100% compliant with the epistemic grounding principle).
- **Mean Pipeline Latency**: **0.23 ms** (in-memory pipeline test).

---

## 4. Reproducible Execution Commands

To reproduce all evaluations from scratch:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run classifier training & evaluation
python scripts/train.py

# 3. Run end-to-end pipeline benchmark evaluation
python scripts/evaluate.py

# 4. Run automated test suite
pytest backend/tests/ -v
```
