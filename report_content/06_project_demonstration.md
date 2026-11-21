# CHAPTER 6 – PROJECT DEMONSTRATION

## 6.1 System Installation and Execution Guide

To replicate, deploy, and evaluate the VeritasAI verification platform from scratch, follow the step-by-step instructions below. The installation commands assume a modern POSIX-compliant operating system (Linux or macOS) with Python 3.11+ and Node.js v18+ installed.

---

### 6.1.1 Environment Setup and Dependency Installation

#### Step 1: Clone Repository and Navigate to Workspace
```bash
git clone <repository-url> final_year_proj
cd final_year_proj
```

#### Step 2: Configure Python Virtual Environment & Install Backend Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
```

#### Step 3: Install Frontend Node.js Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 4: Configure Environment Variables
Create a `.env` file in the project root containing your API credentials:
```bash
cat << 'EOF' > .env
# External API Credentials
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_FACT_CHECK_API_KEY=your_google_fact_check_api_key_here

# Backend Service Configuration
HOST=127.0.0.1
PORT=8000
ENVIRONMENT=development
DATABASE_URL=sqlite:///./fake_news.db
EOF

# Copy configuration into backend directory
cp .env backend/.env
```

---

### 6.1.2 Launching Operational Services

#### Step 5: Start the Asynchronous FastAPI Backend Daemon
```bash
source venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Verification:* The backend initializes database tables in `fake_news.db` and exposes interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

#### Step 6: Start the Frontend Vite Development Server
Open a secondary terminal session:
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
*Verification:* The frontend Vite development server launches at `http://127.0.0.1:5173/`.

---

## 6.2 Step-by-Step Screen Walkthrough

This section walks through the complete operational execution of VeritasAI, documenting user interactions, internal system behaviors, and capturing eighteen distinct operational screenshots.

---

### Screen 1: Backend Server Initialization & Database Setup
- **What the User Does:** The user executes the Uvicorn ASGI launch command in the terminal.
- **What the System Does:** Uvicorn spins up the FastAPI application process, imports service modules, resolves database models via SQLAlchemy, auto-creates the `analyses` table in `fake_news.db`, and binds to `http://127.0.0.1:8000`.

> `[SCREENSHOT NEEDED: Terminal output displaying Uvicorn startup logs, database schema initialization confirmation, and active listening status on port 8000. Command: source venv/bin/activate && PYTHONPATH=. uvicorn backend.app.main:app --host 127.0.0.1 --port 8000]`

---

### Screen 2: Interactive OpenAPI / Swagger Documentation
- **What the User Does:** The user navigates a web browser to `http://127.0.0.1:8000/docs`.
- **What the System Does:** FastAPI renders the interactive Swagger UI documenting all exposed REST endpoints: `/api/analyze`, `/api/claims/extract`, `/api/history`, `/api/health`, `/api/metrics`, and `/api/providers`.

> `[SCREENSHOT NEEDED: Browser view of the FastAPI interactive Swagger UI at http://127.0.0.1:8000/docs, showing expandable endpoint cards for POST /api/analyze and GET /api/history.]`

---

### Screen 3: Verification Dashboard Overview (Home View)
- **What the User Does:** The user navigates to `http://127.0.0.1:5173/`.
- **What the System Does:** React mounts the single-page application dashboard. The interface renders the top navigation bar, the real-time external provider health status bar, the dual input form (URL vs. raw text tabs), optional image upload drop-zone, and quick-testing preset scenario buttons.

> `[SCREENSHOT NEEDED: Full-page view of the VeritasAI home dashboard at http://127.0.0.1:5173/ displaying the dark-themed glassmorphism interface, submission form, and quick presets.]`

---

### Screen 4: Live Provider Health Status Bar
- **What the User Does:** The user views the top status bar on the dashboard.
- **What the System Does:** On page load, the frontend issues an asynchronous `GET /api/providers` request. The component displays real-time operational badges for Google Fact Check Tools API (`ACTIVE`), Google Gemini API (`ACTIVE`), GDELT Global News (`ACTIVE`), and Document Extractor (`ACTIVE`).

> `[SCREENSHOT NEEDED: Close-up capture of the ProviderStatusBar component across the top of the dashboard, showing green active badges for Gemini API, Fact Check API, and GDELT News.]`

---

### Screen 5: Quick-Testing Preset Selection
- **What the User Does:** The user clicks the preset button: *"Preset: WHO Declares End to COVID-19 Emergency"*.
- **What the System Does:** The frontend populates the URL input field with `https://www.reuters.com/business/healthcare-pharmaceuticals/who-end-covid-emergency-2023-05-05/` and sets the headline state without requiring manual typing.

> `[SCREENSHOT NEEDED: Dashboard input form populated automatically after clicking the Reuters COVID-19 preset button, showing the URL field populated and the active "Analyze Article" button.]`

---

### Screen 6: Live Pipeline Execution Progress Tracker
- **What the User Does:** The user clicks the *"Analyze Article"* button.
- **What the System Does:** The submission form transitions into an active execution state. The `ProgressIndicator` component animates through the sequential verification stages: (1) Validating URL & SSRF security, (2) Extracting clean prose, (3) Extracting atomic claims, (4) Querying Google Fact Check & GDELT, (5) Evaluating source credibility, and (6) Synthesizing epistemic fusion verdict.

> `[SCREENSHOT NEEDED: The animated ProgressIndicator component showing active step spinners and completed checkmarks as the backend processes the live Reuters verification request.]`

---

### Screen 7: Verification Report Overview (Scenario A – Supported News Story)
- **What the User Does:** The user reviews the completed verification report for the Reuters submission.
- **What the System Does:** The frontend renders `ReportPage.tsx`. The top hero banner displays a green badge: `Supported by available evidence` with `Uncertainty: Moderate`, accompanied by the explanation: *"Published by accredited news outlet 'reuters.com' (Credibility Score: 72.9/100) with clear editorial attribution. No contradicting fact-check reviews or conflicting reports were identified."*

> `[SCREENSHOT NEEDED: Hero section of the verification report for the Reuters COVID-19 article, displaying the green "Supported by available evidence" badge, headline, and executive summary.]`

---

### Screen 8: Granular Claim-by-Claim Evidentiary Breakdown Cards
- **What the User Does:** The user scrolls down to the *"Factual Claims Extracted & Verified"* section.
- **What the System Does:** The system renders individual cards for each isolated claim. Claim 1 displays: *"WHO declares end to COVID-19 as a global health emergency"*, categorized under Health, with named entities `[WHO, COVID]`. The card indicates that no refuting fact-checks were linked, confirming that unrelated WHO conspiracy debunks were successfully filtered out by the stop-word suppression engine.

> `[SCREENSHOT NEEDED: Detailed view of the extracted claims list in the report, showing Claim 1 and Claim 2 cards, named entity tags, and verification status badges.]`

---

### Screen 9: Source Credibility Gauge & Factor Distribution
- **What the User Does:** The user inspects the *"Source Credibility Assessment"* panel on the right side of the report.
- **What the System Does:** The component displays an overall credibility score gauge of **72.9 / 100** (`Assessed`) for `reuters.com`. Below the gauge, an expandable factor breakdown details: Domain Track Record (96.0 / 100, Weight 40%), TLD & Registration Integrity (85.0 / 100, Weight 25%), Author Attribution (40.0 / 100, Unobserved), and Publisher Transparency (35.0 / 100, Unobserved).

> `[SCREENSHOT NEEDED: Source Credibility panel showing the circular gauge at 72.9/100 for reuters.com, alongside the four weighted factor progress bars.]`

---

### Screen 10: Real-Time Execution Latency Profiling (Recharts Visualization)
- **What the User Does:** The user scrolls to the *"Performance & Telemetry"* card at the bottom of the report.
- **What the System Does:** The platform renders an interactive Recharts horizontal bar chart visualizing the millisecond latency breakdown across stages: Article Extraction (129.7 ms), Text Model (0.6 ms), Claim Extraction (5,086.0 ms), Evidence Retrieval (12,586.9 ms), Claim Matching (0.7 ms), and Decision Fusion (0.03 ms), totaling 17,804.3 ms.

> `[SCREENSHOT NEEDED: Performance & Telemetry section displaying the Recharts horizontal latency bar chart showing execution times across all pipeline stages.]`

---

### Screen 11: Submitting a Contradicted Claim (Scenario B – Bleach Ingestion)
- **What the User Does:** The user navigates back to the dashboard, selects the *"Text Input"* tab, and clicks *"Preset: Bleach Coronavirus Cure"*.
- **What the System Does:** The text area is populated with: *"Drinking bleach cures coronavirus infections and kills all viral pathogens."* No URL is provided.

> `[SCREENSHOT NEEDED: Dashboard text input tab showing the bleach claim entered into the textarea, with the source URL field left empty.]`

---

### Screen 12: Contradicted Verification Report & Authoritative Debunk Cards
- **What the User Does:** The user clicks *"Analyze Submission"* and inspects the resulting report.
- **What the System Does:** The hero banner displays a bold red badge: `Contradicted by available evidence` with `Uncertainty: Low`. Rule 1 triggers: *"Rule 1 (Authoritative Fact-Check Refutation): 1 published fact-check review(s) rated the statement false or misleading."*

> `[SCREENSHOT NEEDED: Red "Contradicted by available evidence" report header for the bleach claim, displaying the Low uncertainty rating and Rule 1 explanation.]`

---

### Screen 13: PolitiFact Debunk Evidence Review Card
- **What the User Does:** The user scrolls to the *"Authoritative Fact-Check Reviews"* section.
- **What the System Does:** The system displays a verified fact-check card from PolitiFact: *"Says drinking a bleach solution will prevent you from getting the coronavirus."* The badge displays the verbatim publisher rating: **Pants on Fire** (Normalized: `FALSE`), accompanied by an external link to `politifact.com`.

> `[SCREENSHOT NEEDED: External fact-check evidence card showing the PolitiFact review, "Pants on Fire" flame icon badge, and claim review metadata.]`

---

### Screen 14: Submitting an Unevidenced Assertion (Scenario C – Local Pottery)
- **What the User Does:** The user selects the text input tab and inputs: *"Oakridge community pottery workshop wins county artisan prize"*.
- **What the System Does:** The user submits the assertion. The backend searches Google Fact Check and GDELT, retrieving zero matching debunks and zero corroborating global news stories.

> `[SCREENSHOT NEEDED: Dashboard showing submission of the localized, unevidenced pottery workshop assertion.]`

---

### Screen 15: Insufficient Evidence Report & Epistemic Uncertainty Badge
- **What the User Does:** The user examines the resulting verification report for the pottery assertion.
- **What the System Does:** The hero banner renders a grey/amber badge: `Insufficient evidence` with `Uncertainty: High`. The narrative explicitly states: *"No matching published fact-check reviews or authoritative independent news reports were retrieved. The absence of evidence does not establish whether the assertion is true or false."*

> `[SCREENSHOT NEEDED: Verification report header displaying the "Insufficient evidence" badge, High uncertainty indicator, and mandatory epistemic humility disclaimer.]`

---

### Screen 16: Multimodal Image Attachment & Context Mismatch Detection
- **What the User Does:** The user enters the claim: *"Explosion causes massive midnight blackout across downtown"* and uploads a bright, sunlit daytime city photograph.
- **What the System Does:** The `ImageAnalyzer` computes an average luminance $L_{\text{mean}} = 165.2$ and detects daytime color temperatures. The system raises the flag `POTENTIAL_CONTEXT_MISMATCH`. Rule 4 triggers, returning `Misleading or missing context` (Uncertainty: Moderate), warning the user of potential image miscontextualization.

> `[SCREENSHOT NEEDED: Multimodal inspection card displaying the uploaded image thumbnail, luminance score (165.2), and the amber "POTENTIAL_CONTEXT_MISMATCH" alert banner.]`

---

### Screen 17: Paginated Verification Audit History Table
- **What the User Does:** The user clicks the *"History"* link in the navigation header.
- **What the System Does:** The frontend fetches `GET /api/history?page=1&limit=10`. The `HistoryPage` renders a clean, paginated data table showing all past analyses, displaying timestamp, headline, publishing domain, verdict badge, source score, total latency, and interactive "View" and "Delete" action buttons.

> `[SCREENSHOT NEEDED: HistoryPage table showing multiple past verification runs (Reuters, Bleach, Pottery) with status badges, latency figures, and delete buttons.]`

---

### Screen 18: Interactive Methodology Guide & Epistemic Rule Reference
- **What the User Does:** The user clicks *"Methodology"* in the navigation bar.
- **What the System Does:** The frontend renders `MethodologyPage.tsx`. The page presents an educational guide explaining the eight-tier epistemic decision hierarchy, the mathematical formula for source credibility, and the technical limitations of automated fact-checking.

> `[SCREENSHOT NEEDED: MethodologyPage view displaying the eight decision fusion rules, source credibility weighting formula, and system limitations guide.]`

---

## 6.3 Commands to Reproduce Verification Scenarios

To execute the verification scenarios and capture the exact outputs documented above, run the automated audit script:

```bash
# Execute complete automated three-article audit suite
source venv/bin/activate
PYTHONPATH=. python3 scripts/audit_three_articles.py
```

To run individual scenarios via `curl` against the live backend:

```bash
# Scenario A: Live Reuters Article Verification
curl -s -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "accept: application/json" \
  -F "url=https://www.reuters.com/business/healthcare-pharmaceuticals/who-end-covid-emergency-2023-05-05/" \
  | python3 -m json.tool

# Scenario B: Contradicted Bleach Ingestion Claim
curl -s -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "accept: application/json" \
  -F "text=Drinking bleach cures coronavirus infections and kills all viral pathogens." \
  | python3 -m json.tool

# Scenario C: Insufficient Evidence Claim
curl -s -X POST "http://127.0.0.1:8000/api/analyze" \
  -H "accept: application/json" \
  -F "text=Oakridge community pottery workshop wins county artisan prize" \
  | python3 -m json.tool
```
