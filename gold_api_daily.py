import requests
import csv
import os
import subprocess
from datetime import datetime

# =====================================================
# FAQ SCHEMA (JSON-LD) — SAFE, NOT AN F-STRING
# =====================================================

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
        "text": "Today's gold price in India depends on international gold rates, USD-INR exchange rate, and local demand. This page shows the latest updated gold price in India for 24K and 22K gold."
      }
    },
    {
      "@type": "Question",
      "name": "Is gold price the same across all cities in India?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Gold prices are largely similar across India, but small differences may occur due to local taxes, transport costs, and jeweller margins."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between 24K and 22K gold?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "24K gold is pure gold and mainly used for investment, while 22K gold is commonly used for jewellery."
      }
    },
    {
      "@type": "Question",
      "name": "How often does the gold price change in India?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Gold prices in India change daily based on international market movements."
      }
    },
    {
      "@type": "Question",
      "name": "Is gold a good investment in India?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Gold is considered a long-term store of value and a hedge against inflation."
      }
    }
  ]
}
</script>
"""

# =====================================================
# CONFIG
# =====================================================

API_KEY = "goldapi-h5rolsmkzhkcgw-io"   # move to env later
SYMBOL = "XAU"
CURRENCY = "INR"

URL = f"https://www.goldapi.io/api/{SYMBOL}/{CURRENCY}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "gold_prices_india.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

TIMEOUT = 15


# =====================================================
# CHECK IF ALREADY RAN TODAY
# =====================================================

def already_ran_today():
    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(CSV_FILE):
        return False

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return today in f.read()


# =====================================================
# FETCH API DATA
# =====================================================

def fetch_gold_data():
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        r = requests.get(URL, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("API Error:", e)
        return None


# =====================================================
# SAVE CSV
# =====================================================

def save_to_csv(price, high, low):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["Datetime", "Price_INR", "High_INR", "Low_INR"])
        writer.writerow([now, price, high, low])


# =====================================================
# GENERATE HTML
# =====================================================

def generate_html(price, high, low):
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gold Price in India Today (24K & 22K)</title>
    <meta charset="utf-8">
    <meta name="description" content="Check today's gold price in India. Live 24K and 22K gold rates updated daily.">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    {FAQ_SCHEMA}

</head>
<body style="font-family:Arial; max-width:720px; margin:auto; padding:20px;">

<h1>Gold Price in India Today</h1>
<p><b>Last Updated:</b> {now}</p>

<h2>Current Rates</h2>

<table border="1" cellpadding="10" cellspacing="0">
<tr><th>Type</th><th>Price (INR)</th></tr>
<tr><td>Spot</td><td>₹{price}</td></tr>
<tr><td>High</td><td>₹{high}</td></tr>
<tr><td>Low</td><td>₹{low}</td></tr>
</table>

<hr>

<h2>Gold Price FAQs</h2>

<h3>What is today's gold price in India?</h3>
<p>This page shows the latest gold price in India for 24K and 22K gold.</p>

<h3>Is gold price the same across all cities?</h3>
<p>Minor variations may occur due to local taxes and jeweller margins.</p>

<h3>What is the difference between 24K and 22K gold?</h3>
<p>24K is pure gold, while 22K is used mainly for jewellery.</p>

<h3>How often does the gold price change?</h3>
<p>Gold prices change daily based on international markets.</p>

<h3>Is gold a good investment?</h3>
<p>Gold is commonly used as a hedge against inflation.</p>

<hr>
<p style="font-size:14px;">Powered by Bidyut's Gold Tracker</p>

</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


# =====================================================
# REBUILD FROM CSV
# =====================================================

def rebuild_from_csv():
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) < 2:
            return False

        last = lines[-1].strip().split(",")
        generate_html(last[1], last[2], last[3])
        return True


# =====================================================
# GIT PUSH
# =====================================================

def git_push():
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto daily update"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("GitHub updated.")
    except subprocess.CalledProcessError:
        print("Nothing new to push.")


# =====================================================
# MAIN
# =====================================================

def main():
    print("===================================")
    print(" Gold Auto System Running")
    print("===================================")

    if already_ran_today():
        print("Already ran today. Rebuilding site...")
        rebuild_from_csv()
        git_push()
        return

    data = fetch_gold_data()
    if not data:
        return

    price = data.get("price")
    high = data.get("high_price")
    low = data.get("low_price")

    save_to_csv(price, high, low)
    generate_html(price, high, low)
    git_push()


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    main()
