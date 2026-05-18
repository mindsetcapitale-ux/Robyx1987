# keep_alive.py
# JARVIS KEEP ALIVE SERVICE

import requests
import time
import datetime

JARVIS_URL = "https://jarvis-dashboard-pmeh.onrender.com"

INTERVAL_SECONDS = 600


def log(message):

    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(f"[{timestamp}] {message}")


def keep_alive():

    log("Keep alive avviato")

    while True:

        try:

            response = requests.get(
                JARVIS_URL,
                timeout=20
            )

            log(
                f"Ping Jarvis: "
                f"{response.status_code}"
            )

        except Exception as e:

            log(
                f"Errore keep alive: {e}"
            )

        time.sleep(
            INTERVAL_SECONDS
        )


if __name__ == "__main__":

    keep_alive()