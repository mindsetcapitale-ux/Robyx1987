# jarvis_daily_digest.py

from datetime import datetime

from signal_history import get_last_signals
from trade_journal import build_report as build_trade_report
from performance_analyzer import build_performance_report
from smart_market_memory import build_memory_report
from jarvis_logger import get_last_logs
from telegram_alerts import send_telegram_message


def build_daily_digest():
    signals = get_last_signals(10)
    logs = get_last_logs(10)

    message = f"""
🗞️ JARVIS DAILY DIGEST

Date:
{datetime.now().isoformat()}

==============================

📡 Last Signals:
"""

    if signals:
        for signal in signals:
            message += f"""
💎 {signal.get("symbol")}
Score: {signal.get("score")}
Reason: {signal.get("reason")}
Time: {signal.get("timestamp")}
"""
    else:
        message += "\nNessun segnale recente.\n"

    message += """

==============================

📓 Trade Journal:
"""

    message += build_trade_report()

    message += """

==============================

📊 Performance:
"""

    message += build_performance_report()

    message += """

==============================

🧠 Market Memory:
"""

    message += build_memory_report()

    message += """

==============================

🧾 Last Logs:
"""

    if logs:
        for log in logs:
            message += f"""
{log.get("event_type")}:
{log.get("message")}
Time: {log.get("timestamp")}
"""
    else:
        message += "\nNessun log recente.\n"

    message += """

⚠️ Report automatico. Non è consiglio finanziario.
"""

    return message


def send_daily_digest():
    digest = build_daily_digest()

    print(digest)

    send_telegram_message(digest)


def main():
    send_daily_digest()


if __name__ == "__main__":
    main()