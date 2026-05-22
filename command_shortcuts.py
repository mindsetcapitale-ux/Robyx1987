# command_shortcuts.py

import sys

from signal_reporter import run_signal_reporter
from fast_mode_engine import run_fast_mode
from ai_signal_engine import run_ai_signal_engine
from early_gem_detector import scan_once
from anti_scam_engine import run_anti_scam_engine
from quality_filter_engine import run_quality_filter
from entry_planner import run_entry_planner
from market_phase_engine import run_market_phase_engine
from market_sentiment_engine import send_sentiment_report
from jarvis_daily_digest import send_daily_digest
from jarvis_health_check import build_health_report
from telegram_alerts import send_telegram_message


COMMANDS = {
    "signals": run_signal_reporter,
    "fast": run_fast_mode,
    "ai": run_ai_signal_engine,
    "gems": scan_once,
    "scam": run_anti_scam_engine,
    "quality": run_quality_filter,
    "entry": run_entry_planner,
    "phase": run_market_phase_engine,
    "sentiment": send_sentiment_report,
    "digest": send_daily_digest,
}


def print_help():
    print("""
==============================
 JARVIS COMMAND SHORTCUTS
==============================

Uso:

python3 command_shortcuts.py signals
python3 command_shortcuts.py fast
python3 command_shortcuts.py ai
python3 command_shortcuts.py gems
python3 command_shortcuts.py scam
python3 command_shortcuts.py quality
python3 command_shortcuts.py entry
python3 command_shortcuts.py phase
python3 command_shortcuts.py sentiment
python3 command_shortcuts.py digest
python3 command_shortcuts.py health
""")


def run_command(command):
    command = command.lower().strip()

    if command == "health":
        report = build_health_report()
        print(report)
        send_telegram_message(report)
        return

    if command not in COMMANDS:
        print("Comando non riconosciuto.")
        print_help()
        return

    func = COMMANDS[command]

    try:
        func(send_telegram=True)
    except TypeError:
        func()


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]
    run_command(command)


if __name__ == "__main__":
    main()