# telegram_alerts.py

import requests

# =========================
# TELEGRAM CONFIG
# =========================

BOT_TOKEN = "8969316010:AAEijoYi-IY65XKqMLzWwpNa5rEoeVUuvr0"
CHAT_ID = "268925092"
# =========================
# SEND MESSAGE
# =========================

def send_telegram_message(message):

    try:

        url = (
            f"https://api.telegram.org/bot"
            f"{BOT_TOKEN}/sendMessage"
        )

        payload = {

            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"

        }

        response = requests.post(

            url,
            json=payload,
            timeout=10

        )

        print(response.json())
        return response.json()

    except Exception as e:

        print(
            "Telegram Error:",
            e
        )

        return None

# =========================
# FORMAT SIGNAL
# =========================

def format_signal_message(signal):

    return f"""
🚨 *JARVIS AI SIGNAL*

💎 Coin:
{signal.get('symbol', 'UNKNOWN')}

🧠 AI Score:
{signal.get('score', 0)}

📈 24H:
{signal.get('change_24h', 0)}%

📊 Source:
{signal.get('source', 'AI')}

📝 Reason:
{signal.get('reason', 'N/A')}
"""

# =========================
# SEND TOP SIGNALS
# =========================

def send_top_signals(signals):

    if len(signals) == 0:
        return

    top = signals[:3]

    for signal in top:

        message = format_signal_message(
            signal
        )

        send_telegram_message(
            message
        )

# =========================
# TEST
# =========================

if __name__ == "__main__":

    fake_signal = {

        "symbol": "SOL",
        "score": 92,
        "change_24h": 2.4,
        "source": "DEX",
        "reason": "Liquidity + momentum"

    }

    msg = format_signal_message(
        fake_signal
    )

    print(msg)

    send_telegram_message(msg)