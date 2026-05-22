# jarvis_cycle.py

import time
from datetime import datetime

from market_sentiment_engine import build_report
from auto_watchlist_builder import update_auto_watchlist
from ai_signal_engine import run_ai_signal_engine
from anti_scam_engine import run_anti_scam_engine
from decision_engine import run_decision_engine
from telegram_alerts import send_telegram_message


CYCLE_INTERVAL_SECONDS = 1800


def run_full_cycle():
    print("\n==============================")
    print(" JARVIS FULL AUTO CYCLE")
    print("==============================\n")

    send_telegram_message(
        f"""
🤖 JARVIS AUTO CYCLE STARTED

Time:
{datetime.now().isoformat()}
"""
    )

    print("\n[1] MARKET SENTIMENT")
    sentiment = build_report()
    print(sentiment)

    send_telegram_message(sentiment)

    time.sleep(3)

    print("\n[2] AUTO WATCHLIST")
    watchlist = update_auto_watchlist(send_telegram=False)

    send_telegram_message(
        f"📋 Watchlist aggiornata. Coin trovate: {len(watchlist)}"
    )

    time.sleep(3)

    print("\n[3] AI SIGNAL ENGINE")
    signals = run_ai_signal_engine(send_telegram=True)

    time.sleep(3)

    print("\n[4] ANTI SCAM ENGINE")
    anti_scam = run_anti_scam_engine(send_telegram=True)

    time.sleep(3)

    print("\n[5] FINAL DECISION ENGINE")
    decisions = run_decision_engine(send_telegram=True)

    send_telegram_message(
        f"""
✅ JARVIS AUTO CYCLE COMPLETED

Signals:
{len(signals)}

Anti Scam Results:
{len(anti_scam)}

Decisions:
{len(decisions)}

Next cycle:
{CYCLE_INTERVAL_SECONDS / 60} minutes
"""
    )


def main():
    print("\n==============================")
    print(" JARVIS 24/7 AUTO SYSTEM")
    print("==============================\n")

    while True:

        try:
            run_full_cycle()

        except Exception as e:
            print("Errore ciclo:", e)

            send_telegram_message(
                f"""
❌ JARVIS AUTO CYCLE ERROR

Error:
{str(e)}
"""
            )

        print(f"\nAttendo {CYCLE_INTERVAL_SECONDS} secondi...\n")

        time.sleep(CYCLE_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()