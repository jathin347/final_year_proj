# VeritasAI Methodology & Decision Logic

## 1. Epistemic Verification Principle
A primary design requirement of VeritasAI is distinguishing **AI-generated model predictions** from **evidence-based factual assessments**.

- **What an AI Classifier can do:** Detect stylistic anomalies, emotional manipulation, sensationalist clickbait phrasing, excessive punctuation, and lack of attribution markers.
- **What an AI Classifier cannot do:** Independently confirm real-world events or verify facts without external evidence.

Therefore, our architecture enforces that **no statement is marked TRUE or FALSE purely because a model assigned a probability score**. External evidence retrieval and claim-evidence matching are treated as mandatory, distinct components.

## 2. Text Stylometric Analysis & Feature Attribution

The text analysis pipeline combines lexical pattern matching with a calibrated logistic classifier:

### 2.1 Linguistic Signals
1. **Sensationalism Index ($S \in [0, 1]$):**
   $$S = \min\left(1.0, 4.0 \cdot R_{\text{caps}} + 5.0 \cdot R_{\text{punct}} + 0.3 \cdot N_{\text{clickbait}}\right)$$
   Where:
   - $R_{\text{caps}}$: Ratio of all-caps words (excluding short acronyms) to total word count.
   - $R_{\text{punct}}$: Ratio of exclamation marks and question marks to total word count.
   - $N_{\text{clickbait}}$: Count of matching clickbait regex patterns (e.g., `"you won't believe"`, `"shocking truth"`, `"doctors don't want you to know"`).

2. **Attribution Density ($A \in [0, 1]$):**
   Frequency of journalistic attribution phrases (`"according to"`, `"spokesperson stated"`, `"data shows"`, `"peer-reviewed"`, `"confirmed by"`). Higher density directly reduces calculated misinformation risk.

3. **Token-Level Feature Attribution:**
   Identifies specific tokens contributing toward risk (e.g., `miracle`, `secret`, `hoax`, `cabal`) or toward credibility (e.g., `study`, `research`, `reuters`, `official`).

## 3. Factual Claim Extraction

The claim extractor parses news content into discrete, testable factual claims adhering to the schema:
- **`claim_id`**: Deterministic identifier (`c1`, `c2`, etc.).
- **`claim_text`**: The verbatim factual assertion.
- **`importance`**: `HIGH`, `MEDIUM`, or `LOW`.
- **`category`**: Politics, Science, Health, Economy, International, General.
- **`named_entities`**: Extracted organizations, persons, and locations.
- **`search_queries`**: Concise 4–7 word search phrases formulated for search APIs.

## 4. Source Credibility Assessment Heuristic

The source credibility score ranges from 0 to 100 based on observed domain attributes:

| Factor | Weight | Evaluation Criteria |
| :--- | :--- | :--- |
| **Domain Track Record** | 40% | Matches against curated registries of accredited news organizations (90–98 pts), neutral unindexed domains (50 pts), or catalogued satire/discredited conspiracy outlets (10–15 pts). |
| **Domain Integrity & TLD** | 25% | Institutional TLDs (.gov = 95 pts, .edu = 92 pts), commercial (.com = 60–85 pts), spam/disposable TLDs (.xyz, .biz, .top = 25 pts), and clone/typosquatting penalties. |
| **Author Attribution** | 20% | Explicit author byline present (85 pts) vs missing attribution (40 pts). |
| **Publisher Transparency** | 15% | Clear publisher branding and metadata imprint (75 pts) vs unverified (35 pts). |

### Mathematical Formula:
$$\text{Score}_{\text{raw}} = \sum_{i=1}^{4} w_i \cdot s_i$$
If the domain is catalogued as satire or conspiracy, the overall score is strictly capped:
$$\text{Score} = \min(\text{Score}_{\text{raw}}, \text{Score}_{\text{flagged}} + 10.0)$$

## 5. Epistemic Decision Fusion Hierarchy

The decision fusion module applies a strict priority cascade:

1. **Rule 1 (Direct Fact-Check Refutation):**
   If $\ge 1$ published fact-check reviews rated the claim FALSE, return **"Contradicted by available evidence"** with *Low Uncertainty*.
2. **Rule 2 (Discredited / Satire Domain):**
   If the source score is $\le 20/100$, return **"Misleading or missing context"** with *Low Uncertainty*.
3. **Rule 3 (Direct Fact-Check Affirmation):**
   If published fact-checks confirmed the claim with no contradictions, return **"Supported by available evidence"** with *Low Uncertainty*.
4. **Rule 4 (Multimodal Inconsistency):**
   If the submitted image exhibits temporal or lighting mismatch with article claims, return **"Misleading or missing context"** with *Moderate Uncertainty*.
5. **Rule 5 (Conflicting Coverage):**
   If both supporting and disputing reports exist, return **"Conflicting evidence"** with *Moderate Uncertainty*.
6. **Rule 6 (Multi-Source News Corroboration):**
   If $\ge 2$ independent reputable outlets corroborate the event, return **"Supported by available evidence"** with *Moderate/Low Uncertainty*.
7. **Rule 7 (Missing Evidence Abstention):**
   If zero external records or fact-checks are found, the system returns **"Insufficient evidence"** with *High Uncertainty*. **The system abstains from guessing**.
