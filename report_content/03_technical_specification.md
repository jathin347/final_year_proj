# CHAPTER 3 – TECHNICAL SPECIFICATION

## 3.1 Requirements Specification

The technical specification of the VeritasAI platform establishes the formal requirements governing system behavior, architectural interactions, security boundaries, and operational performance. Requirements are categorized into Functional Requirements (defining what the system must perform) and Non-Functional Requirements (defining the behavioral qualities, constraints, and standards under which the system must operate).

---

### 3.1.1 Functional Requirements

The functional requirements encompass all user-facing interactions, backend ingestion processes, computational NLP analysis, external API communication, evidence synthesis, and data persistence operations. Table 3.1 details fourteen primary functional requirements (FR-01 through FR-14), their functional descriptions, and their implementation priority (categorized as *High, Medium,* or *Low*).

| Req ID | Requirement Title | Functional Description & Operational Behavior | Priority |
| :--- | :--- | :--- | :--- |
| **FR-01** | Multi-Modal Input Submission | The system shall provide an intuitive user interface and REST API endpoint (`POST /api/analyze`) capable of accepting: (a) raw article text or claims up to 50,000 characters, (b) live article URLs up to 2,048 characters, and (c) optional paired image files (JPEG, PNG, WEBP) up to 5 MB in size. | High |
| **FR-02** | SSRF & Scheme Validation | Prior to performing external network requests, the system shall validate user-supplied URLs using DNS resolution to intercept and reject private/internal IP addresses (RFC 1918, RFC 3927, loopbacks, link-local addresses) and non-HTTP/HTTPS protocols (`file://`, `ftp://`, `gopher://`). | High |
| **FR-03** | Document Extraction & Parsing | When a valid external URL is submitted, the system shall fetch the HTML payload using asynchronous HTTP clients, follow redirects safely, extract clean article prose, and parse structural metadata (title, author byline, domain, and publication date) using BeautifulSoup4. | High |
| **FR-04** | LLM Claim Decomposition | The system shall submit extracted article text to the Google Gemini 3.8 Flash API with structured JSON schema prompting to isolate 1 to 5 atomic, verifiable factual claims, identify named entities, extract temporal bounds, and synthesize optimized search queries. | High |
| **FR-05** | Rule-Based NLP Claim Fallback | If the Gemini API call fails due to HTTP errors (503, 429), quota limits, or times out after 5.0 seconds, the system shall automatically fall back to a deterministic local NLP claim extractor without crashing or stalling the overarching verification pipeline. | High |
| **FR-06** | Google Fact Check API Querying | For each extracted claim search query, the system shall programmatically query the Google Fact Check Tools API (`claims:search`), parse ClaimReview schemas, deduplicate results, and normalize diverse publisher ratings into standardized verdicts (*TRUE, FALSE, MIXED, UNPROVEN*). | High |
| **FR-07** | GDELT News Search & Deduplication | The system shall query the GDELT 2.0 Global Document API for independent news coverage corroborating or refuting extracted assertions, automatically filtering syndicated duplicates via URL canonicalization and title hash matching. | Medium |
| **FR-08** | Tokenized Semantic Evidence Linking | The system shall compute tokenized cosine similarity between extracted claims and retrieved external evidence items, applying an institutional stop-word suppression dictionary (`GENERIC_TOPIC_WORDS`) to eliminate spurious keyword overlap before linking evidence to specific claim IDs. | High |
| **FR-09** | Four-Factor Source Credibility | The system shall evaluate publishing domains across four weighted dimensions: Domain Track Record (40%), TLD & Registration Integrity (25%), Author Attribution (20%), and Publisher Transparency (15%), strictly capping known satire/conspiracy sites at $\le 25.0$ points. | High |
| **FR-10** | Stylometric Text Classification | The system shall process submitted text through a calibrated scikit-learn TF-IDF and Logistic Regression pipeline, computing an objective stylometric prediction (*Credible / Objective Phrasing, Neutral / Mixed, Elevated Misinformation Risk*), confidence score, and sensationalism index. | High |
| **FR-11** | Safe Image Inspection & Context Heuristic | The system shall inspect uploaded imagery using Pillow, enforcing a 10 megapixel decompress-bomb limit, validating image headers, calculating luminance and color distributions, and flagging potential temporal or lighting context discrepancies relative to article claims. | Medium |
| **FR-12** | Hierarchical Decision Fusion | The system shall execute an eight-tier rule hierarchy synthesizing claims, fact-checks, news coverage, source credibility, text predictions, and image flags into one of six mutually exclusive final verdicts accompanied by a categorized uncertainty rating (*Low, Moderate, High*). | High |
| **FR-13** | Database Persistence & Telemetry | The system shall serialize complete analysis records—including claim linkages, raw evidence items, provider execution statuses, and millisecond-level latency telemetry—into an SQLite database via SQLAlchemy ORM. | High |
| **FR-14** | Paginated History Retrieval & Inspection | The system shall provide REST API endpoints (`GET /api/history`, `GET /api/history/{id}`, `DELETE /api/history/{id}`) enabling users to view, search, inspect, and delete previously executed verification records through the frontend dashboard. | Medium |

---

### 3.1.2 Non-Functional Requirements

Non-functional requirements specify the operational criteria, behavioral quality attributes, and architectural constraints necessary to guarantee an enterprise-grade, secure, and user-friendly platform. Table 3.2 outlines these requirements across six foundational engineering pillars.

| Quality Attribute | Requirement Identifier & Criteria | Empirical Metric / Target Threshold |
| :--- | :--- | :--- |
| **Performance & Latency** | **NFR-01 (End-to-End Latency):** The complete multi-stage pipeline—including claim extraction, external API retrieval, machine learning inference, and decision fusion—shall complete processing within a bounded time envelope. | Mean pipeline latency $\le 25.0$ seconds during live global API calls; local fallback execution $\le 8.0$ seconds. |
| **Performance & Latency** | **NFR-02 (Local Model Inference):** Text stylometric classification and rule-based NLP claim extraction shall execute instantaneously on CPU hardware. | Local model inference latency $\le 5.0$ milliseconds per article submission. |
| **Security & Safety** | **NFR-03 (SSRF Immunity):** The system shall intercept and block all attempts to force backend servers to query internal network assets, localhost loopbacks, or cloud instance metadata services. | 100% rejection rate for IP addresses in `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, and `169.254.169.254`. |
| **Security & Safety** | **NFR-04 (Decompression Bomb Defense):** Uploaded image assets shall be validated before allocating memory buffers to prevent denial-of-service memory exhaustion. | Maximum physical file size capped at 5 MB; `MAX_IMAGE_PIXELS` strictly bounded at 10,000,000 pixels (10 MP). |
| **Security & Safety** | **NFR-05 (Secret Credential Isolation):** API keys for Google Fact Check and Gemini services shall never be exposed in client bundles, serialized in database records, or leaked in error responses. | Zero plain-text API keys present in Git version control, client network payloads, or server logging streams. |
| **Reliability & Availability** | **NFR-06 (Graceful API Degradation):** Third-party external API failures (HTTP 503, 429, or connection timeouts) shall not cause unhandled exceptions or crash the backend service. | 100% graceful degradation via automated NLP fallbacks and clean empty-list returns on external service failure. |
| **Reliability & Availability** | **NFR-07 (Database Thread Safety):** Database operations shall execute without connection pool exhaustion, locking conflicts, or session leaks under concurrent user submissions. | Thread-safe scoped session lifecycle management with guaranteed `try-finally` session closing on all API routes. |
| **Epistemic Soundness** | **NFR-08 (Zero Unsupported Verdict Rate):** The decision fusion engine shall never generate a definitive factual verdict (*Supported* or *Contradicted*) without verified external corroboration. | 0.0% unsupported verdict rate on benchmark datasets; unevidenced claims strictly yield *Insufficient evidence*. |
| **Maintainability** | **NFR-09 (Modular Service Architecture):** Backend components shall be decoupled into dedicated, single-responsibility service classes with explicit Pydantic schema contracts. | Zero direct cross-service database access; 100% data transfer mediated by validated Pydantic models. |
| **Usability & UX** | **NFR-10 (Frontend Accessibility & Responsiveness):** The web dashboard shall render fluidly across mobile, tablet, and desktop viewports, providing clear visual status indicators and explanatory tooltips. | Sub-second client rendering (First Contentful Paint $\le 1.2$ s); responsive breakpoints for screen widths down to 320px. |

---

## 3.2 Feasibility Study

A thorough feasibility study was conducted prior to full-scale development, evaluating the technical viability, economic sustainability, and broader social implications of the VeritasAI platform.

### 3.2.1 Technical Feasibility

The technical feasibility of the proposed architecture was evaluated across five critical engineering domains:

1. **Computational Linguistics and Open-Domain Retrieval:**  
   The feasibility of decomposing unstructured news prose into atomic claims and querying external knowledge bases is well-established in modern NLP literature [8], [10]. Traditional approaches failed primarily due to computational bottlenecks in dense passage retrieval across multi-terabyte web archives. VeritasAI bypasses this limitation by interfacing with pre-indexed, authoritative knowledge bases: the Google Fact Check Tools API (which aggregates verified claims published by IFCN-accredited organizations) and the GDELT Project (which monitors global broadcast and print news across over 100 languages). This hybrid architecture allows the platform to achieve global evidentiary coverage without incurring the massive infrastructure overhead of operating a custom planetary web crawler.

2. **Language Model Orchestration and Fallback Feasibility:**  
   Utilizing Google Gemini 3.8 Flash via structured JSON schema instructions enables high-fidelity claim decomposition with structured entity extraction in 1 to 5 seconds. However, acknowledging the operational volatility of cloud LLMs, the feasibility of a dual-tier design was proven through the implementation of `_extract_with_local_nlp()`. By leveraging deterministic regular expressions, entity recognition heuristics, and sentence checkability scoring, the platform maintains uninterrupted core claim extraction even during total external API outages.

3. **Machine Learning Pipeline on Commodity Hardware:**  
   The stylometric classification model utilizes an n-gram TF-IDF vectorizer coupled with a regularized Logistic Regression classifier. This ensemble possesses a microscopic memory footprint (the serialized model artifact in `models/stylistic_classifier.joblib` requires only 20.2 KB of storage) and achieves inference in under 1.0 millisecond on standard modern CPU cores. Consequently, the machine learning subsystem requires no specialized GPU hardware, ensuring high operational feasibility on minimal cloud virtual machines.

4. **Software Framework Maturity and Asynchronous Concurrency:**  
   The selection of Python 3.13, FastAPI, HTTPX, and React 18 provides an exceptionally mature, production-grade foundation. FastAPI’s native asynchronous event loop enables the server to execute multiple external HTTP queries (Google Fact Check, GDELT, and Gemini) concurrently rather than sequentially, reducing total end-to-end verification latency from over 30 seconds to an average of 8 to 15 seconds.

---

### 3.2.2 Economic Feasibility

A critical barrier preventing the widespread deployment of automated fact-checking systems in local newsrooms and academic institutions is prohibitive infrastructure cost. Commercial deep learning pipelines often require dedicated high-memory GPU instances (such as NVIDIA A100 or H100 clusters) costing thousands of dollars per month to run large Transformer models locally. 

VeritasAI was specifically engineered for extreme economic sustainability, leveraging lightweight CPU-optimized local models, open-access public APIs, and efficient asynchronous server execution. Table 3.3 presents an itemized cost analysis demonstrating that the platform can be deployed and operated at an enterprise scale for under $25 per month in cloud infrastructure, or virtually $0.00 for academic and research prototype deployments.

| Cost Category / Service Component | Provider / Infrastructure Specification | Monthly Usage / Tier Allocation | Estimated Monthly Cost (USD) |
| :--- | :--- | :--- | :--- |
| **Compute & Backend Hosting** | Standard Linux Virtual Machine (2 vCPU, 4 GB RAM, e.g., AWS t3.medium or DigitalOcean Droplet) | 24/7 continuous uptime running FastAPI / Uvicorn server | $12.00 – $20.00 |
| **Static Frontend Hosting** | Vercel, Netlify, or Cloudflare Pages | Unlimited bandwidth, global CDN edge distribution for React/Vite bundle | $0.00 (Free Tier) |
| **Database Storage** | Local SQLite (`fake_news.db`) mounted on persistent SSD storage volume | Up to 100,000 complete verification audit runs (~150 MB) | $0.00 (Included in VM) |
| **Google Fact Check Tools API** | Google Cloud Platform (`factchecktools.googleapis.com`) | Up to 25,000 queries per month under standard developer quota | $0.00 (Free Tier / No Charge) |
| **Google Gemini API** | Google AI Studio (`models/gemini-3.8-flash`) | Up to 15 requests per minute (RPM) under developer free tier allocation | $0.00 (Free Tier Allocation) |
| **GDELT 2.0 DOC API** | The GDELT Project (`api.gdeltproject.org`) | Public open-access research API for global document retrieval | $0.00 (Free Open Access) |
| **SSL / TLS Certificate** | Let's Encrypt Automated Domain Validation | Automated 90-day renewal certificates via Certbot | $0.00 (Open Source) |
| **Domain Registration** | Top-Level Domain (e.g., `.org` or `.edu`) | Annual registration amortized monthly | $1.00 – $1.50 |
| **Total Estimated Operating Cost** | **Complete Full-Stack Operational Deployment** | **Enterprise Research / University Department Scale** | **$13.00 – $21.50 / month** |

---

### 3.2.3 Social Feasibility

The social feasibility and ethical impact of an automated fake news verification platform are paramount. Historically, automated detection systems have faced severe skepticism and resistance from both journalists and the general public due to concerns over algorithmic censorship, ideological bias, and opacity [11]. The design of VeritasAI directly addresses these socio-technical concerns through four foundational principles:

1. **Analytical Decision Support vs. Censorship:**  
   The platform is deliberately designed as an analytical decision-support instrument, not an autonomous censorship engine. It does not interface with content removal APIs, nor does it block internet domains. It empowers journalists, researchers, and citizens with transparent, verifiable evidence, leaving final editorial and civic judgment to human intellect.

2. **Epistemic Humility and Uncertainty Transparency:**  
   Traditional black-box models create societal harm by asserting certainty where evidence is absent. By contrast, VeritasAI incorporates explicit epistemic uncertainty levels (*Low, Moderate, High*). When independent evidence cannot be retrieved, the system explicitly returns *Insufficient evidence* and displays the disclaimer: *"The absence of evidence does not establish whether the assertion is true or false."* This transparency prevents algorithmic overreach and fosters critical thinking among users.

3. **Protection of Local and Grassroots Journalism:**  
   By establishing an uncalibrated neutral baseline (~50.0) for unprofiled publishers rather than penalizing unfamiliar domains, the platform actively protects hyper-local reporting, regional student newspapers, and independent civic blogs from being marginalized by automated trust filters.

4. **Civic Education and Information Literacy:**  
   The frontend dashboard features a dedicated Methodology Guide and interactive factor breakdowns that educate users on how source credibility is evaluated, how factual claims are isolated, and how professional fact-checking organizations verify public discourse. In doing so, the platform contributes directly to elevating digital media literacy across society.

---

## 3.3 System Specification

To guarantee reproducibility and provide an exact blueprint for deployment, the system specifications are categorized into hardware specifications (detailing the computational environments required and utilized) and software specifications (documenting the exact library versions extracted directly from repository configuration files).

### 3.3.1 Hardware Specification

Table 3.4 outlines the hardware specifications across three operational tiers: the absolute minimum configuration required to run the stack, the recommended production configuration for handling multi-user traffic, and the exact development benchmark environment utilized during project construction and testing.

| Hardware Component | Minimum System Requirement | Recommended Production Specification | As Used in Project Development / Benchmark |
| :--- | :--- | :--- | :--- |
| **Processor (CPU)** | 64-bit Dual-Core x86_64 or ARM64 processor (1.8 GHz) | Quad-Core x86_64 or ARM64 processor (2.5 GHz or higher) | Apple M-Series Silicon (8-Core ARM64 Architecture) |
| **System Memory (RAM)**| 2 GB Physical RAM | 8 GB Physical RAM (DDR4 or LPDDR5) | 16 GB Unified Memory Architecture (UMA) |
| **Storage Capacity** | 5 GB available disk space | 20 GB Solid State Drive (NVMe SSD) | 512 GB High-Speed NVMe Solid State Drive |
| **Graphics Processing (GPU)**| None (Not required for CPU inference) | None required (Optional GPU acceleration for PyTorch) | Metal Performance Shaders (MPS) capable integrated GPU |
| **Network Interface** | 10 Mbps broadband internet connection | 100 Mbps high-speed low-latency broadband interface | High-speed low-latency Wi-Fi 6 broadband network |
| **Display Resolution** | 1280 $\times$ 720 pixels | 1920 $\times$ 1080 pixels (Full HD) | 2560 $\times$ 1600 Retina Display |

---

### 3.3.2 Software Specification

Table 3.5 provides an exhaustive inventory of the software tools, runtime environments, core frameworks, and specific Python/Node.js packages utilized in VeritasAI, citing the exact version constraints extracted directly from `backend/requirements.txt` and `frontend/package.json`.

| Software Category | Tool / Library Name | Exact Version Constraint | Architectural Purpose in VeritasAI |
| :--- | :--- | :--- | :--- |
| **Operating System** | macOS / POSIX Linux | macOS Sequoia / Ubuntu 22.04 LTS | Host operating system and runtime execution environment |
| **Language Runtime** | Python | 3.13.9 | Backend language runtime supporting asynchronous execution |
| **Web Framework** | FastAPI | `fastapi>=0.115.0` | High-performance asynchronous REST API framework |
| **ASGI Server** | Uvicorn | `uvicorn>=0.30.0` | Lightning-fast ASGI server implementation for Python |
| **Data Validation** | Pydantic | `pydantic>=2.8.0` | Strict data schema validation and serialization |
| **Configuration** | Pydantic Settings | `pydantic-settings>=2.4.0` | Environment variable parsing and configuration management |
| **ORM / Database** | SQLAlchemy | `sqlalchemy>=2.0.30` | Object-Relational Mapping and database connection pooling |
| **Database Engine** | SQLite3 | Native embedded engine | Persistent local database storage (`fake_news.db`) |
| **HTTP Client** | HTTPX | `httpx>=0.27.0` | Asynchronous HTTP client with connection pooling and timeouts |
| **HTML Parser** | BeautifulSoup4 | `beautifulsoup4>=4.12.0` | Clean web scraping, DOM traversal, and article text extraction |
| **Form Processing** | Python-Multipart | `python-multipart>=0.0.9` | Streaming multipart/form-data parser for image/text upload |
| **Image Processing** | Pillow (PIL) | `pillow>=10.4.0` | Safe image decoding, format verification, and pixel analysis |
| **Machine Learning** | Scikit-Learn | `scikit-learn>=1.5.0` | TF-IDF vectorization and Logistic Regression text classifier |
| **Scientific Computing**| NumPy | `numpy>=1.26.0` | High-performance array operations and mathematical scoring |
| **Data Manipulation** | Pandas | `pandas>=2.2.0` | Tabular data manipulation during model calibration and training |
| **Testing Framework** | Pytest | `pytest>=8.3.0` | Automated testing framework for unit and integration suites |
| **Async Testing** | Pytest-Asyncio | `pytest-asyncio>=0.24.0` | Coroutine and async endpoint testing support in Pytest |
| **Node.js Runtime** | Node.js | v20.18.0 (LTS) | JavaScript runtime environment for frontend development |
| **Frontend Framework**| React | `react^18.3.1` | Declarative component-based UI rendering engine |
| **DOM Renderer** | React-DOM | `react-dom^18.3.1` | React Document Object Model reconciliation layer |
| **Build Tool / Bundler**| Vite | `vite^5.4.14` | Ultra-fast frontend development server and ES module bundler |
| **Language Extension** | TypeScript | `typescript^5.7.3` | Static type checking matching backend Pydantic models |
| **CSS Styling Engine** | Tailwind CSS | `tailwindcss^3.4.17` | Utility-first responsive CSS styling with dark mode tokens |
| **Icon Library** | Lucide React | `lucide-react^0.475.0` | Modern, lightweight SVG iconography for dashboards |
| **Data Visualization** | Recharts | `recharts^2.15.1` | SVG-based charting library for latency profiling visualizations |
| **CSS Utilities** | clsx & tailwind-merge | `clsx^2.1.1`, `tailwind-merge^3.0.1` | Dynamic conditional class merging without utility conflicts |
