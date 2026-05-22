# jarvis_command_center.py

from telegram_alerts import send_telegram_message

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
from smart_market_memory import capture_market_snapshot, send_memory_report
from signal_feedback_engine import send_feedback_report


def print_menu():
    print("""
==============================
 JARVIS COMMAND CENTER
==============================

1. Final Signals
2. Fast Mode
3. AI Signal Engine
4. Early Gems
5. Anti Scam Check
6. Quality Filter
7. Entry Planner
8. Market Phase
9. Market Sentiment
10. Daily Digest
11. Health Check
12. Capture Market Memory
13. Market Memory Report
14. Feedback Report
15. Send Status Telegram
16. Exit
""")


def main():
    while True:
        print_menu()

        choice = input("Scegli: ").strip()

        if choice == "1":
            run_signal_reporter(send_telegram=True)

        elif choice == "2":
            run_fast_mode()

        elif choice == "3":
            run_ai_signal_engine(send_telegram=True)

        elif choice == "4":
            scan_once(send_telegram=True)

        elif choice == "5":
            run_anti_scam_engine(send_telegram=True)

        elif choice == "6":
            run_quality_filter(send_telegram=True)

        elif choice == "7":
            run_entry_planner(send_telegram=True)

        elif choice == "8":
            run_market_phase_engine(send_telegram=True)

        elif choice == "9":
            send_sentiment_report()

        elif choice == "10":
            send_daily_digest()

        elif choice == "11":
            report = build_health_report()
            print(report)
            send_telegram_message(report)

        elif choice == "12":
            snapshot = capture_market_snapshot()
            if snapshot:
                send_telegram_message("🧠 Market snapshot salvato.")

        elif choice == "13":
            send_memory_report()

        elif choice == "14":
            send_feedback_report()

        elif choice == "15":
            send_telegram_message("🟢 Jarvis Command Center online.")

        elif choice == "16":
            print("Uscita da Jarvis Command Center.")
            break

        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()