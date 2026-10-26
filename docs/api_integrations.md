# VeritasAI External API Integrations

## Overview of External Services

| Service | Protocol | Key Required? | Purpose | Fallback / Failure Mode |
| :--- | :--- | :--- | :--- | :--- |
| **Google Fact Check Tools API** | REST HTTPS | Optional (Recommended) | Retrieves schema.org ClaimReview fact-checks | Graceful empty result with explanation |
| **GDELT 2.0 DOC API** | REST HTTPS | No (Public) | Live global news search and reporting stance | Preserves completed pipeline results |
| **Google Gemini API** | REST HTTPS | Optional | Structured claim extraction & reasoning | Fallback to internal heuristic NLP extractor |

---

## 1. Google Fact Check Tools API

- **Official Documentation**: [https://developers.google.com/fact-check/tools/api](https://developers.google.com/fact-check/tools/api)
- **Endpoint**: `https://factchecktools.googleapis.com/v1alpha1/claims:search`
- **Method**: `GET`
- **Authentication**: Query parameter `key=<GOOGLE_FACT_CHECK_API_KEY>`
- **Request Parameters**:
  - `query`: The search term or claim text.
  - `languageCode`: Language filter (default: `en`).
  - `pageSize`: Number of results (default: `5`).
- **Response Handling**:
  - Preserves original publisher rating (`textualRating`) verbatim.
  - Maps to normalized indicators (`FALSE`, `TRUE`, `MIXED`, `UNPROVEN`) for decision fusion without overwriting publisher text.
  - Failure handling: Gracefully handles 403 (invalid key), 429 (rate limits), and timeouts by logging the event and returning an empty list.

---

## 2. GDELT Project 2.0 DOC API

- **Official Website**: [https://www.gdeltproject.org/](https://www.gdeltproject.org/)
- **Endpoint**: `https://api.gdeltproject.org/api/v2/doc/doc`
- **Method**: `GET`
- **Authentication**: None required (completely open public API).
- **Request Parameters**:
  - `query`: Keyword query string.
  - `mode`: `artlist` (article list).
  - `maxrecords`: `10` (bounded to max 20).
  - `format`: `json`.
  - `sort`: `DateDesc`.
- **Deduplication Strategy**:
  - GDELT indexes syndicated wire stories across hundreds of local publications. VeritasAI applies pairwise title cosine similarity ($> 0.85$ threshold) to flag syndicated reprints and prevent single-source reports from inflating independent corroboration counts.

---

## 3. Google Gemini API

- **Official Documentation**: [https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
- **Method**: `POST`
- **Authentication**: Query parameter `key=<GEMINI_API_KEY>`
- **Payload Schema**:
  - Enforces `response_mime_type: "application/json"`.
  - Validates output against Pydantic schema for `ExtractedClaim`.
- **Resilient Fallback**:
  - If `GEMINI_API_KEY` is not provided or the request fails, VeritasAI seamlessly activates the local rule-based NLP claim extractor without interrupting analysis.
