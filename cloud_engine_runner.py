# cloud_engine_runner.py
# JARVIS CLOUD AUTO ENGINE LOOP

import time
import datetime

from unified_trading_engine import run_unified_engine

INTERVAL_SECONDS = 300


def log(message):

    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(f"[{timestamp}] {message}")


def start_cloud_engine():

    log("JARVIS CLOUD ENGINE AVVIATO")

    while True:

        try:

            log("Avvio ciclo automatico Jarvis")

            run_unified_engine()

            log("Ciclo completato")

        except Exception as e:

            log(f"ERRORE CLOUD ENGINE: {e}")

        log("Attendo prossimo ciclo...\n")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":

    start_cloud_engine()