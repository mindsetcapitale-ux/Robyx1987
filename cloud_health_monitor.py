# cloud_health_monitor.py

import time
from datetime import datetime

from core.telegram_alerts import send_telegram_message


HEARTBEAT_INTERVAL_SECONDS = 3600


def send_heartbeat():
    message = f"""
💓 JARVIS CLOUD HEARTBEAT

Status:
ONLINE

Mode:
Cloud 24/7

Time:
{datetime.now().isoformat()}

✅ Telegram listener attivo
✅ Render cloud attivo
✅ Jarvis operativo
"""
    send_telegram_message(message)


def start_health_monitor():
    print("JARVIS CLOUD HEALTH MONITOR AVVIATO")

    while True:
        try:
            send_heartbeat()
        except Exception as e:
            print("Errore heartbeat:", e)

        time.sleep(HEARTBEAT_INTERVAL_SECONDS)


if __name__ == "__main__":
    start_health_monitor()