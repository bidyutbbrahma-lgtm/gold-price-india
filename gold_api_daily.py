import requests
import csv
import os
import subprocess
from datetime import datetime


# =========================
# CONFIG
# =========================

API_KEY = "goldapi-h5rolsmkzhkcgw-io"   # Move to env later

SYMBOL = "XAU"
CURRENCY = "INR"

URL = f"https://www.goldapi.io/api/{SYMBOL}/{CURRENCY}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(BASE_DIR, "gold_prices_india.csv")
HTML_FILE = os.path.join(BASE_DIR, "index.html")

TIMEOUT = 15


# =========================
# CHECK IF ALREADY RUN TODAY
# =========================

def already_ran_today():

    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(CSV_FILE):
        return False

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if today in line:
                    return True
    except Exception:
        pass

    return False


# =========================
# FETCH API DATA
# =========================

def fetch_gold_data():

    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(URL, headers=headers, timeout=TIMEOUT)
        res.raise_for_status()
        return res.json()

    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        return None


# =========================
# SAVE TO CSV
# =========================

def save_to_csv(price, high, low):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = ["Datetime", "Price_INR", "High_INR", "Low_INR"]
    row = [now, price, high, low]

    file_exists = os.path.exists(CSV_FILE)

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(header)

            writer.writerow(row)

    except Exception as e:
        print("CSV Error:", e)


# =========================
# GENERATE WEBSITE
# =========================

def generate_html(price, high, low):
    
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gold Price in India Today (24K & 22K) | Live Gold Rate</title>
    <meta charset="utf-8">
    <meta name="description" content="Check today’s gold price in India. Live 24K & 22K gold rates per gram, updated daily.">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="google-site-verification" content="B6PZgT-4bZtyxNfov8ddBxlJjSDgH8bBR6q7Ws2pqSo" />
</head>


<body style="font-family: Arial; max-width: 720px; margin: auto; padding: 20px; background:#fafafa;">

<h1>Gold Price in India Today</h1>

<p><b>Last Updated:</b> {now}</p>

<h2>Current Rates</h2>

<table border="1" cellpadding="10" cellspacing="0">

<tr><th>Type</th><th>Price (INR)</th></tr>
<tr><td>Spot</td><td>₹{price}</td></tr>
<tr><td>High</td><td>₹{high}</td></tr>
<tr><td>Low</td><td>₹{low}</td></tr>

</table>

<p>Updated automatically every day.</p>

<hr>

<h2>Gold Price FAQs</h2>

<h3>What is today’s gold price in India?</h3>
<p>
Today’s gold price in India depends on international gold rates, USD–INR exchange rate, and local demand.
This page shows the latest updated gold price in India for 24K and 22K gold.
</p>

<h3>Is gold price the same across all cities in India?</h3>
<p>
Gold prices are largely similar across India, but small differences may occur due to local taxes,
transport costs, and jeweller margins in different cities.
</p>

<h3>What is the difference between 24K and 22K gold?</h3>
<p>
24K gold is pure gold (99.9%) and is mainly used for investment.
22K gold contains a small amount of other metals and is commonly used for jewellery.
</p>

<h3>How often does the gold price change in India?</h3>
<p>
Gold prices change daily based on international market movements.
This website updates gold prices automatically every day.
</p>

<h3>Is gold a good investment in India?</h3>
<p>
Gold is considered a long-term store of value and a hedge against inflation.
Many investors track daily gold prices before making buying or investment decisions.
</p>

<hr>
<p style="font-size:14px;">Powered by Bidyut's Gold Tracker</p>

</body>
</html>
"""

    try:
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html)

    except Exception as e:
        print("HTML Error:", e)


# =========================
# REBUILD FROM CSV
# =========================

def rebuild_from_csv():

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:

            lines = f.readlines()

            if len(lines) < 2:
                return False

            last = lines[-1].strip().split(",")

            price = last[1]
            high = last[2]
            low = last[3]

            generate_html(price, high, low)

            return True

    except Exception as e:
        print("Rebuild Error:", e)
        return False


# =========================
# PUSH TO GITHUB
# =========================

def git_push():

    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Auto daily update"], check=True)
        subprocess.run(["git", "push"], check=True)

        print("GitHub updated.")

    except subprocess.CalledProcessError:
        print("Nothing new to push.")

    except Exception as e:
        print("Git Error:", e)


# =========================
# MAIN
# =========================

def main():

    print("===================================")
    print(" Gold Auto System Running")
    print("===================================")


    # If already ran today → rebuild only
    if already_ran_today():

        print("Already ran today. Rebuilding site...")

        if rebuild_from_csv():
            git_push()

        return


    # Normal run
    print("Fetching API data...")

    data = fetch_gold_data()

    if not data:
        return


    price = data.get("price")
    high = data.get("high_price")
    low = data.get("low_price")

    if not price:
        print("Invalid API response:", data)
        return


    print("Price:", price)
    print("High :", high)
    print("Low  :", low)


    save_to_csv(price, high, low)

    generate_html(price, high, low)

    git_push()

    print("System finished.")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()
