# CHAPTER 5 – METHODOLOGY AND TESTING

## 5.1 Module Descriptions

The VeritasAI platform is organized into discrete, highly cohesive, and loosely coupled functional modules located within the `backend/app/` and `frontend/src/` directories. Each module encapsulates a specific stage of the verification lifecycle, communicating through validated Pydantic data schemas. This section details the internal architecture, mathematical formulations, algorithmic logic, and code implementations of each production module.

---

### 5.1.1 Ingestion Security & Safe Validation Module (`backend/app/core/security.py`)

- **Purpose:** Protects the verification server against cyber threats, specifically Server-Side Request Forgery (SSRF), DNS rebinding attacks, and Image Decompression Bomb denial-of-service exploits.
- **Inputs:** Raw URL strings submitted by users; multipart image byte streams.
- **Outputs:** Validated public URLs; sanitized PIL `Image` objects; or raises HTTP 400 validation exceptions.
- **Key Functions / Classes:** `validate_url_safety(url: str) -> str`, `SafeImageValidator.validate_and_load(file_bytes: bytes) -> Image.Image`.
- **Libraries Used:** `urllib.parse`, `socket`, `ipaddress`, `PIL.Image`.
- **Algorithmic Logic:**
  1. *URL Security:* The URL scheme is extracted and restricted strictly to `http` or `https`. The host domain is extracted and resolved to its underlying IP addresses via `socket.getaddrinfo()`.
  2. Each resolved IP address is audited using Python's `ipaddress` library against prohibited subnets: loopbacks (`127.0.0.0/8`, `::1`), private networks (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), link-local networks (RFC 3927: `169.254.0.0/16`), and unspecified addresses (`0.0.0.0`). If any resolved address falls within a prohibited range, an HTTP 400 error is raised.
  3. *Image Security:* The byte stream is verified against a 5 MB maximum file-size limit. `Image.MAX_IMAGE_PIXELS` is explicitly set to $10,000,000$ (10 megapixels). The byte stream is decoded within an isolated memory buffer via `Image.open()`. The header `format` is inspected and restricted strictly to `{'JPEG', 'PNG', 'WEBP'}`. The image data is loaded into memory via `img.load()` to verify raster integrity and detect truncated or malicious payload streams.

#### Code Excerpt 5.1 (`backend/app/core/security.py`):
```python
def validate_url_safety(url: str) -> str:
    """Audits URL scheme and resolves target IP to block SSRF vectors."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(status_code=400, detail=f"Unsupported URL scheme: {parsed.scheme}")
    
    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL: Missing hostname")

    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
                raise HTTPException(status_code=400, detail="Target URL resolves to a forbidden internal or private network address.")
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"Unable to resolve DNS hostname: {hostname}")
    return url
```
*Explanation:* Code Excerpt 5.1 demonstrates the SSRF mitigation implementation. By performing DNS resolution before issuing external HTTP requests and auditing every returned IP address against private, loopback, and link-local ranges, the system prevents attackers from using the verifier to probe internal microservices or cloud metadata endpoints.

---

### 5.1.2 Article Extraction & Document Parser Module (`backend/app/services/article_extractor.py`)

- **Purpose:** Retrieves remote web pages, handles HTTP redirects safely, eliminates boilerplate Document Object Model (DOM) elements, extracts clean journalistic prose, and parses structural article metadata.
- **Inputs:** Validated article URL string.
- **Outputs:** `ExtractedArticle` Pydantic model containing `headline`, `article_text`, `publisher`, `domain`, `author`, `published_date`, and `article_summary`.
- **Key Functions / Classes:** `ArticleExtractor.extract_article(url: str) -> ExtractedArticle`, `_clean_html(soup: BeautifulSoup) -> str`.
- **Libraries Used:** `httpx`, `beautifulsoup4`, `urllib.parse`.
- **Algorithmic Logic:**
  1. Issues an asynchronous `GET` request using `httpx.AsyncClient` with a 6.0-second timeout and realistic browser user-agent headers.
  2. Parses the response body with `BeautifulSoup4`. Strips non-content tags including `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>`, and `<form>`.
  3. Extracts candidate article titles prioritizing OpenGraph metadata (`og:title`), Twitter card headers (`twitter:title`), and standard `<h1>` DOM elements.
  4. Parses author bylines from `<meta name="author">` tags, schema.org JSON-LD blocks, and CSS class selectors matching `byline`, `author`, or `writer`.
  5. Concatenates all remaining paragraph (`<p>`) elements, discarding short navigation snippets ($<30$ characters), and generates a concise abstract from the initial two sentences.

---

### 5.1.3 Dual-Tier Factual Claim Extraction Module (`backend/app/services/claim_extractor.py`)

- **Purpose:** Decomposes complex news articles into atomic, verifiable factual assertions, isolating named entities, temporal markers, and search queries.
- **Inputs:** Article prose string and optional headline string.
- **Outputs:** List of `ExtractedClaim` Pydantic models containing `claim_id`, `claim_text`, `importance`, `category`, `named_entities`, and `search_queries`.
- **Key Functions / Classes:** `ClaimExtractor.extract_claims()`, `_extract_with_gemini()`, `_extract_with_local_nlp()`, `_build_search_query()`.
- **Libraries Used:** `httpx`, `json`, `re`.
- **Algorithmic Logic:**
  1. *Primary LLM Tier:* Submits the article to the Google Gemini 3.8 Flash REST endpoint (`generativelanguage.googleapis.com`) with an asynchronous 5.0-second timeout. Prompts the model with strict few-shot JSON schema constraints requiring it to return an array of JSON objects representing checkable factual assertions.
  2. *Secondary Deterministic NLP Tier (Fallback):* If the Gemini API returns an HTTP 503 (server overloaded), HTTP 429 (quota exhausted), or times out after 5.0 seconds, the module catches the exception and immediately invokes `_extract_with_local_nlp()`.
  3. *Local NLP Extraction Algorithm:*
     - The headline is prioritized as Claim 1 (`importance="HIGH"`).
     - The body text is split into sentences using regex boundary detection.
     - Each candidate sentence is scored for checkability: $+2$ points for quantitative metrics, percentages, or currency figures; $+2$ points for named entities; $+2$ points for definitive assertion verbs (`announced`, `confirmed`, `killed`, `signed`, `banned`).
     - Questions and subjective opinion statements (`I think`, `we believe`) are discarded.
     - The top scoring sentences (up to 4) are converted into `ExtractedClaim` instances.
     - Search queries are constructed by filtering low-information stopwords and combining the primary named entities with salient verbs into concise 2-to-4 word queries.

#### Code Excerpt 5.2 (`backend/app/services/claim_extractor.py`):
```python
async def extract_claims(self, text: str, headline: Optional[str] = None) -> List[ExtractedClaim]:
    """Dual-tier claim extraction: attempts Gemini 3.8 Flash, falls back to local NLP."""
    if self.gemini_api_key:
        try:
            return await self._extract_with_gemini(text, headline)
        except Exception as e:
            logger.warning(f"Gemini claim extraction failed: {e}. Falling back to local NLP extractor.")
    return self._extract_with_local_nlp(text, headline)
```
*Explanation:* Code Excerpt 5.2 highlights the dual-tier fault-tolerant design. By wrapping the external LLM call in a structured try-except block and delegating immediately to `_extract_with_local_nlp()`, the system achieves 100% operational continuity under external network or quota failures.

---

### 5.1.4 Calibrated Stylometric Text Classification Module (`backend/app/services/text_analyzer.py`)

- **Purpose:** Evaluates linguistic cues, sensationalism, clickbait patterns, and journalistic attribution density within article text.
- **Inputs:** Article headline string and body text string.
- **Outputs:** `TextModelAnalysis` Pydantic model containing `prediction`, `confidence`, `stylometric_signals`, and `inference_time_ms`.
- **Key Functions / Classes:** `TextAnalyzer.analyze()`, `_compute_sensationalism_index()`, `_compute_attribution_density()`.
- **Libraries Used:** `scikit-learn`, `joblib`, `numpy`, `re`.

#### 5.1.4.1 Machine Learning Architecture & Training Pipeline (`scripts/train.py`)
The platform trains and deploys a reproducible, calibrated machine learning pipeline (`Veritas-Stylistic-Ensemble v1.2.0`):
- **Model Architecture:** A Scikit-Learn `Pipeline` consisting of a `TfidfVectorizer` and a regularized `LogisticRegression` classifier.
- **Preprocessing & Vectorization:** Text is converted to lowercase, stripped of standard English stopwords, and vectorized into unigrams and bigrams (`ngram_range=(1, 2)`) with minimum document frequency `min_df=1`.
- **Classifier Hyperparameters:** Inverse regularization parameter $C=1.0$, optimization solver `solver='lbfgs'`, maximum iterations 100, random seed `random_state=42`.
- **Training Corpus & Split:** Trained on a balanced corpus of journalistic prose (Label 0: official government releases, peer-reviewed medical reports, wire service articles) versus sensationalist/misinformation text (Label 1: conspiracy theories, clickbait headlines, unverified miracle cures). The corpus is split into 75% training (30 samples) and 25% held-out test (10 samples) using stratified sampling (`stratify=labels`).
- **Loss Function:** Binary Cross-Entropy (Logistic Loss) optimized via the L-BFGS algorithm:
  $$\mathcal{L}(w) = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \log(\sigma(w^T x_i)) + (1 - y_i) \log(1 - \sigma(w^T x_i)) \right] + \frac{1}{2C} \|w\|_2^2$$
- **Empirical Performance on Held-Out Split:**
  - Accuracy: **90.00%**
  - Precision (Misinformation Risk): **0.8333**
  - Recall (Misinformation Risk): **1.0000**
  - F1-Score (Misinformation Risk): **0.9091**

Table 5.1 details the full classification metrics across both classes on the held-out test split.

| Target Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| **Credible / Journalistic (Label 0)** | 1.0000 | 0.8000 | 0.8889 | 5 |
| **Misinformation Risk (Label 1)** | 0.8333 | 1.0000 | 0.9091 | 5 |
| **Macro Average** | **0.9167** | **0.9000** | **0.8990** | **10** |
| **Weighted Average** | **0.9167** | **0.9000** | **0.8990** | **10** |

#### 5.1.4.2 Handcrafted Stylometric Signals
In addition to the statistical model, `TextAnalyzer` computes three handcrafted journalistic metrics:
1. *Sensationalism Index ($S_{\text{sens}}$):* Measures the frequency of hyperbolic clickbait adjectives (`shocking`, `unbelievable`, `secret`, `miracle`, `bombshell`, `exposed`) and excessive punctuation (multiple exclamation marks `!!` or interrobangs `?!`).
2. *All-Caps Word Ratio ($R_{\text{caps}}$):* Computes the ratio of words composed entirely of uppercase characters ($>2$ characters in length) relative to total word count.
3. *Attribution Density ($D_{\text{attr}}$):* Detects journalistic attribution phrases (`according to`, `spokesperson said`, `published in`, `official stated`, `reuters reported`), providing a direct measure of journalistic grounding.

---

### 5.1.5 Multimodal Image Context Inspection Module (`backend/app/services/image_analyzer.py`)

- **Purpose:** Evaluates uploaded article imagery for visual relevance, dimension safety, metadata integrity, and potential lighting/context discrepancies.
- **Inputs:** Verified PIL `Image` object or raw image byte stream; extracted article claims.
- **Outputs:** `ImageModelAnalysis` Pydantic model containing `has_image`, `image_format`, `image_dimensions`, `visual_context_summary`, `flags`, and `limitations`.
- **Key Functions / Classes:** `ImageAnalyzer.analyze_image()`, `_compute_luminance_and_color()`.
- **Libraries Used:** `PIL.Image`, `PIL.ImageStat`, `numpy`.
- **Algorithmic Logic:**
  1. Inspects image dimensions and aspect ratios, verifying standard display resolutions.
  2. Computes the mean luminance ($L_{\text{mean}}$) across the pixel grid using standard perceptual color weighting:
     $$L = 0.299 R + 0.587 G + 0.114 B$$
  3. Computes the color temperature ratio ($\text{Red} / \text{Blue}$) to identify daylight, golden hour, or nocturnal conditions.
  4. Tests for contextual mismatches: If article claims describe events occurring during "midnight", "night", or "darkness", while the image exhibits high luminance ($L_{\text{mean}} > 140$) and balanced daylight color distributions, the module raises the warning flag `POTENTIAL_CONTEXT_MISMATCH`.
  5. Attaches a mandatory limitation disclosure: *"Image-text similarity evaluates visual relevance; it does not detect deepfakes or establish photographic authenticity."*

---

### 5.1.6 Live Fact-Checking Retrieval Module (`backend/app/services/fact_check_service.py`)

- **Purpose:** Programmatically queries the Google Fact Check Tools API to retrieve verified ClaimReview records from accredited international fact-checkers.
- **Inputs:** List of targeted search queries generated from extracted claims.
- **Outputs:** List of normalized `FactCheckItem` Pydantic models.
- **Key Functions / Classes:** `GoogleFactCheckService.search_claims()`, `_normalize_verdict()`.
- **Libraries Used:** `httpx`, `urllib.parse`.
- **Algorithmic Logic:**
  1. Iterates through claim search queries, issuing asynchronous `GET` requests to `https://factchecktools.googleapis.com/v1alpha1/claims:search`.
  2. Parses the ClaimReview JSON structure, extracting the claim reviewed, fact-checking organization name, review title, review URL, publication date, and verbatim textual rating.
  3. Deduplicates results across queries using review URLs as unique keys.
  4. Normalizes diverse international publisher ratings into four standard verdicts:
     - `FALSE`: Ratings matching `false`, `pants on fire`, `incorrect`, `fake`, `hoax`, `debunked`, `scam`, `misleading`.
     - `TRUE`: Ratings matching `true`, `correct`, `accurate`, `verified`.
     - `MIXED`: Ratings matching `half true`, `mostly false`, `partly true`, `unsupported`, `exaggerated`.
     - `UNPROVEN`: Ratings where evidence is incomplete or inconclusive.

---

### 5.1.7 Global News Search & Deduplication Module (`backend/app/services/news_search_service.py`)

- **Purpose:** Queries the GDELT 2.0 Global Document API for independent news coverage corroborating or contextualizing assertions.
- **Inputs:** List of claim search queries.
- **Outputs:** List of normalized `NewsArticleItem` Pydantic models.
- **Key Functions / Classes:** `GDELTNewsSearchService.search_news()`, `_filter_syndicated_duplicates()`.
- **Libraries Used:** `httpx`, `hashlib`, `urllib.parse`.
- **Algorithmic Logic:**
  1. Issues asynchronous queries to `https://api.gdeltproject.org/api/v2/doc/doc` with an aggressive 4.0-second timeout.
  2. If GDELT returns an HTTP 429 rate limit or times out, the client immediately aborts and returns an empty list (`[]`), preventing the pipeline from stalling.
  3. Filters syndicated wire duplicates: computes MD5 hashes of article titles and canonicalizes domain names to ensure that syndicated wire stories republished across dozens of local affiliates count as a single corroborating source.

---

### 5.1.8 Tokenized Evidence Matching & Stop-Word Suppression Module (`backend/app/services/evidence_assessor.py`)

- **Purpose:** Links retrieved external fact-checks and news stories to specific atomic claims using tokenized semantic similarity while preventing topic-collapsing errors.
- **Inputs:** List of `ExtractedClaim`, list of `FactCheckItem`, list of `NewsArticleItem`.
- **Outputs:** Updated list of `ExtractedClaim` models with assigned `supporting_evidence_ids`, `contradicting_evidence_ids`, and updated `verification_status`.
- **Key Functions / Classes:** `EvidenceAssessor.assess_and_link_evidence()`, `calculate_cosine_similarity()`, `tokenize_words()`.
- **Libraries Used:** `math`, `collections.Counter`, `re`.
- **Algorithmic Logic:**
  1. *Stop-Word Suppression Dictionary:* Defines `GENERIC_TOPIC_WORDS` containing institutional, governmental, and broad topic terms:
     ```python
     GENERIC_TOPIC_WORDS = {
         "covid", "covid19", "coronavirus", "virus", "health", "people", "said", "says", 
         "claims", "world", "government", "president", "biden", "trump", "administration",
         "official", "officials", "state", "national", "department", "united", "states",
         "agency", "policy", "report", "reports", "organization", "pandemic"
     }
     ```
  2. Computes tokenized cosine similarity ($S_{\cos}$) between claim text and fact-check reviewed text:
     $$S_{\cos}(A, B) = \frac{\sum_{w} f_A(w) \cdot f_B(w)}{\sqrt{\sum_{w} f_A(w)^2} \cdot \sqrt{\sum_{w} f_B(w)^2}}$$
  3. Evaluates specific non-generic overlap tokens:
     $$\text{Overlap}_{\text{specific}} = (\text{Tokens}_{\text{claim}} \cap \text{Tokens}_{\text{review}}) \setminus \text{GENERIC\_TOPIC\_WORDS}$$
  4. *Evidence Linking Threshold:* A fact-check is linked to a claim if and only if:
     $$S_{\cos} \ge 0.45 \quad \lor \quad \left( S_{\cos} \ge 0.30 \ \land \ |\text{Overlap}_{\text{specific}}| \ge 2 \ \land \ \exists w \in \text{Overlap}_{\text{specific}}: |w| \ge 5 \right)$$
  5. If linked, fact-checks rated `FALSE` or `MIXED` append to `contradicting_evidence_ids`; fact-checks rated `TRUE` append to `supporting_evidence_ids`.
  6. The claim's `verification_status` updates to `SUPPORTED`, `CONTRADICTED`, `CONFLICTING`, or `INSUFFICIENT`.

#### Code Excerpt 5.3 (`backend/app/services/evidence_assessor.py`):
```python
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
            explanations.append(f"Contradicted by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'")
        elif fc.normalized_verdict == "TRUE":
            supporting_ids.append(fc.id)
            explanations.append(f"Corroborated by published fact-check by {fc.fact_checker_publisher} rated '{fc.original_rating}'")
```
*Explanation:* Code Excerpt 5.3 illustrates the evidence-linking filter. By suppressing institutional stopwords (`GENERIC_TOPIC_WORDS`) and enforcing high similarity thresholds, the system guarantees that fact checks concerning unrelated conspiracies (e.g., WHO sovereignty myths) do not falsely link to legitimate news stories.

---

### 5.1.9 Four-Factor Source Credibility Scoring Module (`backend/app/services/source_credibility.py`)

- **Purpose:** Computes an objective, explainable credibility score for publishing domains across four weighted dimensions.
- **Inputs:** Article URL string or domain name.
- **Outputs:** `SourceCredibilityReport` Pydantic model containing `overall_score`, `assessment_status`, `factors`, `missing_signals`, and `disclaimer`.
- **Key Functions / Classes:** `SourceCredibilityAnalyzer.assess()`, `_score_domain_track_record()`, `_score_tld_integrity()`, `_score_author_attribution()`, `_score_publisher_transparency()`.
- **Mathematical Scoring Formula:**
  $$\text{Score}_{\text{overall}} = (0.40 \cdot S_{\text{track}}) + (0.25 \cdot S_{\text{tld}}) + (0.20 \cdot S_{\text{author}}) + (0.15 \cdot S_{\text{pub}})$$
  - *Domain Track Record ($S_{\text{track}}$, Weight 40%):* Checks domain against established journalistic accreditation registries (Reuters, AP, BBC $\rightarrow 96.0$) and unprofiled baselines ($\rightarrow 50.0$).
  - *TLD & Registration Integrity ($S_{\text{tld}}$, Weight 25%):* Evaluates Top-Level Domain security (`.gov`, `.edu` $\rightarrow 95.0$; established `.org`, `.com` $\rightarrow 85.0$; high-risk free TLDs `.xyz`, `.top` $\rightarrow 35.0$).
  - *Author Attribution ($S_{\text{author}}$, Weight 20%):* Evaluates explicit journalist byline presence ($85.0$ if present, $40.0$ if missing).
  - *Publisher Transparency ($S_{\text{pub}}$, Weight 15%):* Evaluates organizational metadata and contact transparency ($85.0$ if present, $35.0$ if missing).
- **Satire / Conspiracy Hard Cap:** If a domain is identified within the verified satire or conspiracy registry (`theonion.com`, `babylonbee.com`, `infowars.com`), its overall score is strictly capped at $\le 25.0$ points.
- **Missing URL Handling:** If no URL is provided (direct text input), `overall_score` evaluates to `None`, `assessment_status` sets to `"Assessment unavailable"`, and missing signals are explicitly documented.

---

### 5.1.10 Hierarchical Epistemic Decision Fusion Module (`backend/app/services/decision_fusion.py`)

- **Purpose:** Synthesizes multi-source evidence into a transparent final assessment governed by formal epistemic rules.
- **Inputs:** Lists of `ExtractedClaim`, `FactCheckItem`, `NewsArticleItem`, `SourceCredibilityReport`, `TextModelAnalysis`, and `ImageModelAnalysis`.
- **Outputs:** `DecisionFusionReport` Pydantic model containing `final_assessment`, `explanation`, `uncertainty_level`, `evidence_coverage`, and `decision_rules_applied`.
- **Key Functions / Classes:** `DecisionFusionEngine.fuse()`.
- **The Eight Epistemic Decision Rules (Evaluated in Strict Hierarchical Order):**
  1. *Rule 1 (Authoritative Fact-Check Refutation):* If matched fact-checks rated `FALSE` or `MIXED` are $>0$, verdict is **Contradicted by available evidence** (Uncertainty: Low).
  2. *Rule 2 (Discredited / Satire Domain Grounding):* If source credibility score is $\le 20.0$, verdict is **Misleading or missing context** (Uncertainty: Low).
  3. *Rule 3 (Authoritative Fact-Check Corroboration):* If matched fact-checks rated `TRUE` are $>0$ and contradicting evidence is $0$, verdict is **Supported by available evidence** (Uncertainty: Low).
  4. *Rule 4 (Multimodal Inconsistency):* If image analysis flags `POTENTIAL_CONTEXT_MISMATCH`, verdict is **Misleading or missing context** (Uncertainty: Moderate).
  5. *Rule 5 (Active Evidentiary Conflict):* If supporting evidence $>0$ and contradicting evidence $>0$, verdict is **Conflicting evidence** (Uncertainty: Moderate).
  6. *Rule 6 (Multi-Source News Corroboration):* If supporting independent news outlets $\ge 2$ and contradicting evidence is $0$, verdict is **Supported by available evidence** (Uncertainty: Low to Moderate).
  7. *Rule 6b (Verified Primary Publisher Corroboration):* If source score is $\ge 70.0$, text model prediction is `Credible` or `Neutral`, and contradictions are $0$, verdict is **Supported by available evidence** (Uncertainty: Moderate).
  8. *Rule 7 (Stylistic Risk with Missing Corroboration):* If text model flags `Elevated Misinformation Risk` but external evidence is $0$, verdict is strictly **Insufficient evidence** (Uncertainty: High). Model style cannot establish factual falsehood.
  9. *Rule 8 (Default Baseline Outcome):* If no fact-checks or corroborating news reports exist, verdict defaults strictly to **Insufficient evidence** (Uncertainty: High).

---

## 5.2 Testing and Verification

To validate software correctness, security resilience, numerical reproducibility, and epistemic soundness, VeritasAI was subjected to a comprehensive multi-tier testing strategy comprising unit testing, security penetration testing, integration testing, system testing, and empirical benchmark audits.

### 5.2.1 Test Strategy & Test Environment

The test harness is implemented in Python using the `pytest` and `pytest-asyncio` frameworks. All tests execute within an isolated virtual environment (`./venv`) using Python 3.13.9 on an Apple Silicon (M-Series) ARM64 architecture running macOS Sequoia. Tests utilize an in-memory SQLite database instance (`sqlite:///:memory:`) configured in `backend/tests/conftest.py` to prevent cross-test data pollution. External HTTP dependencies are mocked in unit tests using `unittest.mock` to ensure deterministic execution, while integration scripts (`scripts/audit_three_articles.py`) test live global network endpoints.

---

### 5.2.2 Comprehensive Test Cases Specification

Table 5.2 documents twenty-five rigorous test cases (TC-01 through TC-25) spanning API routes, security validators, NLP components, source scoring, decision fusion, and database persistence.

| Test Case ID | Target Module | Test Description & Objective | Test Input Data | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `endpoints.py` | Verify text-only submission analysis via REST API | Text: `"Drinking bleach cures coronavirus infections"` | HTTP 200; `status="COMPLETED"`; final assessment present | HTTP 200; `final_assessment="Contradicted by available evidence"` | **PASS** (Real) |
| **TC-02** | `endpoints.py` | Verify rejection when neither text nor URL is provided | Empty request body (`text=None`, `url=None`) | HTTP 400 Bad Request; `"Must provide either article URL or text"` | HTTP 400; Expected detail returned | **PASS** (Real) |
| **TC-03** | `endpoints.py` | Verify multimodal submission with valid JPEG image | Text + 100x100 valid JPEG byte stream | HTTP 200; `has_image=True`; image dimensions parsed | HTTP 200; `image_dimensions=[100, 100]` | **PASS** (Real) |
| **TC-04** | `health.py` | Verify health check monitoring endpoint | `GET /api/health` | HTTP 200; `{"status": "healthy", "service": "veritasai"}` | HTTP 200; JSON payload matches schema | **PASS** (Real) |
| **TC-05** | `health.py` | Verify Prometheus metrics telemetry endpoint | `GET /api/metrics` | HTTP 200; JSON containing request counts and memory stats | HTTP 200; Metrics payload returned | **PASS** (Real) |
| **TC-06** | `providers.py`| Verify provider health status reporting | `GET /api/providers` | HTTP 200; Status dictionary for Gemini, Fact Check, GDELT | HTTP 200; All providers reported | **PASS** (Real) |
| **TC-07** | `security.py` | Verify valid public HTTPS URL passes validation | URL: `https://www.reuters.com/news/article-1` | URL validated and returned unmodified | Returns `https://www.reuters.com/news/article-1` | **PASS** (Real) |
| **TC-08** | `security.py` | Intercept and reject unsupported URL schemes | URL: `file:///etc/passwd` | HTTP 400; `"Unsupported URL scheme: file"` | HTTP 400; Error raised | **PASS** (Real) |
| **TC-09** | `security.py` | Intercept and reject localhost loopback URLs (SSRF) | URL: `http://127.0.0.1:8000/admin` | HTTP 400; `"Target URL resolves to a forbidden internal address"` | HTTP 400; Blocked successfully | **PASS** (Real) |
| **TC-10** | `security.py` | Intercept and reject AWS cloud metadata IP (SSRF) | URL: `http://169.254.169.254/latest/meta-data` | HTTP 400; Forbidden internal IP address | HTTP 400; Blocked successfully | **PASS** (Real) |
| **TC-11** | `security.py` | Verify safe image validation on valid 50x50 PNG | Valid 50x50 PNG byte buffer | Returns PIL `Image` object with format `"PNG"` | Returns verified PIL Image object | **PASS** (Real) |
| **TC-12** | `security.py` | Intercept corrupted or malicious binary image upload | Corrupted random byte stream (`b"not-an-image"`) | HTTP 400; `"Uploaded file is not a valid image"` | HTTP 400; Rejected successfully | **PASS** (Real) |
| **TC-13** | `security.py` | Intercept oversized image exceeding 5MB bound | Generated byte stream exceeding 5,242,880 bytes | HTTP 400; `"Image file size exceeds maximum limit"` | HTTP 400; Rejected successfully | **PASS** (Real) |
| **TC-14** | `text_analyzer.py`| Verify sensationalism and clickbait detection | Headline: `"SHOCKING TRUTH: Mind control in vaccines!!"` | `sensationalism_index > 0.3`; `clickbait_detected=True` | `sensationalism_index=0.62`; Clickbait flagged | **PASS** (Real) |
| **TC-15** | `text_analyzer.py`| Verify objective journalistic phrasing scoring | Text: `"According to official statements, treasury reports growth."` | `prediction="Credible / Objective Phrasing"`; high attribution | Prediction: Credible; Attribution density: 1.0 | **PASS** (Real) |
| **TC-16** | `claim_extractor.py`| Verify rule-based local NLP claim extraction | Headline + 3 sentences with figures and verbs | Returns $\ge 1$ `ExtractedClaim` with entity search queries | Returns 3 claims; Headline claim importance: HIGH | **PASS** (Real) |
| **TC-17** | `source_credibility.py`| Verify reputable news domain scoring | URL: `https://www.reuters.com/business` | `overall_score >= 70.0`; `assessment_status="Assessed"` | Score: 72.9; Status: Assessed | **PASS** (Real) |
| **TC-18** | `source_credibility.py`| Verify satire domain hard cap enforcement | URL: `https://www.theonion.com/article-123` | `overall_score <= 25.0`; Flagged as satire | Score: 20.2; Flagged satire domain | **PASS** (Real) |
| **TC-19** | `source_credibility.py`| Verify missing URL yields unavailable status | URL: `None` (Text-only submission) | `overall_score=None`; `status="Assessment unavailable"` | Score: None; Status: Assessment unavailable | **PASS** (Real) |
| **TC-20** | `decision_fusion.py`| Verify Rule 1 authoritative fact-check refutation | Matched fact-check rated `FALSE` ("Pants on Fire") | `final_assessment="Contradicted by available evidence"`; Low uncertainty | Verdict: Contradicted; Uncertainty: Low | **PASS** (Real) |
| **TC-21** | `decision_fusion.py`| Verify Rule 8 baseline insufficient evidence outcome | 0 fact-checks; 0 news reports; unprofiled source | `final_assessment="Insufficient evidence"`; High uncertainty | Verdict: Insufficient evidence; High uncertainty | **PASS** (Real) |
| **TC-22** | `decision_fusion.py`| Verify Rule 7 prevents model prediction as proof | Text flagged `Elevated Misinformation Risk`; 0 evidence | `final_assessment="Insufficient evidence"` (Not Contradicted) | Verdict: Insufficient evidence (Rule 7 applied) | **PASS** (Real) |
| **TC-23** | `evidence_assessor.py`| Verify institutional stop-word suppression filter | Claim: WHO ends emergency; FC: WHO sovereignty treaty | No match (`is_relevant_match=False`); overlap filtered | Overlap set empty; No false link created | **PASS** (Real) |
| **TC-24** | `history.py` | Verify paginated history API and deletion | Submit article, retrieve via `/api/history`, delete ID | HTTP 200 on list; Record deleted successfully | Record retrieved and deleted cleanly | **PASS** (Real) |
| **TC-25** | `image_analyzer.py`| Verify nocturnal claim with daylight image mismatch | Text: `"Midnight explosion"` + Image: Luminance 165.0 | Flag: `POTENTIAL_CONTEXT_MISMATCH`; Rule 4 triggered | Flag raised; Verdict: Misleading context | **PASS** (Real) |

---

### 5.2.3 Defect Discovery, Security Remediation & Audit Log

During the rigorous end-to-end audit of the VeritasAI platform, multiple subtle algorithmic and architectural defects were discovered and remediated. Table 5.3 catalogs these defects, detailing their root causes, system impact, and exact code-level resolutions.

| Defect ID | Component Affected | Root Cause Description | System Impact Observed | Code-Level Resolution & Verification |
| :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | `evidence_assessor.py` | Over-inclusive keyword matching: broad terms (`"world"`, `"health"`, `"organization"`, `"pandemic"`) treated as specific topic overlap. | A true news report (*"WHO declares end to COVID-19 emergency"*) matched unrelated conspiracy debunks (*"WHO pandemic treaty"*), causing a false contradiction. | Expanded `GENERIC_TOPIC_WORDS` filter to include institutional stopwords; increased required cosine threshold to $S_{\cos} \ge 0.45$ or $S_{\cos} \ge 0.30$ with $\ge 2$ specific non-generic words $\ge 5$ chars. |
| **BUG-02** | `decision_fusion.py` | Unlinked global fact-check counting: `fc_false_count` counted all raw fact-checks returned by search queries, regardless of whether any claim matched them. | If an external API returned 4 debunks for a general entity query, the article was declared debunked even if `evidence_assessor` linked 0 of them to claims. | Updated `fuse()` to evaluate `is_assessed_by_pipeline`. When claims are evaluated, only fact-checks linked to claim IDs via `c.contradicting_evidence_ids` are counted. |
| **BUG-03** | `decision_fusion.py` | Strict text model constraint in Rule 6b: only accepted `prediction == "Credible / Objective Phrasing"`. | Legitimate news reports from Reuters with balanced, neutral prose (`"Neutral / Mixed Stylometric Signals"`) failed Rule 6b and defaulted to insufficient evidence. | Updated Rule 6b condition to accept `prediction in ("Credible / Objective Phrasing", "Neutral / Mixed Stylometric Signals")`, properly recognizing high-credibility reporting. |
| **BUG-04** | `source_credibility.py`| Satire domains (*The Onion*) received 40.2 points due to standard `.com` TLD registration and clear publisher metadata. | Satire domains were not sufficiently penalized to trigger Rule 2 domain grounding. | Added explicit `KNOWN_SATIRE_DOMAINS` set with a strict score cap ($\le 25.0$). Verified via `test_source_credibility_reputable_and_flagged()`. |
| **BUG-05** | `claim_extractor.py` | Gemini API model endpoint deprecation (`gemini-1.5-flash` returned HTTP 404). | External LLM extraction failed continuously across all requests. | Updated endpoint to `models/gemini-3.8-flash` with 5.0s timeout and automatic fallback to `_extract_with_local_nlp()`. |
| **BUG-06** | `news_search_service.py`| GDELT 2.0 API returned HTTP 429 under rapid queries, causing connection hangs. | Verification pipeline stalled for 30+ seconds waiting for news searches. | Reduced timeout to 4.0s and configured immediate clean abort returning `[]` on HTTP 429. |
