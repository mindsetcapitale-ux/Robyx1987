# jarvis_scheduler.py
# JARVIS AUTO SCHEDULER + DAILY REPORT

import time
import datetime

from unified_trading_engine import run_unified_engine
from report_exporter import run_exporter

# =========================
# SETTINGS
# =========================

INTERVAL_SECONDS = 300

REPORT_HOUR = 23
REPORT_MINUTE = 0

last_report_day = None

# =========================
# LOGGER
# =========================

def log(message):

    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(f"[{timestamp}] {message}")

# =========================
# REPORT CHECK
# =========================

def should_generate_report():

    global last_report_day

    now = datetime.datetime.now()

    today = now.date()

    if (
        now.hour == REPORT_HOUR
        and now.minute >= REPORT_MINUTE
    ):

        if last_report_day != today:

            last_report_day = today

            return True

    return False

# =========================
# MAIN LOOP
# =========================

def start_scheduler():

    log("JARVIS SCHEDULER AVVIATO")

    log(
        f"Intervallo: "
        f"{INTERVAL_SECONDS} secondi"
    )

    log(
        f"Daily report: "
        f"{REPORT_HOUR}:"
        f"{REPORT_MINUTE}"
    )

    while True:

        try:

            log("Avvio ciclo Jarvis...")

            run_unified_engine()

            log("Ciclo completato.")

            # =========================
            # DAILY REPORT
            # =========================

            if should_generate_report():

                log(
                    "Generazione "
                    "daily report..."
                )

                run_exporter()

                log(
                    "Daily report "
                    "completato."
                )

        except Exception as e:

            log(
                f"ERRORE "
                f"SCHEDULER: {e}"
            )

        log(
            "Attendo prossimo ciclo...\n"
        )

        time.sleep(
            INTERVAL_SECONDS
        )

# =========================
# START
# =========================

if __name__ == "__main__":

    start_scheduler()