# jarvis_guard.py

import subprocess
import time
from datetime import datetime

from telegram_alerts import send_telegram_message


TARGET_FILE = "jarvis_cycle.py"
RESTART_DELAY = 10


def run_guard():
    print("\n==============================")
    print(" JARVIS AUTO RESTART GUARD")
    print("==============================\n")

    while True:

        try:
            send_telegram_message(
                f"""
🛡️ JARVIS GUARD

Starting:
{TARGET_FILE}

Time:
{datetime.now().isoformat()}
"""
            )

            process = subprocess.Popen(
                ["python3", TARGET_FILE]
            )

            process.wait()

            send_telegram_message(
                f"""
⚠️ JARVIS PROCESS STOPPED

File:
{TARGET_FILE}

Restarting in:
{RESTART_DELAY} sec
"""
            )

        except Exception as e:

            send_telegram_message(
                f"""
❌ JARVIS GUARD ERROR

{str(e)}
"""
            )

        time.sleep(RESTART_DELAY)


if __name__ == "__main__":
    run_guard()