import requests
import pandas as pd
from datetime import datetime
import time

# Telegram credentials
TELEGRAM_TOKEN = "7481875754:AAFVurIEOgcftMw6H-xgp58lzCUPf28AR2g"  # Replace if needed
TELEGRAM_CHAT_ID = "5964132878"

# Define the list of client types for analysis
CLIENT_TYPES = ["Client", "FII", "PRO", "DII"]

# Function to extract sentiment from NSE participant-wise data
def get_sentiment_table():
    url = "https://www.nseindia.com/api/participant-wise-position?type=FUTIDX"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()["data"]

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Extract last row (latest)
        latest_date = df["date"].max()
        latest_df = df[df["date"] == latest_date]

        sentiment = {}

        for client in CLIENT_TYPES:
            row = latest_df[latest_df["participant"] == client]
            if not row.empty:
                long_pos = row["long_position"].astype(float).values[0]
                short_pos = row["short_position"].astype(float).values[0]
                net_pos = long_pos - short_pos

                sentiment[client] = {
                    "Long": long_pos,
                    "Short": short_pos,
                    "Net": net_pos,
                    "Sentiment": "Bullish" if net_pos > 0 else "Bearish" if net_pos < 0 else "Neutral"
                }

        return sentiment, latest_date

    except Exception as e:
        return None, f"Error: {e}"

# Function to send alert via Telegram
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

# Build and send the sentiment message
def build_and_send_sentiment_alert():
    sentiment, date = get_sentiment_table()
    if not sentiment:
        send_telegram_alert(f"❌ Failed to fetch sentiment data.\n{date}")
        return

    msg = f"<b>📊 Participant Sentiment - {date}</b>\n"
    for client, values in sentiment.items():
        msg += (
            f"\n<b>{client}</b> → {values['Sentiment']}\n"
            f"  • Long: {values['Long']:.2f}\n"
            f"  • Short: {values['Short']:.2f}\n"
            f"  • Net: {values['Net']:.2f}\n"
        )

    send_telegram_alert(msg)

# Main loop (optional if scheduling externally)
if __name__ == "__main__":
    build_and_send_sentiment_alert()
