# market_phase_engine.py

import requests
from datetime import datetime

from telegram_alerts import send_telegram_message


BTC_URL = "https://api.coingecko.com/api/v3/coins/bitcoin"


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_btc_market_data():
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }

    try:
        response = requests.get(
            BTC_URL,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            print("Errore BTC API:", response.text)
            return None

        data = response.json()

        market = data.get("market_data", {})

        return {
            "price": market.get("current_price", {}).get("usd"),
            "change_24h": market.get(
                "price_change_percentage_24h"
            ),
            "change_7d": market.get(
                "price_change_percentage_7d"
            ),
            "volume": market.get("total_volume", {}).get("usd"),
            "market_cap": market.get("market_cap", {}).get("usd"),
        }

    except Exception as e:
        print("Errore market phase:", e)
        return None


def detect_market_phase(data):
    if not data:
        return {
            "phase": "UNKNOWN",
            "reason": "Dati non disponibili"
        }

    change_24h = safe_float(data.get("change_24h"))
    change_7d = safe_float(data.get("change_7d"))

    if change_7d > 10:
        return {
            "phase": "BULLISH",
            "reason": "Trend settimanale forte"
        }

    if change_7d < -10:
        return {
            "phase": "BEARISH",
            "reason": "Trend settimanale debole"
        }

    if abs(change_24h) < 1.5:
        return {
            "phase": "SIDEWAYS",
            "reason": "Mercato laterale"
        }

    return {
        "phase": "NEUTRAL",
        "reason": "Mercato senza direzione forte"
    }


def format_market_phase(data, phase):
    return f"""
🌍 JARVIS MARKET PHASE ENGINE

BTC Price:
${round(safe_float(data.get("price")), 2)}

24H:
{round(safe_float(data.get("change_24h")), 2)}%

7D:
{round(safe_float(data.get("change_7d")), 2)}%

Detected Phase:
{phase.get("phase")}

Reason:
{phase.get("reason")}

Volume:
${round(safe_float(data.get("volume")), 2)}

Market Cap:
${round(safe_float(data.get("market_cap")), 2)}

Time:
{datetime.now().isoformat()}
"""


def run_market_phase_engine(send_telegram=True):
    print("\n==============================")
    print(" JARVIS MARKET PHASE ENGINE")
    print("==============================\n")

    data = get_btc_market_data()

    if not data:
        message = "❌ Impossibile leggere dati BTC."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return None

    phase = detect_market_phase(data)

    report = format_market_phase(data, phase)

    print(report)

    if send_telegram:
        send_telegram_message(report)

    return {
        "market": data,
        "phase": phase,
    }


def main():
    run_market_phase_engine(send_telegram=True)


if __name__ == "__main__":
    main()