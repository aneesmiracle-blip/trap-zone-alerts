import time
import requests
import pandas as pd
from datetime import datetime
import telegram

# === CONFIGURATION ===
BOT_TOKEN = "7481875754:AAFVurIEOgcftMw6H-xgp58lzCUPf28AR2g"
CHAT_ID = "5964132878"
ALERT_INTERVAL_MINUTES = 10
NSE_OI_URL = "https://www.nseindia.com/api/fo-analytics/participantWiseOI?type=Futures"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# === TELEGRAM FUNCTION ===
def send_telegram_message(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

# === DATA FETCH FUNCTION ===
def fetch_nse_participant_data():
    session = requests.Session()
    session.headers.update(HEADERS)

    # Access homepage once to set cookies
    session.get("https://www.nseindia.com", timeout=5)
    response = session.get(NSE_OI_URL, timeout=10)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Failed to fetch NSE data: Status {response.status_code}")

# === DATA ANALYSIS FUNCTION ===
def analyze_participant_data(data):
    df = pd.DataFrame(data["data"])
    latest_date = df["date"].max()
    latest_data = df[df["date"] == latest_date]

    msg = f"📊 Participant OI Summary ({latest_date}):\n\n"
    for client_type in ["Client", "FI]()_
