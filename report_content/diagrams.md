# VERITASAI – CONSOLIDATED MERMAID DIAGRAM SOURCE CODE

This document aggregates the complete, valid Mermaid diagram source code for all eleven architectural, data flow, sequence, and entity-relationship figures created for the B.Tech Project-I report. These code snippets can be copied directly into Mermaid Live Editor (`mermaid.live`), GitHub Markdown, or documentation build tools to render high-resolution PNG/SVG vector diagrams.

---

## Figure 4.1: VeritasAI Multi-Tier Pipeline Architecture Diagram

```mermaid
graph TD
    subgraph Presentation_Layer [Presentation Layer - React 18 / Vite / Tailwind]
        UI[Web Dashboard & Ingestion Form]
        Viz[Visualization Gauges & Recharts]
        HistoryUI[Audit History Table]
    end

    subgraph Gateway_Security [API Gateway & Ingestion Security Layer]
        API[FastAPI Router - /api/analyze]
        SSRF[SSRF Validator - DNS IP Check]
        ImgSec[Pillow Image Bounds Validator]
    end

    subgraph Service_Orchestration [Core Analytical Service Layer]
        Parser[Article & Metadata Extractor]
        
        subgraph Claim_Engine [Claim Decomposition Engine]
            Gemini[Primary: Google Gemini 3.8 Flash LLM]
            LocalNLP[Fallback: Rule-Based Local NLP]
        end

        subgraph Evidence_Retrieval [Concurrent External Evidence Retrieval]
            FactCheckAPI[Google Fact Check Tools API]
            GDELTAPI[GDELT 2.0 Global Document API]
        end

        subgraph Independent_Analyses [Parallel Signal Analyzers]
            TextML[TF-IDF + Logistic Regression Stylometrics]
            SrcScorer[4-Factor Source Credibility Engine]
            ImgAnalyzer[Multimodal Image Context Inspector]
        end

        Linker[Evidence Assessor - Cosine Match & Stopword Suppression]
        Fusion[Epistemic Decision Fusion Engine - Rules 1 to 8]
        Explain[Audit Narrative & Explanation Generator]
    end

    subgraph Storage_Layer [Persistence & Telemetry Layer]
        ORM[SQLAlchemy Repository]
        DB[(SQLite - fake_news.db)]
    end

    UI -->|URL / Text / Image| API
    API --> SSRF
    API --> ImgSec
    SSRF -->|Safe URL| Parser
    Parser --> Claim_Engine
    ImgSec --> ImgAnalyzer
    
    Parser --> TextML
    Parser --> SrcScorer
    
    Claim_Engine --> Gemini
    Gemini -.->|On 503 / 429 / Timeout| LocalNLP
    
    Claim_Engine -->|Claim Queries| Evidence_Retrieval
    
    Evidence_Retrieval --> FactCheckAPI
    Evidence_Retrieval --> GDELTAPI
    
    FactCheckAPI --> Linker
    GDELTAPI --> Linker
    Claim_Engine --> Linker
    
    Linker --> Fusion
    TextML --> Fusion
    SrcScorer --> Fusion
    ImgAnalyzer --> Fusion
    
    Fusion --> Explain
    Explain --> ORM
    ORM --> DB
    Explain -->|JSON Response| UI
    DB --> HistoryUI
```

---

## Figure 4.2: Data Flow Diagram Level 0 (Context Diagram)

```mermaid
graph LR
    User((User / Journalist))
    ExtWeb[(External Websites)]
    FactCheckSys[(Google Fact Check API)]
    GDELTSys[(GDELT News API)]
    GeminiSys[(Google Gemini API)]

    System[0.0 VeritasAI Fake News Verification System]

    User -->|Submit URL / Text / Image| System
    System -->|Fetch Article HTML| ExtWeb
    ExtWeb -->|Return Webpage Data| System

    System -->|Prompt Claim Decomposition| GeminiSys
    GeminiSys -->|Return Extracted Claims JSON| System

    System -->|Query Verified Claims| FactCheckSys
    FactCheckSys -->|Return ClaimReview Schemas| System

    System -->|Query Global News Articles| GDELTSys
    GDELTSys -->|Return News Metadata| System

    System -->|Deliver Verification Report & Visual Evidence| User
```

---

## Figure 4.3: Data Flow Diagram Level 1 (Pipeline Decomposition)

```mermaid
graph TD
    User((User))
    D1[(SQLite Database)]
    ExtFact[(Fact Check API)]
    ExtNews[(GDELT API)]
    ExtLLM[(Gemini API)]
    ExtWeb[(Target Website)]

    User -->|Input Form| P1[1.0 Ingest & Validate Input]
    P1 -->|Validated URL| P2[2.0 Extract Article & Metadata]
    P1 -->|Direct Text| P3[3.0 Extract Factual Claims]
    P1 -->|Image Binary| P4[4.0 Perform Image Analysis]

    P2 -->|HTTP Request| ExtWeb
    ExtWeb -->|Raw HTML| P2
    P2 -->|Article Prose| P3
    P2 -->|Domain Name| P5[5.0 Assess Source Credibility]
    P2 -->|Article Prose| P6[6.0 Analyze Text Stylometrics]

    P3 -->|JSON Prompt| ExtLLM
    ExtLLM -->|Claim List| P3
    P3 -->|Claim Queries| P7[7.0 Retrieve External Evidence]

    P7 -->|Claim Query| ExtFact
    ExtFact -->|ClaimReviews| P7
    P7 -->|Topic Query| ExtNews
    ExtNews -->|Articles| P7

    P7 -->|Evidence Items| P8[8.0 Assess & Link Evidence]
    P3 -->|Atomic Claims| P8

    P8 -->|Linked Claims & Evidence| P9[9.0 Execute Decision Fusion]
    P4 -->|Visual Discrepancies| P9
    P5 -->|Source Score & Factors| P9
    P6 -->|Stylometric Prediction| P9

    P9 -->|Synthesized Report| P10[10.0 Persist & Render Report]
    P10 -->|Save Record| D1
    P10 -->|Display Dashboard| User
```

---

## Figure 4.4: Data Flow Diagram Level 2 (Evidence Retrieval & Fusion Subsystem)

```mermaid
graph TD
    Claims[Extracted Claims List]
    FactAPI[(Google Fact Check API)]
    NewsAPI[(GDELT News API)]

    subgraph Process_7_Detail [7.0 Evidence Retrieval Subsystem]
        P7_1[7.1 Generate Optimized Search Queries]
        P7_2[7.2 Query Fact Check API Asynchronously]
        P7_3[7.3 Query GDELT News API Asynchronously]
        P7_4[7.4 Deduplicate & Normalize Fact-Check Ratings]
        P7_5[7.5 Filter Syndicated News Duplicates]
    end

    subgraph Process_8_Detail [8.0 Evidence Linking Subsystem]
        P8_1[8.1 Tokenize Claim & Review Texts]
        P8_2[8.2 Suppress Generic Topic Stopwords]
        P8_3[8.3 Compute Cosine Similarity Matrix]
        P8_4[8.4 Enforce Non-Generic Overlap Threshold]
        P8_5[8.5 Assign Supporting / Contradicting IDs]
    end

    subgraph Process_9_Detail [9.0 Decision Fusion Engine]
        P9_1[9.1 Check Rule 1: Authoritative Refutations]
        P9_2[9.2 Check Rule 2: Discredited Domain Grounding]
        P9_3[9.3 Check Rule 3: Fact-Check Corroborations]
        P9_4[9.4 Check Rule 4: Multimodal Inconsistency]
        P9_5[9.5 Check Rule 5: Conflicting Evidence]
        P9_6[9.6 Check Rule 6: Multi-Source News Corroboration]
        P9_7[9.7 Check Rule 6b: Accredited Source Corroboration]
        P9_8[9.8 Check Rule 7: Stylistic Alert Default]
        P9_9[9.9 Check Rule 8: Baseline Insufficient Evidence]
    end

    Claims --> P7_1
    P7_1 --> P7_2
    P7_1 --> P7_3
    P7_2 <--> FactAPI
    P7_3 <--> NewsAPI
    P7_2 --> P7_4
    P7_3 --> P7_5

    P7_4 --> P8_1
    P7_5 --> P8_1
    Claims --> P8_1
    P8_1 --> P8_2
    P8_2 --> P8_3
    P8_3 --> P8_4
    P8_4 --> P8_5

    P8_5 --> P9_1
    P9_1 -->|No Refutations| P9_2
    P9_2 -->|Not Satire| P9_3
    P9_3 -->|No True FC| P9_4
    P9_4 -->|No Visual Mismatch| P9_5
    P9_5 -->|No Conflict| P9_6
    P9_6 -->|No Multi-News| P9_7
    P9_7 -->|Not High Cred Publisher| P9_8
    P9_8 -->|No Stylistic Risk| P9_9
```

---

## Figure 4.5: System Use Case Diagram

```mermaid
graph LR
    User((Journalist / User))
    Admin((System Auditor))
    FactCheckActor((Google Fact Check API))
    GeminiActor((Google Gemini LLM))
    GDELTActor((GDELT 2.0 API))

    subgraph VeritasAI_Platform [VeritasAI Platform Boundary]
        UC1[Submit Article URL for Verification]
        UC2[Submit Raw News Text / Claim]
        UC3[Upload Paired Article Image]
        UC4[View Claim-by-Claim Evidence Breakdown]
        UC5[Inspect Source Credibility Breakdown]
        UC6[View Execution Latency Profile]
        UC7[Browse & Filter Verification History]
        UC8[Delete Past Verification Record]
        UC9[Inspect Provider Health & Service Status]
        UC10[Decompose Factual Claims]
        UC11[Retrieve External Fact-Checks]
        UC12[Query Global News Coverage]
        UC13[Synthesize Epistemic Verdict]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8

    Admin --> UC7
    Admin --> UC8
    Admin --> UC9

    UC1 ..> UC10 : <<include>>
    UC2 ..> UC10 : <<include>>
    UC10 <--> GeminiActor
    
    UC1 ..> UC11 : <<include>>
    UC11 <--> FactCheckActor

    UC1 ..> UC12 : <<include>>
    UC12 <--> GDELTActor

    UC1 ..> UC13 : <<include>>
    UC13 ..> UC4 : <<manifests>>
```

---

## Figure 4.6: Unified Backend & Frontend Class Diagram

```mermaid
classDiagram
    class AnalysisRecord {
        +String id
        +String article_url
        +String headline
        +String article_summary
        +String publisher
        +String domain
        +String final_assessment
        +String assessment_explanation
        +String uncertainty_level
        +Float source_credibility_score
        +Float text_model_confidence
        +List extracted_claims
        +List fact_check_results
        +List news_search_results
        +Dict latency_breakdown_ms
        +Float total_latency_ms
        +DateTime created_at
    }

    class VerificationPipelineService {
        -ArticleExtractor article_extractor
        -ClaimExtractor claim_extractor
        -TextAnalyzer text_analyzer
        -ImageAnalyzer image_analyzer
        -GoogleFactCheckService fact_check_service
        -GDELTNewsSearchService news_search_service
        -EvidenceAssessor evidence_assessor
        -SourceCredibilityAnalyzer source_analyzer
        -DecisionFusionEngine fusion_engine
        -ExplanationService explanation_service
        -AnalysisRepository repository
        +verify_submission(request, image_file) VerificationReport
    }

    class ClaimExtractor {
        +extract_claims(text, headline) List~ExtractedClaim~
        -_extract_with_gemini(text, headline) List~ExtractedClaim~
        -_extract_with_local_nlp(text, headline) List~ExtractedClaim~
        -_build_search_query(text, entities) String
    }

    class EvidenceAssessor {
        +GENERIC_TOPIC_WORDS Set~String~
        +assess_and_link_evidence(claims, fact_checks, news) List~ExtractedClaim~
        -_calculate_cosine_similarity(text_a, text_b) Float
    }

    class DecisionFusionEngine {
        +fuse(claims, fact_checks, news, source, text, image) DecisionFusionReport
        -_quantify_matched_evidence(claims, fact_checks) Tuple
    }

    class SourceCredibilityAnalyzer {
        -KNOWN_SATIRE_DOMAINS Set~String~
        -REPUTABLE_DOMAINS Set~String~
        +assess(url) SourceCredibilityReport
        -_score_domain_track_record(domain) FactorScore
        -_score_tld_integrity(domain) FactorScore
        -_score_author_attribution(author) FactorScore
        -_score_publisher_transparency(publisher) FactorScore
    }

    class TextAnalyzer {
        -Pipeline model
        +analyze(headline, text) TextModelAnalysis
        -_compute_sensationalism_index(text) Float
        -_compute_attribution_density(text) Float
    }

    class ImageAnalyzer {
        +analyze_image(image_bytes) ImageModelAnalysis
        -_inspect_exif_metadata(pil_img) Dict
        -_compute_luminance_and_color(pil_img) Dict
    }

    class ExtractedClaim {
        +String claim_id
        +String claim_text
        +String importance
        +String category
        +List named_entities
        +List search_queries
        +String verification_status
        +List supporting_evidence_ids
        +List contradicting_evidence_ids
        +String explanation
    }

    VerificationPipelineService --> ClaimExtractor
    VerificationPipelineService --> EvidenceAssessor
    VerificationPipelineService --> DecisionFusionEngine
    VerificationPipelineService --> SourceCredibilityAnalyzer
    VerificationPipelineService --> TextAnalyzer
    VerificationPipelineService --> ImageAnalyzer
    VerificationPipelineService --> AnalysisRecord : persists via ORM
    EvidenceAssessor ..> ExtractedClaim : updates status & linkages
    DecisionFusionEngine ..> ExtractedClaim : reads matched IDs
```

---

## Figure 4.7: Sequence Diagram — Primary Live Fact-Checking Verification Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Client
    participant API as FastAPI Router (/api/analyze)
    participant Sec as Security Validator
    participant Ext as Article Extractor
    participant LLM as Claim Extractor (Gemini)
    participant FC as Google Fact Check Service
    participant Assessor as Evidence Assessor
    participant Fusion as Decision Fusion Engine
    participant Repo as SQLAlchemy Repository
    participant DB as SQLite Database

    User->>API: POST /api/analyze (URL: reuters.com/news-item)
    API->>Sec: validate_url_safety(URL)
    Sec-->>API: URL Validated (Public IPv4)
    
    API->>Ext: extract_article(URL)
    Ext-->>API: Article Text, Headline, Domain ("reuters.com")

    par Claim Extraction & Source Analysis
        API->>LLM: extract_claims(Text, Headline)
        LLM-->>API: List of Extracted Claims & Search Queries
    and
        API->>Fusion: assess_source("reuters.com")
    end

    API->>FC: search_claims(claim.search_queries)
    FC-->>API: List of FactCheckItems (ClaimReviews)

    API->>Assessor: assess_and_link_evidence(Claims, FactChecks)
    Assessor-->>API: Claims Linked (Stopwords Filtered)

    API->>Fusion: fuse(Claims, FactChecks, SourceReport, TextModel)
    Fusion-->>API: DecisionFusionReport ("Supported by available evidence")

    API->>Repo: save_report(FullPayload)
    Repo->>DB: INSERT into analyses
    DB-->>Repo: Saved (UUID)
    
    API-->>User: HTTP 200 OK (AnalysisResponse JSON)
```

---

## Figure 4.8: Sequence Diagram — Multimodal Image Submission & Context Consistency Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant API as FastAPI Router
    participant ImgVal as SafeImageValidator
    participant ImgSvc as ImageAnalyzer (Pillow)
    participant Pipe as Pipeline Orchestrator
    participant Fusion as Decision Fusion Engine

    User->>API: POST /api/analyze (Text + Multipart Image Binary)
    API->>ImgVal: validate_and_load(image_bytes)
    
    alt File Size > 5MB or Pixels > 10MP
        ImgVal-->>API: Raise HTTP 400 Bad Request
        API-->>User: Error: Image exceeds maximum allowed boundaries
    else Valid Image Payload
        ImgVal-->>API: Verified PIL.Image Object
        API->>Pipe: Run Multimodal Pipeline
        
        par Parallel Execution
            Pipe->>ImgSvc: analyze_image(PIL.Image, ArticleClaims)
            ImgSvc->>ImgSvc: Inspect EXIF, Luminance, & Color Histogram
            ImgSvc->>ImgSvc: Check Daylight / Temporal Heuristic
            ImgSvc-->>Pipe: ImageModelAnalysis (Flag: POTENTIAL_CONTEXT_MISMATCH)
        and
            Pipe->>Pipe: Execute Text & Evidence Subsystems
        end

        Pipe->>Fusion: fuse(Claims, Evidence, Source, Text, ImageAnalysis)
        Note over Fusion: Rule 4 Triggers: Multimodal Context Inconsistency
        Fusion-->>Pipe: Verdict: "Misleading or missing context" (Uncertainty: Moderate)
        
        Pipe-->>User: HTTP 200 OK (Render Multimodal Alert & Visual Discrepancy)
    end
```

---

## Figure 4.9: Sequence Diagram — Graceful Degradation & Provider Fallback Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Pipe as Pipeline Orchestrator
    participant Gemini as Gemini API Client
    participant LocalNLP as Rule-Based Local NLP Extractor
    participant GDELT as GDELT 2.0 API Client
    participant Fusion as Decision Fusion Engine

    User->>Pipe: Analyze Article Submission
    Pipe->>Gemini: POST /models/gemini-3.8-flash:generateContent (Timeout: 5.0s)
    
    alt Gemini Returns HTTP 503 (Overloaded) or HTTP 429 (Quota Exceeded)
        Gemini-->>Pipe: HTTP 503 / 429 Error
        Note over Pipe: Automated Fallback Triggered Instantly
        Pipe->>LocalNLP: _extract_with_local_nlp(Text, Headline)
        LocalNLP-->>Pipe: Return Extracted Claims & Entity Queries (0.5ms)
    else Gemini Network Timeout (5.0s elapsed)
        Pipe->>LocalNLP: _extract_with_local_nlp(Text, Headline)
        LocalNLP-->>Pipe: Return Extracted Claims & Entity Queries
    end

    Pipe->>GDELT: search_news(Queries) (Timeout: 4.0s)
    alt GDELT Returns HTTP 429 or Times Out
        GDELT-->>Pipe: Timeout / Rate Limit Detected
        Note over Pipe: Abort GDELT cleanly; return empty list []
    end

    Pipe->>Fusion: fuse(Claims, AvailableEvidence, Source, Text)
    Fusion-->>Pipe: Synthesized Verdict without Pipeline Interruption
    Pipe-->>User: HTTP 200 OK (Status: COMPLETED with Fallback Notes)
```

---

## Figure 4.10: Entity-Relationship Database Schema Diagram

```mermaid
erDiagram
    ANALYSES {
        string id PK "UUID primary key (char 36)"
        string article_url "URL of article (varchar 2048, nullable)"
        string headline "Headline or central claim (varchar 1024)"
        text article_summary "Extracted summary text (text, nullable)"
        string publisher "Extracted publisher name (varchar 255)"
        string domain "Extracted domain name (varchar 255)"
        string author "Extracted author byline (varchar 255)"
        string published_date "Publication date string (varchar 64)"
        string input_type "Input mode: url, text, multimodal"
        int has_image "Boolean flag: 0 or 1"
        string final_assessment "Final categorical verdict (varchar 64)"
        text assessment_explanation "Auditable narrative explanation"
        string uncertainty_level "Uncertainty rating: Low, Moderate, High"
        float source_credibility_score "Calculated domain score (0-100)"
        string source_assessment_status "Status: Assessed, Unavailable"
        string text_model_prediction "Prediction: Credible, Neutral, Risk"
        float text_model_confidence "Model confidence score (0.0-1.0)"
        float image_text_relevance "Calculated relevance score"
        text image_analysis_summary "Visual context inspection notes"
        json extracted_claims "Serialized JSON list of claims"
        json fact_check_results "Serialized JSON list of ClaimReviews"
        json news_search_results "Serialized JSON list of news items"
        json source_credibility_breakdown "Serialized JSON factor dictionary"
        json decision_factors "Serialized JSON decision rules applied"
        json latency_breakdown_ms "Serialized JSON execution profile"
        float total_latency_ms "Total end-to-end execution latency"
        string status "Status: COMPLETED, PARTIAL, FAILED"
        json provider_status "Provider status dictionary"
        datetime created_at "Indexed UTC timestamp"
        string retrieval_timestamp "ISO formatted retrieval timestamp"
    }
```

---

## Figure 4.11: Algorithmic Decision Fusion Flowchart

```mermaid
flowchart TD
    Start([Start: Ingest Linked Claims, Evidence, Source, Text, Image]) --> LinkCheck{Were Claims Assessed by Pipeline?}
    
    LinkCheck -- Yes --> FilterMatched[Filter Fact-Checks Matched to Claim IDs via Evidence Assessor]
    LinkCheck -- No --> RawCount[Count Raw Fact-Check Verdicts - Standalone Mode]
    
    FilterMatched --> Rule1{Rule 1: Are Matched False/Mixed Fact-Checks > 0?}
    RawCount --> Rule1
    
    Rule1 -- Yes --> VerdictContradicted["Final Assessment: Contradicted by available evidence<br/>Uncertainty: Low<br/>Rule 1 Applied"]
    
    Rule1 -- No --> Rule2{Rule 2: Is Source Score <= 20.0 (Known Satire / Conspiracy)?}
    Rule2 -- Yes --> VerdictSatire["Final Assessment: Misleading or missing context<br/>Uncertainty: Low<br/>Rule 2 Applied"]
    
    Rule2 -- No --> Rule3{Rule 3: Are Matched True Fact-Checks > 0 AND Contradictions == 0?}
    Rule3 -- Yes --> VerdictSupportedFC["Final Assessment: Supported by available evidence<br/>Uncertainty: Low<br/>Rule 3 Applied"]
    
    Rule3 -- No --> Rule4{Rule 4: Is Image Flagged for Context Mismatch?}
    Rule4 -- Yes --> VerdictImageMismatch["Final Assessment: Misleading or missing context<br/>Uncertainty: Moderate<br/>Rule 4 Applied"]
    
    Rule4 -- No --> Rule5{Rule 5: Are Supporting Evidence > 0 AND Contradicting Evidence > 0?}
    Rule5 -- Yes --> VerdictConflict["Final Assessment: Conflicting evidence<br/>Uncertainty: Moderate<br/>Rule 5 Applied"]
    
    Rule5 -- No --> Rule6{Rule 6: Are Supporting News Outlets >= 2 AND Contradictions == 0?}
    Rule6 -- Yes --> VerdictMultiNews["Final Assessment: Supported by available evidence<br/>Uncertainty: Low / Moderate<br/>Rule 6 Applied"]
    
    Rule6 -- No --> Rule6b{Rule 6b: Is Source Score >= 70.0 AND Text Objective AND Contradictions == 0?}
    Rule6b -- Yes --> VerdictAccreditedSource["Final Assessment: Supported by available evidence<br/>Uncertainty: Moderate<br/>Rule 6b Applied"]
    
    Rule6b -- No --> Rule7{Rule 7: Is Text Flagged Misinformation Risk AND Total Evidence == 0?}
    Rule7 -- Yes --> VerdictStylisticRisk["Final Assessment: Insufficient evidence<br/>Uncertainty: High<br/>Rule 7 Applied (Style Alert)"]
    
    Rule7 -- No --> Rule8["Final Assessment: Insufficient evidence<br/>Uncertainty: High<br/>Rule 8 Applied (Default Baseline)"]

    VerdictContradicted --> End([Return DecisionFusionReport])
    VerdictSatire --> End
    VerdictSupportedFC --> End
    VerdictImageMismatch --> End
    VerdictConflict --> End
    VerdictMultiNews --> End
    VerdictAccreditedSource --> End
    VerdictStylisticRisk --> End
    Rule8 --> End
```
