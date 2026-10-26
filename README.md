# VeritasAI: AI-Powered Real-Time Fake News Detector with Source Credibility Scoring and Multimodal Verification

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen)
![React: 18](https://img.shields.io/badge/React-18-cyan)
![FastAPI: 0.115+](https://img.shields.io/badge/FastAPI-0.115%2B-teal)
![Vite: 5](https://img.shields.io/badge/Vite-5-purple)
![Tests: 17 Passed](https://img.shields.io/badge/Tests-17%20Passed-emerald)

VeritasAI is an investigative decision-support platform designed to analyze news articles and factual claims. Rather than relying on a simplistic black-box binary classifier, VeritasAI unites AI linguistic modeling with live external evidence retrieval, professional fact-check database queries, transparent source credibility assessment, multimodal scene verification, and an epistemic decision fusion engine that abstains from guessing when evidence is absent.

---

## Key Features

1. **Multi-Input Ingestion with SSRF Protection**
   - Supports news URLs, headlines, full article bodies, and optional image uploads.
   - Robust SSRF guardrails validating DNS resolutions against private (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), loopback (`127.0.0.0/8`), and cloud metadata (`169.254.169.254`) ranges.

2. **Factual Claim Extraction Engine**
   - Extracts discrete, testable factual assertions with Pydantic schema validation.
   - Dual-engine architecture: Google Gemini API structured extraction when configured, and a resilient internal rule-based NLP extractor when operating offline.

3. **AI Text Stylometrics & Token Feature Attribution**
   - Calculates sensationalism indices, all-caps word density, clickbait phrasing, and journalistic attribution density.
   - Logistic calibrated model with unigram/bigram feature extraction.
   - Transparently highlights risk and credibility tokens.

4. **Multimodal Scene Verification**
   - Safe image decoding with decompression bomb protection ($6000 \times 6000$ bound) and MIME validation.
   - Extracts visual attributes (brightness, contrast) and evaluates contextual consistency with textual claims (detecting day/night discrepancies).

5. **Live Fact-Check & Global News Retrieval**
   - **Google Fact Check Tools API:** Directly queries verified schema.org `ClaimReview` records; preserves original publisher ratings verbatim (`Pants on Fire`, `False`, `Mostly True`).
   - **GDELT 2.0 DOC API:** Live global news search with pairwise title cosine similarity deduplication to filter syndicated reprints.

6. **Transparent Source Credibility Scoring (0–100)**
   - Factor-weighted heuristic: Domain track record (40%), TLD & domain integrity (25%), author byline (20%), publisher transparency (15%).
   - Explicitly notes missing signals; caps satirical and flagged conspiracy domains at low credibility scores.

7. **Epistemic Decision Fusion Hierarchy**
   - Strictly grounds verdicts in external evidence rather than arbitrary probability weights.
   - Output categories:
     - `Supported by available evidence`
     - `Contradicted by available evidence`
     - `Misleading or missing context`
     - `Conflicting evidence`
     - `Insufficient evidence`
     - `Analysis unavailable`
   - **Responsible Abstention:** Returns `Insufficient evidence` when no authoritative fact-checks or news records exist (0.0% unsupported verdict rate).

8. **Audit Persistence & Operational Metrics**
   - Stores verification runs, extracted claims, evidence references, and per-module latency breakdowns (ms) in SQLite via SQLAlchemy.
   - Paginated history browsing and one-click deletion.

---

## Architecture Diagram

```
[ User Input (URL / Headline / Text / Image) ]
                      │
                      ▼
[ Input Validation & SSRF Defense (ipaddress, socket) ]
                      │
                      ▼
[ Article Extractor & Metadata Parser (BeautifulSoup4) ]
                      │
                      ▼
[ Claim Extraction Engine (Gemini LLM / Rule-Based NLP) ]
          │                                   │
          ▼                                   ▼
[ Text Stylometrics ]               [ Multimodal Image Analysis ]
          │                                   │
          └─────────────────┬─────────────────┘
                            │
                            ▼
[ External Evidence Retrieval (Google Fact Check + GDELT News) ]
                            │
                            ▼
[ Claim-Evidence Matching & Stance Categorization ]
                            │
                            ▼
[ Transparent Source Credibility Scoring (0–100) ]
                            │
                            ▼
[ Epistemic Decision Fusion (Hierarchical Rules) ]
                            │
                            ▼
[ Verification Dashboard (React + Vite + Tailwind CSS) ]
```

---

## Technology Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SQLite, HTTPX, BeautifulSoup4, Pillow, Scikit-learn, PyTorch, TorchVision.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts.
- **Testing:** Pytest, Pytest-Asyncio.
- **Data & Models:** Joblib, TF-IDF Vectorizer, Calibrated Logistic Regression.

---

## Directory Structure

```
final_year_proj/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── analyze.py       # Core orchestration endpoint (/api/analyze)
│   │   │   │   ├── claims.py        # Claim extraction & search endpoints
│   │   │   │   ├── health.py        # /api/health and /api/metrics
│   │   │   │   ├── history.py       # Paginated history CRUD
│   │   │   │   └── providers.py     # Safe configuration status
│   │   │   └── schemas/             # Pydantic schemas (analysis, claims, evidence)
│   │   ├── core/
│   │   │   ├── config.py            # Environment settings
│   │   │   ├── logging.py           # Sanitized logger
│   │   │   └── security.py          # SSRF prevention & image validation
│   │   ├── models/
│   │   │   ├── database.py          # SQLAlchemy engine & session factory
│   │   │   └── entities.py          # AnalysisRecord entity
│   │   ├── repositories/
│   │   │   └── analysis_repository.py
│   │   ├── services/
│   │   │   ├── article_extractor.py # Safe article ingestion
│   │   │   ├── claim_extractor.py   # Gemini & NLP claim extraction
│   │   │   ├── decision_fusion.py   # Epistemic fusion engine
│   │   │   ├── evidence_assessor.py # Stance matching
│   │   │   ├── explanation_service.py
│   │   │   ├── fact_check_service.py# Google Fact Check API client
│   │   │   ├── image_analyzer.py    # Multimodal image consistency
│   │   │   ├── news_search_service.py# GDELT 2.0 API client
│   │   │   ├── source_credibility.py# 0-100 heuristic scoring
│   │   │   └── text_analyzer.py     # Stylometric model
│   │   ├── utils/
│   │   │   ├── text_processing.py
│   │   │   └── url_validation.py
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── tests/                       # 17 automated unit and integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.ts            # Typed API client
│   │   ├── components/              # Navbar, ProviderStatusBar, ProgressIndicator
│   │   ├── pages/                   # DashboardPage, ReportPage, HistoryPage, MethodologyPage
│   │   ├── types/index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── datasets/
│   ├── README.md
│   └── benchmark_evaluation.json    # Gold-standard evaluation benchmark
├── models/
│   ├── README.md
│   └── stylistic_classifier.joblib  # Trained model artifact
├── scripts/
│   ├── train.py                     # Classifier training & calibration
│   └── evaluate.py                  # Pipeline evaluation & metrics
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── api_integrations.md
│   ├── evaluation_plan.md
│   ├── security.md
│   └── feature_status.md
├── .env.example
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Navigate to project root
cd /path/to/final_year_proj

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build to verify bundle
npm run build
```

---

## Running the Application

### Start the Backend (Port 8000)
```bash
source venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

### Start the Frontend (Port 5173)
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
Access the application in your browser at: `http://127.0.0.1:5173/`

---

## Running Automated Tests

Run the complete test suite (all 17 unit and integration tests):
```bash
source venv/bin/activate
PYTHONPATH=. pytest backend/tests/ -v
```

---

## Reproducing Model Training & Evaluation

### Train & Calibrate Stylistic Classifier:
```bash
source venv/bin/activate
python scripts/train.py
```
*Output: 90.0% Held-Out Test Accuracy, 0.9091 F1 Score.*

### Run Pipeline Grounding & Abstention Benchmark:
```bash
source venv/bin/activate
python scripts/evaluate.py
```
*Output: 0.0% Unsupported Verdict Rate (abstained on 100% of claims with missing evidence).*

---

## Environment Configuration

Configure external API keys in `.env` (optional):
```ini
# Google Gemini API key (optional for enhanced claim extraction)
GEMINI_API_KEY=

# Google Fact Check Tools API key (optional for live ClaimReview search)
GOOGLE_FACT_CHECK_API_KEY=

# Database URL
DATABASE_URL=sqlite:///./fake_news.db

# Server settings
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
LOG_LEVEL=INFO
```

---

## Limitations

1. **On-Demand Scope**: The application is an on-demand verification tool, not a continuous web-crawling surveillance monitor.
2. **Absence of Proof**: Unreported local events return `Insufficient evidence` rather than forced binary verdicts.
3. **Multimodal Boundaries**: Vision checks evaluate scene consistency; deepfake forensic detection requires dedicated cryptographic provenance models.
