import re
from typing import Optional, List, Dict, Any
from backend.app.api.schemas.evidence import SourceCredibilityReport, CredibilityFactor
from backend.app.utils.url_validation import extract_domain

class SourceCredibilityAnalyzer:
    """
    Transparent Source Credibility Assessment Service:
    - Analyzes observed domain characteristics, institutional indicators, and journalistic track record.
    - Computes factor-weighted heuristic scores (0 to 100).
    - Labels status: Assessed, Partially assessed, Insufficient source information, Assessment unavailable.
    - Discloses limitations and factor weights explicitly.
    """
    # High-credibility journalistic, public service, and scientific institutions
    REPUTABLE_DOMAINS = {
        "reuters.com": 96.0,
        "apnews.com": 96.0,
        "bbc.com": 94.0,
        "bbc.co.uk": 94.0,
        "nytimes.com": 90.0,
        "washingtonpost.com": 90.0,
        "theguardian.com": 90.0,
        "nature.com": 98.0,
        "science.org": 98.0,
        "who.int": 96.0,
        "cdc.gov": 96.0,
        "nih.gov": 97.0,
        "npr.org": 92.0,
        "pbs.org": 92.0,
        "bloomberg.com": 92.0,
        "wsj.com": 92.0,
        "afp.com": 95.0,
        "dw.com": 91.0,
        "lemonde.fr": 90.0,
        "snopes.com": 93.0,
        "politifact.com": 93.0,
        "factcheck.org": 94.0
    }

    # Documented satire or known conspiracy domains
    FLAGGED_DOMAINS = {
        "theonion.com": 15.0, # Satire
        "babylonbee.com": 15.0, # Satire
        "newsthump.com": 15.0, # Satire
        "infowars.com": 10.0, # Conspiracy
        "naturalnews.com": 12.0, # Discredited medical claims
        "worldnewsdailyreport.com": 10.0 # Fabricated stories
    }

    def assess(self, url: Optional[str], publisher_name: Optional[str] = None, author: Optional[str] = None) -> SourceCredibilityReport:
        if not url:
            return SourceCredibilityReport(
                domain=None,
                publisher_name=publisher_name or "Unspecified Source",
                overall_score=None,
                assessment_status="Assessment unavailable",
                factors=[],
                missing_signals=[
                    "No source URL provided",
                    "Domain registration and reputation cannot be evaluated",
                    "Publisher attribution relies on self-reported input"
                ]
            )

        domain = extract_domain(url)
        if not domain:
            return SourceCredibilityReport(
                domain=None,
                publisher_name=publisher_name,
                overall_score=None,
                assessment_status="Insufficient source information",
                factors=[],
                missing_signals=["Invalid or unparseable source domain."]
            )

        factors: List[CredibilityFactor] = []
        missing_signals: List[str] = []

        # 1. Domain Track Record Factor (Weight: 40%)
        if domain in self.REPUTABLE_DOMAINS:
            track_score = self.REPUTABLE_DOMAINS[domain]
            factors.append(CredibilityFactor(
                factor_name="Domain Track Record",
                score=track_score,
                weight=0.40,
                description=f"Domain '{domain}' has an established record with recognized editorial oversight or fact-checking accreditations.",
                status="Observed"
            ))
        elif domain in self.FLAGGED_DOMAINS:
            track_score = self.FLAGGED_DOMAINS[domain]
            factors.append(CredibilityFactor(
                factor_name="Domain Track Record",
                score=track_score,
                weight=0.40,
                description=f"Domain '{domain}' is documented as satire, parody, or disputed conspiratorial outlet.",
                status="Observed"
            ))
        else:
            track_score = 50.0 # Neutral baseline for unknown independent domains
            factors.append(CredibilityFactor(
                factor_name="Domain Track Record",
                score=track_score,
                weight=0.40,
                description=f"Domain '{domain}' does not appear in major curated fact-checking registries. Evaluated as unindexed independent publisher.",
                status="Partially observed"
            ))
            missing_signals.append("Domain track record unverified in accredited registries")

        # 2. Institutional TLD & Domain Integrity Factor (Weight: 25%)
        tld_score = 50.0
        if domain.endswith(".gov") or domain.endswith(".mil"):
            tld_score = 95.0
            desc = "Official government or military institutional top-level domain (.gov / .mil)."
        elif domain.endswith(".edu") or domain.endswith(".ac.uk"):
            tld_score = 92.0
            desc = "Accredited educational / academic research institutional domain."
        elif domain.endswith(".org"):
            tld_score = 65.0
            desc = "Non-profit or organizational top-level domain (.org). Requires independent corroboration."
        elif any(domain.endswith(t) for t in (".xyz", ".top", ".biz", ".click", ".buzz", ".info")):
            tld_score = 25.0
            desc = "Low-reputation generic top-level domain frequently utilized in transient spam or deceptive campaigns."
        elif domain in self.REPUTABLE_DOMAINS:
            tld_score = 85.0
            desc = "Verified high-integrity domain registration for major recognized news organization."
        else:
            tld_score = 60.0
            desc = "Standard commercial or country-code top-level domain (.com, .net, etc.)."

        # Check for deceptive clone typos (e.g. "cnn-world.com", "bbc-daily.org")
        if re.search(r'(?:cnn|bbc|reuters|nytimes|foxnews|theguardian)-', domain):
            tld_score = max(10.0, tld_score - 40.0)
            desc += " WARNING: Pattern resembles domain-impersonation / deceptive branding."
            missing_signals.append("Possible domain-squatting or brand impersonation detected")

        factors.append(CredibilityFactor(
            factor_name="Domain Integrity & TLD",
            score=tld_score,
            weight=0.25,
            description=desc,
            status="Observed"
        ))

        # 3. Editorial & Author Attribution Transparency (Weight: 20%)
        if author and len(author.strip()) > 3:
            factors.append(CredibilityFactor(
                factor_name="Author Attribution",
                score=85.0,
                weight=0.20,
                description=f"Article specifies clear author byline: '{author}'.",
                status="Observed"
            ))
        else:
            factors.append(CredibilityFactor(
                factor_name="Author Attribution",
                score=40.0,
                weight=0.20,
                description="No specific author byline detected in extracted metadata.",
                status="Unobserved"
            ))
            missing_signals.append("Missing explicit author attribution / byline")

        # 4. Publisher Identification (Weight: 15%)
        if publisher_name and publisher_name.lower() != "unknown publisher":
            factors.append(CredibilityFactor(
                factor_name="Publisher Transparency",
                score=75.0,
                weight=0.15,
                description=f"Publisher clearly identifies as '{publisher_name}'.",
                status="Observed"
            ))
        else:
            factors.append(CredibilityFactor(
                factor_name="Publisher Transparency",
                score=35.0,
                weight=0.15,
                description="Publisher identity could not be verified from page metadata.",
                status="Unobserved"
            ))
            missing_signals.append("Missing clear publisher identification")

        # Compute weighted score
        overall = sum(f.score * f.weight for f in factors)
        if domain in self.FLAGGED_DOMAINS:
            # Satire and conspiracy domains cannot exceed low risk threshold
            overall = min(overall, self.FLAGGED_DOMAINS[domain] + 10.0)
        overall_score = round(overall, 1)

        # Determine status
        if domain in self.REPUTABLE_DOMAINS or domain in self.FLAGGED_DOMAINS:
            status = "Assessed"
        elif len(missing_signals) <= 1:
            status = "Partially assessed"
        else:
            status = "Insufficient source information"

        return SourceCredibilityReport(
            domain=domain,
            publisher_name=publisher_name or domain.capitalize(),
            overall_score=overall_score,
            assessment_status=status,
            factors=factors,
            missing_signals=missing_signals
        )
