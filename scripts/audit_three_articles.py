"""
Audit Script: Testing Three Real Articles through /api/analyze
Tests:
Article A: Corroborated factual news story
Article B: Debunked claim with published fact-checks
Article C: Obscure claim with insufficient external evidence
"""
import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

ARTICLES = [
    {
        "type": "Article A (Supported Factual Claim)",
        "headline": "WHO declares end to COVID-19 as a global health emergency",
        "article_text": "The World Health Organization said Friday that Covid-19 no longer qualifies as a global health emergency, a major step toward the end of the pandemic that has killed more than 6.9 million people.",
        "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/who-end-covid-emergency-2023-05-05/"
    },
    {
        "type": "Article B (Contradicted Claim with Published Fact-Checks)",
        "headline": "Drinking bleach cures coronavirus infections",
        "article_text": "Social media posts claim drinking household disinfectant or chlorine solution cures coronavirus and kills all viral pathogens.",
        "url": None
    },
    {
        "type": "Article C (Claim with Insufficient Evidence)",
        "headline": "Oakridge community pottery workshop wins county artisan prize",
        "article_text": "The local pottery workshop on 4th street was awarded a ribbon at the annual county arts gathering according to the neighborhood newsletter.",
        "url": None
    }
]

def run_audit():
    print("===================================================================")
    print("TASK 3 AUDIT: Testing Three Distinct Real-World Article Scenarios")
    print("===================================================================\n")

    results = []

    for idx, art in enumerate(ARTICLES):
        print(f"\n[{idx+1}/3] Running Test for: {art['type']}")
        print(f"Headline: {art['headline']}")
        if art['url']:
            print(f"URL: {art['url']}")

        t0 = time.time()
        data = {
            "headline": art["headline"],
            "article_text": art["article_text"]
        }
        if art["url"]:
            data["url"] = art["url"]

        try:
            resp = httpx.post(f"{BASE_URL}/analyze", data=data, timeout=30.0)
            elapsed = (time.time() - t0) * 1000.0

            if resp.status_code != 200:
                print(f"Error {resp.status_code}: {resp.text}")
                continue

            payload = resp.json()
            print(f"-> Status Code: {resp.status_code}")
            print(f"-> Final Assessment: {payload['final_assessment']}")
            print(f"-> Uncertainty: {payload['uncertainty_level']}")
            print(f"-> Fact-Checks Retrieved: {len(payload['fact_checks'])}")
            print(f"-> News Articles Retrieved: {len(payload['news_articles'])}")
            print(f"-> Source Credibility Score: {payload['source_credibility']['overall_score']} ({payload['source_credibility']['assessment_status']})")
            print(f"-> AI Text Prediction: {payload['text_analysis']['prediction']} (Confidence: {payload['text_analysis']['confidence']})")
            print(f"-> Rules Applied: {payload['decision_fusion']['decision_rules_applied']}")
            print(f"-> Total Latency: {payload['total_latency_ms']} ms")

            results.append({
                "scenario": art["type"],
                "headline": art["headline"],
                "url": art["url"],
                "response": payload,
                "client_measured_latency_ms": round(elapsed, 2)
            })

        except Exception as e:
            print(f"Exception during request: {str(e)}")

    with open("audit_three_articles_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n===================================================================")
    print("Audit execution complete. Full results saved to audit_three_articles_results.json")
    print("===================================================================")

if __name__ == "__main__":
    run_audit()
