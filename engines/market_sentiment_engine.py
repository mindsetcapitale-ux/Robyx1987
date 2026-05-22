# market_sentiment_engine.py

import requests
from datetime import datetime

from telegram_alerts import send_telegram_message


FEAR_GREED_URL = "https://api.alternative.me/fng/"


def get_fear_greed_index():
    try:
        response = requests.get(FEAR_GREED_URL, timeout=20)

        if response.status_code != 200:
            return None

        data = response.json()

        if "data" not in data:
            return None

        return data["data"][0]

    except Exception as e:
        print("Errore Fear & Greed:", e)
        return None


def analyze_sentiment(index_value):
    value = int(index_value)

    if value <= 20:
        return {
            "sentiment": "EXTREME FEAR",
            "signal": "Possibile accumulo forte",
            "risk": "Mercato molto spaventato"
        }

    elif value <= 40:
        return {
            "sentiment": "FEAR",
            "signal": "Possibili opportunità",
            "risk": "Mercato debole"
        }

    elif value <= 60:
        return {
            "sentiment": "NEUTRAL",
            "signal": "Mercato equilibrato",
            "risk": "Nessun eccesso"
        }

    elif value <= 80:
        return {
            "sentiment": "GREED",
            "signal": "Attenzione ai pump",
            "risk": "Mercato molto ottimista"
        }

    else:
        return {
            "sentiment": "EXTREME GREED",
            "signal": "Alta probabilità di correzione",
            "risk": "Mercato euforico"
        }


def build_report():
    data = get_fear_greed_index()

    if not data:
        return "❌ Impossibile leggere Fear & Greed Index."

    value = data.get("value", "0")
    classification = data.get("value_classification", "UNKNOWN")

    analysis = analyze_sentiment(value)

    message = f"""
🧠 JARVIS MARKET SENTIMENT

Fear & Greed Index:
{value}

Classification:
{classification}

AI Sentiment:
{analysis.get("sentiment")}

Signal:
{analysis.get("signal")}

Risk:
{analysis.get("risk")}

Updated:
{datetime.now().isoformat()}

⚠️ Il sentiment non basta da solo per entrare nel mercato.
"""

    return message


def send_sentiment_report():
    report = build_report()

    print(report)

    send_telegram_message(report)


def main():
    send_sentiment_report()


if __name__ == "__main__":
    main()