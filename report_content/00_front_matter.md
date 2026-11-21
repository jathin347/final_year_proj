# FRONT MATTER

## PROJECT CONTEXT
- **Project Title:** [NOT FOUND – I will supply] *(Repository Working Title: AI-Powered Real-Time Fake News Detector with Source Credibility Scoring and Multimodal Verification / VeritasAI)*
- **Course Code & Title:** BCSE497J – Project-I
- **Institution:** School of Computer Science and Engineering, Vellore Institute of Technology (VIT)
- **One-Line Purpose:** [NOT FOUND – I will supply] *(System Purpose: A multi-tier fake news verification platform combining LLM factual claim decomposition, live fact-checking API retrieval, stylometric text classification, domain credibility scoring, and evidence-grounded decision fusion.)*
- **Team Size / Roles:** [NOT FOUND – I will supply]
- **Project Guide:** [NOT FOUND – I will supply]

---

## ABSTRACT

The proliferation of unverified, sensationalist, and deliberately falsified information across online news platforms and social networks poses an existential threat to democratic discourse, public health communication, and financial market integrity. Traditional automated fake news detection frameworks often rely exclusively on monolithic deep neural network classifiers that generate binary veracity predictions without providing verifiable external evidence or explaining their underlying reasoning. Such black-box predictions suffer from severe epistemic limitations: linguistic style alone does not establish empirical falsehood, deep learning confidence metrics do not correlate with factual truth probability, and static models rapidly become obsolete when confronting emergent news events. 

To overcome these structural deficiencies, this project presents **VeritasAI**, an end-to-end, real-time fake news verification and source credibility scoring platform with multimodal consistency verification. The proposed system rejects black-box classification in favor of an evidence-grounded, multi-stage analytical architecture. When an article URL or text passage is ingested, the system validates the request against strict Server-Side Request Forgery (SSRF) and DNS-rebinding security safeguards before extracting clean article prose and structural metadata using custom document parsers. A dual-tier claim extraction module utilizes Google Gemini 3.8 Flash via structured JSON schema instructions—with an automated, rule-based natural language processing (NLP) fallback—to decompose complex articles into atomic, verifiable factual assertions, identifying named entities, temporal markers, and targeted search queries.

Each extracted claim is cross-referenced concurrently against authoritative, independent verification databases through the Google Fact Check Tools API and the GDELT 2.0 Global Document API. The retrieved evidence is matched to individual claims using tokenized cosine similarity combined with institutional stop-word filtering to prevent false contextual matches. In parallel, the platform executes a multi-signal stylistic evaluation employing a calibrated TF-IDF and Logistic Regression ensemble model, computes an objective four-factor source credibility score (evaluating domain historical track records, top-level domain integrity, author attribution, and publisher transparency), and analyzes optional image attachments for dimensions, metadata integrity, and potential lighting/context discrepancies.

Finally, an explainable Decision Fusion Engine synthesizes these multi-source signals through an epistemologically grounded rule hierarchy. The engine strictly ensures that model predictions are never treated as factual proof, missing fact-checks never imply falsehood, and unknown publishers are never penalized without empirical basis. Evaluated across real-world investigative scenarios and a curated benchmark suite, the platform demonstrates a 0.0% unsupported verdict rate, an average processing latency between 8.9 and 21.0 seconds across live global APIs, and complete explanatory transparency. The frontend dashboard, implemented in React 18, Vite, and Tailwind CSS, provides journalists, researchers, and citizens with an interactive evidentiary breakdown, claim-level badges, source credibility gauges, and execution profiling metrics.

---

## LIST OF ABBREVIATIONS

| Abbreviation | Expansion / Definition |
| :--- | :--- |
| **API** | Application Programming Interface |
| **AUC** | Area Under the Receiver Operating Characteristic Curve |
| **BCSE497J** | B.Tech Computer Science and Engineering Project-I Course Code |
| **BOM** | Byte Order Mark |
| **CORS** | Cross-Origin Resource Sharing |
| **CPU** | Central Processing Unit |
| **CSRF** | Cross-Site Request Forgery |
| **DFD** | Data Flow Diagram |
| **DNS** | Domain Name System |
| **DOM** | Document Object Model |
| **DoD** | Denial of Service |
| **ER** | Entity-Relationship |
| **F1** | Harmonic Mean of Precision and Recall |
| **FDA** | Food and Drug Administration |
| **GDELT** | Global Database of Events, Language, and Tone |
| **Gantt** | Gantt Chart (Project Scheduling Tool) |
| **GPU** | Graphics Processing Unit |
| **HMR** | Hot Module Replacement |
| **HTML** | HyperText Markup Language |
| **HTTP** | Hypertext Transfer Protocol |
| **HTTPS** | Hypertext Transfer Protocol Secure |
| **IEEE** | Institute of Electrical and Electronics Engineers |
| **IP** | Internet Protocol |
| **IPv4** | Internet Protocol Version 4 |
| **IPv6** | Internet Protocol Version 6 |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **LBFGS** | Limited-memory Broyden–Fletcher–Goldfarb–Shanno Algorithm |
| **LLM** | Large Language Model |
| **MIME** | Multipurpose Internet Mail Extensions |
| **MP** | Megapixels |
| **NER** | Named Entity Recognition |
| **NLP** | Natural Language Processing |
| **NLTK** | Natural Language Toolkit |
| **ORM** | Object-Relational Mapping |
| **OS** | Operating System |
| **PIL / Pillow** | Python Imaging Library Fork |
| **POSIX** | Portable Operating System Interface |
| **RAM** | Random Access Memory |
| **REST** | Representational State Transfer |
| **ROC** | Receiver Operating Characteristic |
| **SDLC** | Software Development Life Cycle |
| **SQL** | Structured Query Language |
| **SSRF** | Server-Side Request Forgery |
| **TF-IDF** | Term Frequency-Inverse Document Frequency |
| **TLD** | Top-Level Domain |
| **TLS** | Transport Layer Security |
| **UAT** | User Acceptance Testing |
| **UI** | User Interface |
| **URI** | Uniform Resource Identifier |
| **URL** | Uniform Resource Locator |
| **UUID** | Universally Unique Identifier |
| **VIT** | Vellore Institute of Technology |
| **Vite** | Frontend Development Build Tool (French for "Fast") |
| **WHO** | World Health Organization |
| **XSS** | Cross-Site Scripting |

---

## SYMBOLS AND NOTATIONS

| Symbol | Mathematical / Technical Meaning | Units / Domain |
| :--- | :--- | :--- |
| $\text{tf}(t, d)$ | Term Frequency of token $t$ in document $d$ | Dimensionless ratio |
| $\text{idf}(t, D)$ | Inverse Document Frequency of token $t$ across corpus $D$ | $\log(\text{ratio})$ |
| $S_{\cos}(A, B)$ | Cosine similarity between token vector $A$ and token vector $B$ | $[-1.0, 1.0]$ |
| $C$ | Inverse regularization parameter in Logistic Regression | Positive scalar |
| $W_{\text{track}}$ | Weight allocated to historical domain track record in source scoring | 0.40 (40%) |
| $W_{\text{tld}}$ | Weight allocated to Top-Level Domain and registration integrity | 0.25 (25%) |
| $W_{\text{author}}$ | Weight allocated to author byline and attribution signals | 0.20 (20%) |
| $W_{\text{pub}}$ | Weight allocated to publisher identification and transparency | 0.15 (15%) |
| $P(y=1 \mid x)$ | Probability of misinformation risk given extracted text feature vector $x$ | $[0.0, 1.0]$ |
| $\Delta t$ | Processing execution duration / latency | Milliseconds (ms) |

---

## DRAFT LIST OF FIGURES

- **Figure 4.1:** VeritasAI Multi-Tier Pipeline Architecture Diagram
- **Figure 4.2:** Data Flow Diagram Level 0 (Context Diagram)
- **Figure 4.3:** Data Flow Diagram Level 1 (Pipeline Decomposition)
- **Figure 4.4:** Data Flow Diagram Level 2 (Evidence Retrieval & Fusion Subsystem)
- **Figure 4.5:** System Use Case Diagram
- **Figure 4.6:** Unified Backend & Frontend Class Diagram
- **Figure 4.7:** Sequence Diagram — Primary Live Fact-Checking Verification Workflow
- **Figure 4.8:** Sequence Diagram — Multimodal Image Submission & Context Consistency Workflow
- **Figure 4.9:** Sequence Diagram — Graceful Degradation & Provider Fallback Workflow
- **Figure 4.10:** Entity-Relationship (ER) Database Schema Diagram
- **Figure 4.11:** Algorithmic Decision Fusion & Epistemic Rule Evaluation Flowchart
- **Figure 7.1:** Latency Breakdown Across Core Pipeline Verification Stages
- **Figure 7.2:** Confusion Matrix of Calibrated Stylometric Classification Model
- **Figure 7.3:** Source Credibility Factor Distribution Comparison

---

## DRAFT LIST OF TABLES

- **Table 2.1:** Comprehensive Comparative Analysis of Existing Automated Fake News Detection Literature
- **Table 2.2:** Project Work Breakdown Structure and Execution Schedule (Gantt Milestone Mapping)
- **Table 2.3:** Risk Assessment and Epistemic Mitigation Matrix
- **Table 3.1:** Functional Requirements Specification (FR-01 through FR-14)
- **Table 3.2:** Non-Functional Requirements Specification with Measurable Metrics
- **Table 3.3:** Comprehensive Economic Feasibility and Cloud Service Cost Analysis
- **Table 3.4:** Hardware Environment Specifications (Minimum, Recommended, and Development Benchmark)
- **Table 3.5:** Software Environment Stack and Exact Dependency Specifications
- **Table 5.1:** Stylometric Classification Performance Metrics on Held-Out Test Split
- **Table 5.2:** Comprehensive Software Verification Test Cases (TC-01 through TC-25)
- **Table 5.3:** Defect Discovery, Security Remediation, and Refactoring Audit Log
- **Table 7.1:** Empirical Performance and Latency Across Three Real-World Verification Scenarios
- **Table 7.2:** Benchmark Evaluation on Multi-Domain Claim Dataset
- **Table 8.1:** Project Objectives Achievement vs. Initial Planning Matrix
