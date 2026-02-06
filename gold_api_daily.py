# gold_api_daily.py
import requests
from datetime import datetime
import subprocess
import os
import csv

API_KEY = os.getenv("GOLD_API_KEY")
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

# Function to fetch gold price data from the API
def fetch_gold_price():
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }
    res = requests.get(URL, headers=headers)
    res.raise_for_status()  # Ensure the request was successful
    data = res.json()
    return data["price"], data["high_price"], data["low_price"]

# Update the CSV with new price data
def update_csv(price, high, low):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("gold_prices_india.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write new row with timestamp, price, high, and low values
        writer.writerow([now, price, high, low])

# Generate the HTML content for the website
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

# Git push to update the website
def git_push():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Auto daily update"], check=True)
    subprocess.run(["git", "push"], check=True)

# Check if today is a new day or if the API has been called already today
def check_if_new_day():
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # If the file doesn't exist, create it
    if not os.path.exists("last_api_run.txt"):
        with open("last_api_run.txt", "w") as file:
            file.write(today_date)
        return True  # First run, so call API

    # Read the date of the last API call
    with open("last_api_run.txt", "r") as file:
        last_run_date = file.read().strip()

    # If the last run date is different from today, it's a new day
    if last_run_date != today_date:
        # Update the file with today's date
        with open("last_api_run.txt", "w") as file:
            file.write(today_date)
        return True  # It's a new day, call the API

    return False  # No new day, skip API call

if __name__ == "__main__":
    # Check if it's a new day
    if check_if_new_day():
        price, high, low = fetch_gold_price()
        generate_html(price, high, low)
        update_csv(price, high, low)  # Update the CSV file with the new price data
        git_push()  # Commit and push to the repository
    else:
        print("API already called today. Skipping data fetch.")
