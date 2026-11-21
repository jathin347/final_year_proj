# STEP 3 – QUALITY CHECKS & REPORT AUDIT METRICS

This document provides the master index, quality metrics, placeholder catalog, and page volume estimates for the complete B.Tech Project-I technical report prepared for course **BCSE497J – Project-I** at the School of Computer Science and Engineering, Vellore Institute of Technology (VIT).

---

## 1. Master Index of Figures and Tables

### 1.1 List of Figures

| Figure Number | Chapter | Figure Caption / Title | Format / Implementation |
| :--- | :--- | :--- | :--- |
| **Figure 4.1** | Chapter 4 | VeritasAI Multi-Tier Pipeline Architecture Diagram | Mermaid flowchart (Presentation, Gateway, Services, Storage) |
| **Figure 4.2** | Chapter 4 | Data Flow Diagram Level 0 (Context Diagram) | Mermaid graph LR (External actors & core system) |
| **Figure 4.3** | Chapter 4 | Data Flow Diagram Level 1 (Pipeline Decomposition) | Mermaid graph TD (Processes 1.0 through 10.0) |
| **Figure 4.4** | Chapter 4 | Data Flow Diagram Level 2 (Evidence Retrieval & Fusion Subsystem) | Mermaid graph TD (Processes 7.0, 8.0, 9.0 detailed) |
| **Figure 4.5** | Chapter 4 | System Use Case Diagram | Mermaid graph LR (User, Auditor, API actors & use cases) |
| **Figure 4.6** | Chapter 4 | Unified Backend & Frontend Class Diagram | Mermaid classDiagram (Entities, Services, Schemas) |
| **Figure 4.7** | Chapter 4 | Sequence Diagram — Primary Live Fact-Checking Verification Workflow | Mermaid sequenceDiagram (Reuters URL end-to-end trace) |
| **Figure 4.8** | Chapter 4 | Sequence Diagram — Multimodal Image Submission & Context Consistency Workflow | Mermaid sequenceDiagram (Image bounds, Pillow, Rule 4) |
| **Figure 4.9** | Chapter 4 | Sequence Diagram — Graceful Degradation & Provider Fallback Workflow | Mermaid sequenceDiagram (Gemini 503/429 & GDELT fallback) |
| **Figure 4.10** | Chapter 4 | Entity-Relationship (ER) Database Schema Diagram | Mermaid erDiagram (`ANALYSES` SQLite table schema) |
| **Figure 4.11** | Chapter 4 | Algorithmic Decision Fusion & Epistemic Rule Evaluation Flowchart | Mermaid flowchart TD (Rules 1 through 8 decision tree) |
| **Figure 7.1** | Chapter 7 | VeritasAI Latency Profile Across Verification Stages | Matplotlib horizontal bar chart (Logarithmic scale) |
| **Figure 7.2** | Chapter 7 | Confusion Matrix for VeritasAI Stylometric Classifier | Seaborn heatmap (Held-out test split evaluation) |
| **Figure 7.3** | Chapter 7 | Source Credibility Factor Distribution Comparison | Matplotlib grouped bar chart (Reuters vs. The Onion) |

---

### 1.2 List of Tables

| Table Number | Chapter | Table Caption / Title | Contents & Scope |
| :--- | :--- | :--- | :--- |
| **Table 2.1** | Chapter 2 | Comprehensive Comparative Analysis of Existing Automated Fake News Detection Literature | 18 verifiable academic papers compared across 5 columns |
| **Table 2.2** | Chapter 2 | Project Work Breakdown Structure and Execution Schedule (Gantt Milestone Mapping) | 5 sequential SDLC phases, weekly timelines, milestones |
| **Table 2.3** | Chapter 2 | Risk Assessment and Epistemic Mitigation Matrix | 7 technical risks (R-01 to R-07) with codebase mitigations |
| **Table 3.1** | Chapter 3 | Functional Requirements Specification (FR-01 through FR-14) | 14 numbered functional requirements with priorities |
| **Table 3.2** | Chapter 3 | Non-Functional Requirements Specification with Measurable Metrics | 10 non-functional requirements with empirical thresholds |
| **Table 3.3** | Chapter 3 | Comprehensive Economic Feasibility and Cloud Service Cost Analysis | Itemized cloud infrastructure operating costs ($13–$21.50/mo) |
| **Table 3.4** | Chapter 3 | Hardware Environment Specifications | Minimum, recommended, and development benchmark hardware |
| **Table 3.5** | Chapter 3 | Software Environment Stack and Exact Dependency Specifications | Exact library versions from `requirements.txt` & `package.json` |
| **Table 5.1** | Chapter 5 | Stylometric Classification Performance Metrics on Held-Out Test Split | Precision, recall, and F1-score for classes 0 and 1 |
| **Table 5.2** | Chapter 5 | Comprehensive Software Verification Test Cases (TC-01 through TC-25) | 25 real test cases mapped to modules, inputs, outputs, status |
| **Table 5.3** | Chapter 5 | Defect Discovery, Security Remediation, and Refactoring Audit Log | 6 real bugs discovered and resolved during audit |
| **Table 7.1** | Chapter 7 | Empirical Performance and Latency Across Three Real-World Verification Scenarios | Measured metrics for Scenarios A, B, and C across 21 rows |
| **Table 7.2** | Chapter 7 | Benchmark Evaluation on Multi-Domain Claim Dataset | Unsupported verdict rate, conservative fallback, latency |
| **Table 7.3** | Chapter 7 | Architectural Comparison with Existing Literature Baselines | Feature comparison across 5 computational paradigms |
| **Table 8.1** | Chapter 8 | Project Objectives Achievement vs. Initial Planning Matrix | 9 formal project objectives mapped to achieved outcomes |

---

## 2. Inventory of Actionable Placeholders

The table below catalogs every placeholder requiring author input before final submission to VIT.

| Placeholder Category | File & Line | Target Field / Action | Instructions for Author |
| :--- | :--- | :--- | :--- |
| **`[NOT FOUND]`** | `00_front_matter.md:L4` | Project Title | Insert official university-registered project title. |
| **`[NOT FOUND]`** | `00_front_matter.md:L7` | One-Line Purpose | Insert approved project abstract one-liner. |
| **`[NOT FOUND]`** | `00_front_matter.md:L8` | Team Size / Roles | Insert student names, registration numbers, and role split. |
| **`[NOT FOUND]`** | `00_front_matter.md:L9` | Project Guide | Insert Faculty Guide name, designation, and department. |
| **`[NOT FOUND]`** | `02_project_description_and_goals.md:L287` | Team Allocation | Insert student names against the 4 module divisions. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L82` | Screen 1: Uvicorn Startup | Capture terminal after running `uvicorn backend.app.main:app`. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L90` | Screen 2: Swagger UI | Capture browser at `http://127.0.0.1:8000/docs`. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L98` | Screen 3: Home Dashboard | Capture home screen at `http://127.0.0.1:5173/`. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L106` | Screen 4: Provider Status Bar | Capture top status bar showing green active badges. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L114` | Screen 5: Preset Selection | Capture form populated via Reuters preset button. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L122` | Screen 6: Progress Indicator | Capture animated progress tracker during analysis. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L130` | Screen 7: Supported Report Banner | Capture green "Supported by available evidence" report header. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L138` | Screen 8: Claim Cards | Capture extracted claim cards for Reuters article. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L146` | Screen 9: Source Gauge | Capture circular credibility score gauge (72.9/100). |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L154` | Screen 10: Latency Chart | Capture Recharts horizontal bar chart in telemetry section. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L162` | Screen 11: Bleach Submission | Capture text area with bleach claim entered. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L170` | Screen 12: Contradicted Banner | Capture red "Contradicted by available evidence" header. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L178` | Screen 13: PolitiFact Debunk Card | Capture PolitiFact "Pants on Fire" fact-check card. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L186` | Screen 14: Pottery Claim Input | Capture input form with local pottery claim. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L194` | Screen 15: Insufficient Badge | Capture grey/amber "Insufficient evidence" report header. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L202` | Screen 16: Multimodal Alert | Capture image inspection card with context mismatch alert. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L210` | Screen 17: History Table | Capture paginated audit history table. |
| **`[SCREENSHOT NEEDED]`** | `06_project_demonstration.md:L218` | Screen 18: Methodology Page | Capture Methodology page showing the 8 decision rules. |

*Note on Empirical Results:* There are **zero** `[TO BE FILLED AFTER RUN]` or speculative `PROPOSED` placeholders. All evaluation metrics, latencies, accuracy scores, and test cases were verified through actual script runs.

---

## 3. Word Count and Page Volume Analysis

The table below details the exact word counts extracted from each chapter file and calculates the estimated printed page volume based on standard university formatting guidelines: **Times New Roman 12 pt, 1.15 line spacing, 1-inch margins** (averaging approximately **275 words per full page**, supplemented by figures, tables, code blocks, and diagrams).

| File Name | Chapter Title / Content | Exact Word Count | Estimated Page Count (Text + Visuals) |
| :--- | :--- | :--- | :--- |
| `00_front_matter.md` | Front Matter (Abstract, Abbreviations, Indices) | 1,447 words | ~5 – 6 pages |
| `01_introduction.md` | Chapter 1 – Introduction | 1,936 words | ~7 – 8 pages |
| `02_project_description_and_goals.md` | Chapter 2 – Project Description and Goals | 6,276 words | ~23 – 25 pages |
| `03_technical_specification.md` | Chapter 3 – Technical Specification | 3,078 words | ~11 – 13 pages |
| `04_design_approach_and_details.md` | Chapter 4 – Design Approach and Details | 3,877 words | ~16 – 18 pages (includes 11 diagrams) |
| `05_methodology_and_testing.md` | Chapter 5 – Methodology and Testing | 4,185 words | ~16 – 18 pages (includes 3 tables & code) |
| `06_project_demonstration.md` | Chapter 6 – Project Demonstration | 2,025 words | ~10 – 12 pages (includes 18 screenshot slots) |
| `07_result_and_discussion.md` | Chapter 7 – Result and Discussion | 2,161 words | ~9 – 11 pages (includes 3 chart scripts) |
| `08_conclusion.md` | Chapter 8 – Conclusion | 1,158 words | ~4 – 5 pages |
| `09_references.md` | Chapter 9 – References (27 IEEE Citations) | 928 words | ~3 – 4 pages |
| `A_appendix_code.md` | Appendix A – Sample Code Excerpts | 2,127 words | ~8 – 10 pages |
| `diagrams.md` | Consolidated Mermaid Diagram Source Code | 2,190 words | Reference Document |
| **TOTALS** | **Complete B.Tech Technical Report Package** | **31,388 words** | **~112 – 125 pages** |

### Compliance Assessment:
- **Minimum Page Requirement:** 70 pages
- **Estimated Report Length:** **~114 pages**
- **Word Target Minimum:** 18,000 – 22,000 words
- **Actual Word Count:** **31,388 words**
- **Compliance Status:** **FULL COMPLIANCE (Exceeds minimum depth criteria by 62.8%)**

---

## 4. Diagram Export and Rendering Instructions

All eleven architectural, data flow, sequence, and entity-relationship diagrams have been formatted using valid Mermaid syntax and consolidated into [`report_content/diagrams.md`](file:///Users/jathinaraveti/Desktop/final_year_proj/report_content/diagrams.md).

To render and export these diagrams as high-resolution images for your final Word/PDF report:
1. Open [`report_content/diagrams.md`](file:///Users/jathinaraveti/Desktop/final_year_proj/report_content/diagrams.md) in your editor.
2. Copy the Mermaid code block for any figure (e.g., Figure 4.1).
3. Navigate to [Mermaid Live Editor](https://mermaid.live/) in your web browser.
4. Paste the snippet into the editor window.
5. Click **Actions $\rightarrow$ Download PNG (or SVG)** to save a publication-quality image.
