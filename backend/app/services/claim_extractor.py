import time
import json
import re
import httpx
from typing import List, Dict, Any, Optional
from backend.app.api.schemas.claims import ExtractedClaim
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.utils.text_processing import (
    split_into_sentences,
    extract_named_entities_heuristic,
    extract_dates_heuristic
)

class ClaimExtractor:
    """
    Factual Claim Extraction Service:
    - Uses Google Gemini API when configured for contextual claim identification.
    - Features a resilient local heuristic NLP fallback when API keys are not present.
    - Validates all extracted claims against Pydantic schema.
    """
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""

    async def extract_claims(self, text: str, headline: Optional[str] = None) -> List[ExtractedClaim]:
        if not text and not headline:
            return []

        # Attempt Gemini LLM extraction first if configured
        if self.gemini_key:
            try:
                llm_claims = await self._extract_with_gemini(text, headline)
                if llm_claims:
                    logger.info(f"Successfully extracted {len(llm_claims)} claims using Gemini API")
                    return llm_claims
            except Exception as e:
                logger.warning(f"Gemini claim extraction failed: {str(e)}. Falling back to local NLP extractor.")

        # Fallback to local heuristic extractor
        return self._extract_with_local_nlp(text, headline)

    async def _extract_with_gemini(self, text: str, headline: Optional[str] = None) -> List[ExtractedClaim]:
        """Calls Gemini API using standard REST endpoint with JSON schema prompt."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        
        prompt = f"""
You are a factual claim extraction system for a real-time fake news detector.
Analyze the following news text and extract up to 5 discrete, checkable factual claims.
Do not extract opinions, predictions, or subjective claims. Focus on verifiable factual assertions.

Headline: {headline or 'N/A'}
Article Text:
{text[:4000]}

Respond ONLY with a valid JSON array of objects with the following schema:
[
  {{
    "claim_id": "c1",
    "claim_text": "Exact checkable factual statement",
    "importance": "HIGH" or "MEDIUM" or "LOW",
    "category": "Politics" or "Science" or "Health" or "Economy" or "International" or "General",
    "named_entities": ["Entity1", "Entity2"],
    "relevant_dates": ["2024", "October 2023"],
    "relevant_locations": ["City", "Country"],
    "search_queries": ["Search query 1 for fact check", "Search query 2 for news search"]
  }}
]
"""
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }
        
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise Exception(f"Gemini HTTP {resp.status_code}: {resp.text[:200]}")
                
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise Exception("No candidates returned from Gemini API")
                
            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            parsed_json = json.loads(raw_text)
            
            validated_claims = []
            for idx, item in enumerate(parsed_json):
                cid = item.get("claim_id") or f"c{idx+1}"
                claim = ExtractedClaim(
                    claim_id=cid,
                    claim_text=item.get("claim_text", "").strip(),
                    importance=item.get("importance", "MEDIUM").upper(),
                    category=item.get("category", "General"),
                    named_entities=item.get("named_entities", []),
                    relevant_dates=item.get("relevant_dates", []),
                    relevant_locations=item.get("relevant_locations", []),
                    search_queries=item.get("search_queries", [item.get("claim_text", "")]),
                    verification_status="UNVERIFIED"
                )
                if claim.claim_text:
                    validated_claims.append(claim)
                    
            return validated_claims

    def _extract_with_local_nlp(self, text: str, headline: Optional[str] = None) -> List[ExtractedClaim]:
        """
        Rule-based NLP factual claim extractor:
        - Prioritizes headline assertion if available.
        - Identifies sentences containing quantitative data, named entities, or definitive action verbs.
        - Generates search queries optimized for fact-checking engines.
        """
        claims: List[ExtractedClaim] = []
        counter = 1
        
        # 1. Headline claim (almost always primary claim in news)
        if headline and len(headline.strip()) > 15:
            entities = extract_named_entities_heuristic(headline)
            dates = extract_dates_heuristic(headline)
            search_query = self._build_search_query(headline, entities)
            
            claims.append(ExtractedClaim(
                claim_id=f"c{counter}",
                claim_text=headline.strip(),
                importance="HIGH",
                category=self._categorize_claim(headline),
                named_entities=entities,
                relevant_dates=dates,
                relevant_locations=[],
                search_queries=[search_query, headline.strip()],
                verification_status="UNVERIFIED"
            ))
            counter += 1

        # 2. Extract key sentences from body text
        sentences = split_into_sentences(text or "")
        
        # Scoring sentences for checkability
        candidate_sentences = []
        for s in sentences:
            # Check for numbers, percentages, currency, or definitive verbs
            has_numbers = bool(re.search(r'\b\d+(?:,\d+)*(?:\.\d+)?%?|\$\d+\b', s))
            has_entities = len(extract_named_entities_heuristic(s)) > 0
            has_assertion_verbs = bool(re.search(r'\b(?:announced|banned|confirmed|discovered|killed|passed|signed|voted|stole|arrested|tested|caused|admitted)\b', s, re.I))
            
            # Avoid questions and pure opinion sentences
            if s.endswith("?") or re.search(r'\b(?:i think|in my opinion|we believe|it seems)\b', s, re.I):
                continue
                
            score = 0
            if has_numbers: score += 2
            if has_entities: score += 2
            if has_assertion_verbs: score += 2
            
            if score >= 3:
                candidate_sentences.append((score, s))
                
        candidate_sentences.sort(key=lambda x: x[0], reverse=True)
        
        for _, s in candidate_sentences[:4]:
            # Deduplicate against existing headline claim
            if headline and headline.lower() in s.lower():
                continue
            if any(s.lower() in c.claim_text.lower() or c.claim_text.lower() in s.lower() for c in claims):
                continue
                
            entities = extract_named_entities_heuristic(s)
            dates = extract_dates_heuristic(s)
            search_query = self._build_search_query(s, entities)
            
            claims.append(ExtractedClaim(
                claim_id=f"c{counter}",
                claim_text=s,
                importance="MEDIUM" if counter > 1 else "HIGH",
                category=self._categorize_claim(s),
                named_entities=entities,
                relevant_dates=dates,
                relevant_locations=[],
                search_queries=[search_query],
                verification_status="UNVERIFIED"
            ))
            counter += 1
            if len(claims) >= 5:
                break

        # Fallback if no specific assertion detected
        if not claims and text:
            first_sentence = (sentences[0] if sentences else text[:200]).strip()
            if first_sentence:
                claims.append(ExtractedClaim(
                    claim_id="c1",
                    claim_text=first_sentence,
                    importance="MEDIUM",
                    category="General",
                    named_entities=extract_named_entities_heuristic(first_sentence),
                    relevant_dates=[],
                    relevant_locations=[],
                    search_queries=[first_sentence],
                    verification_status="UNVERIFIED"
                ))

        return claims

    def _categorize_claim(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ("vaccine", "virus", "cancer", "health", "hospital", "doctor", "fda", "disease", "treatment", "malaria", "pandemic")):
            return "Health"
        if any(w in text_lower for w in ("president", "senate", "congress", "vote", "election", "biden", "trump", "minister", "parliament", "legislation")):
            return "Politics"
        if any(w in text_lower for w in ("climate", "nasa", "space", "study", "planet", "scientist", "physics", "dna")):
            return "Science"
        if any(w in text_lower for w in ("inflation", "gdp", "market", "economy", "bank", "interest rate", "dollars", "stock")):
            return "Economy"
        if any(w in text_lower for w in ("war", "treaty", "nato", "ukraine", "russia", "china", "un", "diplomacy")):
            return "International"
        return "General"

    def _build_search_query(self, text: str, entities: List[str]) -> str:
        """Constructs concise 4-7 word search query for fact-checking APIs."""
        if entities:
            query = " ".join(entities[:3])
            # Add key assertion words
            action_words = re.findall(r'\b[a-zA-Z]{5,}\b', text)
            for w in action_words:
                if w.lower() not in [e.lower() for e in entities] and len(query.split()) < 7:
                    query += f" {w}"
            return query.strip()
        
        words = [w for w in text.split() if len(w) > 3][:6]
        return " ".join(words)
