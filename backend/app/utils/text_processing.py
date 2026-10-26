import re
import string
from typing import List, Tuple, Set
from collections import Counter
import math

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves"
}

def clean_text(text: str) -> str:
    """Removes irregular whitespace, non-printable characters, and HTML artefacts."""
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize_words(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words."""
    cleaned = text.lower()
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    return [word for word in cleaned.split() if word and word not in STOPWORDS]

def split_into_sentences(text: str) -> List[str]:
    """Splits body text into individual coherent sentences."""
    if not text:
        return []
    # Match sentence boundaries (period, question mark, exclamation mark followed by space or uppercase)
    raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 15]
    return sentences

def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """Computes cosine similarity between two texts using term frequency."""
    tokens1 = tokenize_words(text1)
    tokens2 = tokenize_words(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    
    sum1 = sum(v ** 2 for v in vec1.values())
    sum2 = sum(v ** 2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator / denominator)

def extract_named_entities_heuristic(text: str) -> List[str]:
    """
    Extracts potential named entities (capitalized phrases, acronyms, known patterns)
    without requiring heavyweight SpaCy model downloads.
    """
    entities = set()
    
    # Capitalized multi-word phrases (e.g. "World Health Organization", "Donald Trump", "United States")
    capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
    for p in capitalized_phrases:
        if len(p.split()) <= 4:
            entities.add(p)
            
    # All-caps acronyms (e.g. "WHO", "CDC", "FBI", "NASA", "EU")
    acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
    for a in acronyms:
        if a not in ("AND", "THE", "FOR", "NOT", "USA"):
            entities.add(a)
            
    return sorted(list(entities))[:8]

def extract_dates_heuristic(text: str) -> List[str]:
    """Extracts explicit date strings."""
    date_patterns = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
        r'\b(?:19|20)\d{2}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    dates = set()
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            dates.add(m)
    return sorted(list(dates))[:5]
