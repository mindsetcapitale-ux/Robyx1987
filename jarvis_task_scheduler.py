# jarvis_task_scheduler.py

import time
from datetime import datetime

from fast_mode_engine import run_fast_mode
from signal_reporter import run_signal_reporter
from jarvis_daily_digest import send_daily_digest
from smart_market_memory import capture_market_snapshot
from jarvis_health_check import build_health_report
from telegram_alerts import send_telegram_message


FAST_INTERVAL = 1800
SIGNALS_INTERVAL = 3600
DIGEST_INTERVAL = 21600
MEMORY_INTERVAL = 7200
HEALTH_INTERVAL = 10800


last_fast = 0
last_signals = 0
last_digest = 0
last_memory = 0
last_health = 0


def should_run(last_run, interval):
    return time.time() - last_run >= interval


def run_scheduler():
    global last_fast
    global last_signals
    global last_digest
    global last_memory
    global last_health

    print("\n==============================")
    print(" JARVIS TASK SCHEDULER")
    print("==============================\n")

    send_telegram_message(
        f"""
🕒 JARVIS TASK SCHEDULER ONLINE

Started:
{datetime.now().isoformat()}
"""
    )

    while True:

        try:

            if should_run(last_fast, FAST_INTERVAL):
                print("Running FAST MODE...")
                run_fast_mode(send_telegram=True)
                last_fast = time.time()

            if should_run(last_signals, SIGNALS_INTERVAL):
                print("Running SIGNAL REPORTER...")
                run_signal_reporter(send_telegram=True)
                last_signals = time.time()

            if should_run(last_digest, DIGEST_INTERVAL):
                print("Running DAILY DIGEST...")
                send_daily_digest()
                last_digest = time.time()

            if should_run(last_memory, MEMORY_INTERVAL):
                print("Capturing MARKET MEMORY...")
                capture_market_snapshot()
                last_memory = time.time()

            if should_run(last_health, HEALTH_INTERVAL):
                print("Running HEALTH CHECK...")

                report = build_health_report()

                print(report)

                send_telegram_message(report)

                last_health = time.time()

        except Exception as e:

            error_message = f"""
❌ JARVIS TASK SCHEDULER ERROR

{str(e)}

Time:
{datetime.now().isoformat()}
"""

            print(error_message)

            send_telegram_message(error_message)

        time.sleep(30)


if __name__ == "__main__":
    run_scheduler()