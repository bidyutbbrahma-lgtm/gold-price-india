# gold_api_daily.py
import requests
from datetime import datetime
import subprocess
import os

API_KEY = "goldapi-h5rolsmkzhkcgw-io"
URL = "https://www.goldapi.io/api/XAU/INR"
OUNCE_TO_GRAM = 31.1035

FAQ_SCHEMA = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is today's gold price in India?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Today's gold price in India is derived from international gold markets and converted into Indian Rupees. This page shows gold prices per ounce, per gram, and per 10 grams."
      }
    },
    {
      "@type": "Question",
      "name": "Why does gold price change daily?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Gold prices change daily due to global demand, currency movements, interest rates, inflation expectations, and geopolitical events."
      }
    }
  ]
}
</script>
"""

def fetch_gold_price():
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }
    res = requests.get(URL, headers=headers)
    res.raise_for_status()
    data = res.json()
    return data["price"], data["high_price"], data["low_price"]

def generate_html(price, high, low):
    price_g = round(price / OUNCE_TO_GRAM, 2)
    high_g = round(high / OUNCE_TO_GRAM, 2)
    low_g = round(low / OUNCE_TO_GRAM, 2)

    price_10g = round(price_g * 10, 2)
    high_10g = round(high_g * 10, 2)
    low_10g = round(low_g * 10, 2)

    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{TITLE}}", "Gold Price in India Today – Per Gram & 10g")
    html = html.replace("{{META_DESCRIPTION}}",
                        "Check today's gold price in India. View gold rates per ounce, per gram, and per 10 grams updated daily.")
    html = html.replace("{{LAST_UPDATED}}", now)

    html = html.replace("{{PRICE_OUNCE}}", str(price))
    html = html.replace("{{HIGH_OUNCE}}", str(high))
    html = html.replace("{{LOW_OUNCE}}", str(low))

    html = html.replace("{{PRICE_GRAM}}", str(price_g))
    html = html.replace("{{HIGH_GRAM}}", str(high_g))
    html = html.replace("{{LOW_GRAM}}", str(low_g))

    html = html.replace("{{PRICE_10G}}", str(price_10g))
    html = html.replace("{{HIGH_10G}}", str(high_10g))
    html = html.replace("{{LOW_10G}}", str(low_10g))

    html = html.replace("{{FAQ_SCHEMA}}", FAQ_SCHEMA)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def git_push():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Auto daily update"], check=True)
    subprocess.run(["git", "push"], check=True)

if __name__ == "__main__":
    price, high, low = fetch_gold_price()
    generate_html(price, high, low)
    git_push()
