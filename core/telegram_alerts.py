# telegram_alerts.py

import os
import requests

BOT_TOKEN = "8969316010:AAEijoYi-IY65XKqMLzWwpNa5rEoeVUuvr0"
CHAT_ID = "268925092"


def telegram_ready():
    return BOT_TOKEN != "" and CHAT_ID != ""


def send_telegram_message(message):
    if not telegram_ready():
        print("Telegram non configurato.")
        print("Controlla TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")
        return None

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

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

        return response.json()

    except Exception as e:
        print("Telegram Error:", e)
        return None


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


def send_top_signals(signals):
    if not signals:
        print("Nessun segnale da inviare.")
        return

    for signal in signals[:3]:
        message = format_signal_message(signal)
        result = send_telegram_message(message)
        print("Risultato invio segnale:", result)


def send_trade_opened(trade):
    message = f"""
🟢 *JARVIS TRADE OPENED*

💎 Coin:
{trade.get('symbol', 'UNKNOWN')}

📊 Source:
{trade.get('source', 'UNKNOWN')}

🧠 Score:
{trade.get('score', 0)}

💵 Entry:
{trade.get('entry_price', 0)}

🎯 Take Profit:
{trade.get('take_profit', 0)}%

🛑 Stop Loss:
{trade.get('stop_loss', 0)}%
"""

    result = send_telegram_message(message)
    print("Risultato trade opened:", result)


def send_trade_closed(trade):
    message = f"""
🔴 *JARVIS TRADE CLOSED*

💎 Coin:
{trade.get('symbol', 'UNKNOWN')}

📌 Result:
{trade.get('close_reason', 'UNKNOWN')}

💵 Entry:
{trade.get('entry_price', 0)}

💰 Close:
{trade.get('close_price', 0)}

📈 Final PNL:
{trade.get('final_pnl', 0)}%

⏱ Duration:
{trade.get('duration_minutes', 0)} min
"""

    result = send_telegram_message(message)
    print("Risultato trade closed:", result)


def send_cloud_status(message):
    final_message = f"""
☁️ *JARVIS CLOUD STATUS*

{message}
"""

    result = send_telegram_message(final_message)
    print("Risultato cloud status:", result)


if __name__ == "__main__":

    test_signal = {
        "symbol": "BTC",
        "score": 87,
        "change_24h": 4.2,
        "source": "Jarvis AI Engine",
        "reason": "Strong volume and bullish trend"
    }

    send_cloud_status("Jarvis Telegram system online ✅")
    send_top_signals([test_signal])

    print("Test Telegram completato.")