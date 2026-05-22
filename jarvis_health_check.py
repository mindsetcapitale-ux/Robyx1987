# jarvis_health_check.py

import os
from datetime import datetime

from telegram_alerts import send_telegram_message


REQUIRED_FILES = [
    "telegram_alerts.py",
    "telegram_bot_listener.py",
    "unified_trading_engine.py",
    "early_gem_detector.py",
    "ai_signal_engine.py",
    "anti_scam_engine.py",
    "quality_filter_engine.py",
    "entry_planner.py",
    "signal_reporter.py",
    "market_phase_engine.py",
    "signal_cooldown.py",
    "signal_history.py",
    "jarvis_cycle.py",
]


def build_health_report():
    missing = []
    present = []

    for file in REQUIRED_FILES:
        if os.path.exists(file):
            present.append(file)
        else:
            missing.append(file)

    status = "OK" if not missing else "WARNING"

    message = f"""
🩺 JARVIS HEALTH CHECK

Status:
{status}

Files OK:
{len(present)}

Missing Files:
{len(missing)}

"""

    if missing:
        message += "Missing:\n"
        for file in missing:
            message += f"- {file}\n"
    else:
        message += "Tutti i file principali sono presenti.\n"

    message += f"""

Time:
{datetime.now().isoformat()}
"""

    return message


def main():
    report = build_health_report()
    print(report)
    send_telegram_message(report)


if __name__ == "__main__":
    main()