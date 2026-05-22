# fast_mode_engine.py

from datetime import datetime

from signal_reporter import run_signal_reporter
from telegram_alerts import send_telegram_message


def run_fast_mode(send_telegram=True):
    print("\n==============================")
    print(" JARVIS FAST MODE")
    print("==============================\n")

    reports = run_signal_reporter(
        send_telegram=False
    )

    if not reports:
        message = """
⚡ JARVIS FAST MODE

Nessun segnale valido adesso.
"""

        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    top_reports = reports[:2]

    summary = f"""
⚡ JARVIS FAST MODE

Top Signals:
{len(top_reports)}

Generated:
{datetime.now().isoformat()}
"""

    print(summary)

    if send_telegram:
        send_telegram_message(summary)

    for item in top_reports:

        message = item.get("message", "")

        print(message)

        if send_telegram:
            send_telegram_message(message)

    return top_reports


def main():
    run_fast_mode(send_telegram=True)


if __name__ == "__main__":
    main()