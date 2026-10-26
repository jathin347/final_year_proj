# VeritasAI System Architecture

## 1. High-Level Architecture Overview

VeritasAI is an investigative decision-support platform designed for real-time fake news verification, factual claim extraction, source credibility scoring, and multimodal consistency checking.

The platform follows a layered pipeline where **AI linguistic classification is strictly decoupled from external evidence verification**.

```
                           USER INPUT
        (News URL, Headline, Full Text, Optional Image)
                              │
                              ▼
                INPUT VALIDATION & SECURITY (SSRF)
            (Scheme check, DNS resolution, private IP block,
               image decompression bounds & MIME filter)
                              │
                              ▼
                ARTICLE EXTRACTION & METADATA
            (OpenGraph, Twitter Cards, Schema.org, Byline,
             canonical domain, publication date, main text)
                              │
                              ▼
              TEXT PROCESSING & CLAIM EXTRACTION
      (Google Gemini API structured extraction or local NLP fallback:
       named entities, dates, quantitative assertions, search queries)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
       AI TEXT STYLOMETRICS           MULTIMODAL IMAGE ANALYSIS
   (Sensationalism, clickbait,     (PIL / PyTorch safe decoding,
    attribution density, TF-IDF     brightness, contrast, scene
     logistic calibrated model)     consistency, timing mismatch)
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                   EXTERNAL EVIDENCE SEARCH
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
   LIVE FACT-CHECK SEARCH            LIVE NEWS SEARCH
 (Google Fact Check Tools API)      (GDELT 2.0 Global News API)
 (ClaimReview schema, verbatim      (Cross-publisher deduplication,
  ratings, publication dates)        reporting stance, syndication)
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                   CLAIM-EVIDENCE MATCHING
     (Cosine similarity, lexical alignment, stance categorization:
      Supporting, Contradicting, Contextual, Neutral/Inconclusive)
                              │
                              ▼
                 SOURCE CREDIBILITY SCORING
     (Domain track record 40%, TLD integrity 25%, byline 20%,
      publisher transparency 15%, explicit missing indicators)
                              │
                              ▼
                  TRANSPARENT DECISION FUSION
    (Hierarchical decision rules: Fact-check debunks > Satire source
     > Fact-check confirmation > Multimodal discrepancy > News coverage
     > Missing evidence abstention. Never converts model score to fact)
                              │
                              ▼
                 EXPLANATION & AUDIT PERSISTENCE
     (Uncertainty rating, attribution tokens, latency breakdown ms,
       SQLite persistence via SQLAlchemy, paginated history API)
                              │
                              ▼
                   VERIFICATION DASHBOARD
   (React + TypeScript + Tailwind CSS with live progress indicators,
       evidence cards, source score gauge, and interactive history)
```

## 2. Core Components

### 2.1 Backend (`backend/app`)
- **FastAPI Core**: Asynchronous REST API with OpenAPI v3 auto-documentation (`/docs`), strict Pydantic schemas, and custom CORS middleware.
- **Security & SSRF Guard (`app/core/security.py`)**: Validates URLs, enforces `http/https`, performs DNS lookups to block private IP spaces (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, `::1`), and validates image files.
- **Article Extractor (`app/services/article_extractor.py`)**: Extracts headline, byline, publication date, domain, and body text using BeautifulSoup4.
- **Text Stylometrics (`app/services/text_analyzer.py`)**: Extracts punctuation density, all-caps ratios, clickbait regex patterns, journalistic attribution markers, and calibrated sigmoid probability with token-level feature attribution.
- **Multimodal Validator (`app/services/image_analyzer.py`)**: Safe image decoding, visual statistics (brightness, contrast), and contextual consistency with text claims.
- **Claim Extractor (`app/services/claim_extractor.py`)**: Generates structured `ExtractedClaim` models via Gemini API or rule-based NLP fallback.
- **Google Fact Check Client (`app/services/fact_check_service.py`)**: Searches ClaimReview database; preserves verbatim ratings.
- **GDELT News Search (`app/services/news_search_service.py`)**: Free REST queries against GDELT 2.0 DOC API with title similarity deduplication.
- **Evidence Assessor (`app/services/evidence_assessor.py`)**: Matches claims against evidence items and categorizes stances.
- **Source Credibility Engine (`app/services/source_credibility.py`)**: Weighted heuristic assessment (0–100) based on observed signals.
- **Decision Fusion (`app/services/decision_fusion.py`)**: Epistemic decision hierarchy grounding final verdicts on external evidence.
- **Persistence (`app/repositories/analysis_repository.py`)**: SQLAlchemy models storing verification records, claims, evidence, and latency metrics in SQLite.

### 2.2 Frontend (`frontend/src`)
- **React 18 + Vite + TypeScript**: Fast single-page application with modular architecture.
- **Tailwind CSS**: Dark slate aesthetic (`slate-950`), custom verdict palettes, and high-contrast typography.
- **Pages**:
  - `DashboardPage`: Input forms, test presets, live multi-stage progress tracker, and recent runs table.
  - `ReportPage`: Detailed verification view with verdict cards, claim breakdowns, evidence cards with source links, source score gauge, model attributions, and latency bar.
  - `HistoryPage`: Paginated historical runs with search, drill-down, and record deletion.
  - `MethodologyPage`: Comprehensive documentation of the system's architecture, formulas, and limitations.

### 2.3 Storage Layer
- **SQLite Database (`fake_news.db`)**: Lightweight, self-contained relational database managed via SQLAlchemy. Stores analysis records, structured claims JSON, retrieved evidence JSON, and latency profiles.
