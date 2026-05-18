# telegram_alerts.py

import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def telegram_ready():
    return BOT_TOKEN != "" and CHAT_ID != ""


def send_telegram_message(message):
    if not telegram_ready():
        print("Telegram non configurato nel cloud.")
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
    if len(signals) == 0:
        return

    for signal in signals[:3]:
        message = format_signal_message(signal)
        send_telegram_message(message)


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

    send_telegram_message(message)


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

    send_telegram_message(message)


def send_cloud_status(message):
    final_message = f"""
☁️ *JARVIS CLOUD STATUS*

{message}
"""

    send_telegram_message(final_message)


if __name__ == "__main__":
    send_cloud_status("Telegram cloud alerts online ✅")