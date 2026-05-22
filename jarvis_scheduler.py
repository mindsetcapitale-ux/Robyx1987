# jarvis_scheduler.py
# JARVIS AUTO SCHEDULER COMPATTO

import time
import datetime

from telegram_alerts import send_telegram_message
from signal_reporter import run_signal_reporter
from live_momentum_engine import scan_live_momentum
from jarvis_health_check import build_health_report


CYCLE_INTERVAL_SECONDS = 1800
HEALTH_INTERVAL_SECONDS = 3600

last_cycle_run = 0
last_health_run = 0
is_running = False


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def should_run(last_run, interval):
    return time.time() - last_run >= interval


def build_compact_summary(signals, momentum, health_report=None):
    message = f"""
🤖 JARVIS AUTO SUMMARY

Time:
{datetime.datetime.now().isoformat()}

Signals found:
{len(signals)}

Momentum found:
{len(momentum)}

"""

    if signals:
        message += "\n🚀 SIGNALS:\n"

        for item in signals[:3]:
            card = item.get("card", {})
            priority = item.get("priority", {})
            message += f"""
- {card.get("symbol")} | {priority.get("priority_level")}
  Score: {priority.get("priority_score")}
  Chain: {card.get("chain")}
"""

    if momentum:
        message += "\n⚡ MOMENTUM:\n"

        for item in momentum[:3]:
            message += f"""
- {item.get("symbol")} | Score: {item.get("score")}
  1H: {item.get("change_1h")}%
  24H: {item.get("change_24h")}%
"""

    if not signals and not momentum:
        message += "\n📭 Nessun segnale forte adesso.\n"

    if health_report:
        message += "\n🩺 Health check eseguito.\n"

    message += "\n⚠️ Non è consiglio finanziario."

    return message


def run_compact_cycle():
    log("Avvio ciclo compatto Jarvis...")

    signals = []
    momentum = []
    health_report = None

    try:
        signals = run_signal_reporter(send_telegram=False)
    except Exception as e:
        log(f"Errore signals: {e}")

    try:
        momentum = scan_live_momentum(send_telegram=False)
    except Exception as e:
        log(f"Errore momentum: {e}")

    summary = build_compact_summary(signals, momentum, health_report)

    send_telegram_message(summary)

    log("Ciclo compatto completato.")


def start_scheduler():
    global last_cycle_run
    global last_health_run
    global is_running

    log("JARVIS COMPACT SCHEDULER AVVIATO")

    send_telegram_message(
        """
🤖 JARVIS COMPACT AUTO MODE ONLINE

Invierò un solo report compatto per ciclo.
"""
    )

    while True:
        try:
            if should_run(last_cycle_run, CYCLE_INTERVAL_SECONDS):
                if not is_running:
                    is_running = True
                    run_compact_cycle()
                    last_cycle_run = time.time()
                    is_running = False
                else:
                    log("Ciclo già in esecuzione, salto.")

            if should_run(last_health_run, HEALTH_INTERVAL_SECONDS):
                try:
                    health_report = build_health_report()
                    print(health_report)
                    last_health_run = time.time()
                except Exception as e:
                    log(f"Errore health: {e}")

        except Exception as e:
            is_running = False

            send_telegram_message(
                f"""
❌ JARVIS SCHEDULER ERROR

Errore:
{str(e)}

Time:
{datetime.datetime.now().isoformat()}
"""
            )

        time.sleep(10)


if __name__ == "__main__":
    start_scheduler()