import os
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import asyncio
from telegram import Bot
from io import BytesIO

# === Telegram Setup ===
BOT_TOKEN = "7481875754:AAFVurIEOgcftMw6H-xgp58lzCUPf28AR2g"
CHAT_ID = "5964132878"

# === Fetch NSE Option Chain ===
def fetch_nse_option_chain(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/option-chain"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        response = session.get(url, headers=headers, timeout=5)
        data = response.json()
        records = data['records']['data']
        spot_price = data['records']['underlyingValue']
        calls, puts = [], []
        for item in records:
            strike = item.get("strikePrice")
            ce = item.get("CE")
            pe = item.get("PE")
            if ce:
                ce["strikePrice"] = strike
                calls.append(ce)
            if pe:
                pe["strikePrice"] = strike
                puts.append(pe)
        df_calls = pd.DataFrame(calls)
        df_puts = pd.DataFrame(puts)
        return df_calls, df_puts, spot_price
    except Exception as e:
        return None, None, None

# === Trap Score ===
def calculate_trap_score(df):
    df["trap_score"] = (df["openInterest"] * 0.5) + (df["changeinOpenInterest"] * 0.5)
    return df.sort_values("trap_score", ascending=False)

# === Save Excel ===
def save_to_excel(df_calls, df_puts, spot_price):
    folder = os.path.join(os.getcwd(), "nifty_trap_output")
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(folder, f"trap_zones_{timestamp}.xlsx")
    with pd.ExcelWriter(filepath) as writer:
        df_calls.to_excel(writer, sheet_name="Call Trap Zones", index=False)
        df_puts.to_excel(writer, sheet_name="Put Trap Zones", index=False)
    return filepath

# === Telegram Message & File ===
async def send_telegram(msg, file_path=None):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)
    if file_path:
        with open(file_path, "rb") as f:
            await bot.send_document(chat_id=CHAT_ID, document=f)

# === MAIN ===
if __name__ == "__main__":
    df_calls, df_puts, spot_price = fetch_nse_option_chain("NIFTY")
    if df_calls is not None and df_puts is not None:
        df_calls_filtered = calculate_trap_score(df_calls).head(3)
        df_puts_filtered = calculate_trap_score(df_puts).head(3)

        msg = f"""📈 NIFTY Trap Zone Alert - {datetime.now().strftime('%d-%m-%Y %H:%M')}

📍 Spot Price: {spot_price:.2f}

🔴 Call Trap Zones (Resistance):
{df_calls_filtered[['strikePrice', 'trap_score']].to_string(index=False)}

🟢 Put Trap Zones (Support):
{df_puts_filtered[['strikePrice', 'trap_score']].to_string(index=False)}
"""
        excel_path = save_to_excel(df_calls_filtered, df_puts_filtered, spot_price)
        asyncio.run(send_telegram(msg, excel_path))
    else:
        asyncio.run(send_telegram("❌ Failed to fetch NIFTY option chain data."))
