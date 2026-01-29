import requests
import csv
import os
from datetime import datetime


# ============================
# CONFIG
# ============================

API_KEY = "goldapi-h5rolsmkzhkcgw-io"   # ⚠️ Hide later in production

SYMBOL = "XAU"
CURRENCY = "INR"

URL = f"https://www.goldapi.io/api/{SYMBOL}/{CURRENCY}"

CSV_FILE = "gold_prices_india.csv"
HTML_FILE = "index.html"

TIMEOUT = 15


# ============================
# CHECK IF ALREADY RUN TODAY
# ============================

def already_ran_today():

    today = datetime.now().strftime("%Y-%m-%d")

    if not os.path.exists(CSV_FILE):
        return False

    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if today in line:
                    return True
    except:
        pass

    return False


# ============================
# FETCH FROM API
# ============================

def fetch_gold_data():

    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        return None


# ============================
# SAVE TO CSV
# ============================

def save_to_csv(price, high, low):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = ["Datetime", "Price_INR", "High_INR", "Low_INR"]

    row = [now, price, high, high]

    file_exists = os.path.exists(CSV_FILE)

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(header)

            writer.writerow(row)

    except Exception as e:
        print("CSV Error:", e)


# ============================
# GENERATE WEBSITE
# ============================

def generate_html(price, high, low):

    today = datetime.now().strftime("%d %B %Y")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gold Price in India Today - {today}</title>

    <meta charset="utf-8">
    <meta name="description" content="Live gold price in India today. Updated daily. 24K gold rates.">

    <meta name="viewport" content="width=device-width, initial-scale=1">

</head>

<body style="font-family: Arial; max-width: 720px; margin: auto; padding: 20px; background:#fafafa;">

<h1>Gold Price in India Today</h1>

<p><b>Last Updated:</b> {today}</p>

<h2>Current Gold Rates</h2>

<table border="1" cellpadding="10" cellspacing="0">

<tr>
    <th>Type</th>
    <th>Price (INR)</th>
</tr>

<tr>
    <td>Spot Price</td>
    <td>₹{price}</td>
</tr>

<tr>
    <td>High</td>
    <td>₹{high}</td>
</tr>

<tr>
    <td>Low</td>
    <td>₹{low}</td>
</tr>

</table>

<p>Rates are updated automatically every day.</p>

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


# ============================
# MAIN
# ============================

def main():

    print("===================================")
    print(" Gold Auto Website Script Started")
    print("===================================")

    # If already ran today, rebuild site from latest CSV
    if already_ran_today():
        print("Already updated today. Rebuilding website...")

        try:
            with open(CSV_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

                if len(lines) < 2:
                    print("CSV has no data yet.")
                    return

                last = lines[-1].strip().split(",")

                price = last[1]
                high = last[2]
                low = last[3]

                generate_html(price, high, low)

                print("Website rebuilt from CSV.")

        except Exception as e:
            print("Rebuild Error:", e)

        return

    # Normal API flow
    print("Fetching gold data...")

    data = fetch_gold_data()

    if not data:
        print("No data. Exiting.")
        return

    price = data.get("price")
    high = data.get("high_price")
    low = data.get("low_price")

    if not price:
        print("Invalid response:", data)
        return

    print("-----------------------------")
    print("Price:", price)
    print("High :", high)
    print("Low  :", low)
    print("-----------------------------")

    save_to_csv(price, high, low)

    generate_html(price, high, low)

    print("CSV and Website Updated")
    print("Done.")



# ============================
# RUN
# ============================

if __name__ == "__main__":
    main()
