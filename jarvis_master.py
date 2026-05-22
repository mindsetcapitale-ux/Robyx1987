# jarvis_master.py

from telegram_alerts import send_telegram_message
from ai_signal_engine import run_ai_signal_engine
from early_gem_detector import scan_once
from market_sentiment_engine import send_sentiment_report
from auto_watchlist_builder import update_auto_watchlist
from signal_history import print_last_signals
from performance_analyzer import build_performance_report
from trade_journal import build_report


def main():
    while True:
        print("""
==============================
 JARVIS MASTER CONTROL
==============================

1. AI Signal Engine
2. Early Gem Detector
3. Market Sentiment
4. Auto Watchlist
5. Signal History
6. Trade Journal Report
7. Performance Analyzer
8. Send Status Telegram
9. Exit
""")

        choice = input("Scegli: ").strip()

        if choice == "1":
            run_ai_signal_engine(send_telegram=True)

        elif choice == "2":
            scan_once(send_telegram=True)

        elif choice == "3":
            send_sentiment_report()

        elif choice == "4":
            update_auto_watchlist(send_telegram=True)

        elif choice == "5":
            print_last_signals()

        elif choice == "6":
            report = build_report()
            print(report)
            send_telegram_message(report)

        elif choice == "7":
            report = build_performance_report()
            print(report)
            send_telegram_message(report)

        elif choice == "8":
            send_telegram_message("🟢 Jarvis Master Control online.")

        elif choice == "9":
            print("Uscita da Jarvis Master.")
            break

        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()