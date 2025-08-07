import requests
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
client = OpenAI() # Automatically uses OPENAI_API_KEY from environment

def diagnose_missing_url(url: str, reason: str) -> str:
    try:
        reachable = is_url_accessible(url)
        reachability_note = "It is reachable." if reachable else "It appears to be inaccessible."

        prompt = f"""
A log analysis system flagged this URL as missing:

URL: {url}
Error/Reason: {reason}

{reachability_note}

Based on the reason, URL format, and accessibility, explain why this title might be missing and whether the URL looks valid. Reply in one sentence.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        except Exception as e:
            # Try fallback model if gpt-4 fails
            print(f"[AI WARNING] gpt-4 failed: {e} – trying gpt-3.5-turbo")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[AI ERROR] diagnose_missing_url failed: {e}")
        return "AI analysis unavailable"


def is_url_accessible(url: str) -> bool:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        print(f"[CHECK ERROR] Failed to access URL {url}: {e}")
        return False

def style_missing_entries(df):
    # Precompute URL accessibility
    df["url_accessible"] = df["url"].apply(lambda url: is_url_accessible(url) if pd.notna(url) else False)
    def highlight_row(row):
        if row.get("ai_reason") and "not" in row.get("ai_reason", "").lower() and row.get("url_accessible"):
            return ["background-color: salmon"] * len(row)
        else:
            return ["background-color: lightgreen"] * len(row)

    return df.style.apply(highlight_row, axis=1)
