# core/telegram_bot_listener.py

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import time
import threading
import requests

from engines.unified_trading_engine import UnifiedTradingEngine
from core.telegram_alerts import (
    send_telegram_message,
    BOT_TOKEN
)
from core.signal_history import get_last_signals
from engines.early_gem_detector import scan_once
from core.ai_signal_engine import run_ai_signal_engine
from core.signal_reporter import run_signal_reporter
from engines.live_momentum_engine import (
    scan_live_momentum
)
from core.adaptive_learning_engine import (
    build_learning_report
)


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_UPDATE_ID = None

engine = UnifiedTradingEngine()

RUNNING_TASKS = {}


def run_background_task(
    task_name,
    function
):

    if RUNNING_TASKS.get(task_name):

        send_telegram_message(
            f"⏳ {task_name} è già in esecuzione."
        )

        return

    def wrapper():

        RUNNING_TASKS[task_name] = True

        try:

            send_telegram_message(
                f"🚀 Avvio {task_name}..."
            )

            function()

            send_telegram_message(
                f"✅ {task_name} completato."
            )

        except Exception as e:

            send_telegram_message(
                f"""
❌ Errore in {task_name}

{str(e)}
"""
            )

        finally:

            RUNNING_TASKS[
                task_name
            ] = False

    thread = threading.Thread(
        target=wrapper
    )

    thread.daemon = True
    thread.start()


def get_updates():

    global LAST_UPDATE_ID

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30
    }

    if LAST_UPDATE_ID:

        params["offset"] = (
            LAST_UPDATE_ID + 1
        )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        data = response.json()

        return data.get(
            "result",
            []
        )

    except Exception as e:

        print(
            "Errore getUpdates:",
            e
        )

        return []


def handle_command(chat_id, text):

    command = text.lower().strip()

    print(
        f"Comando ricevuto: {command}"
    )

    if command == "/start":

        message = """
🤖 JARVIS AI ONLINE

━━━━━━━━━━━━━━━━━━
⚡ CRYPTO AI SYSTEM
━━━━━━━━━━━━━━━━━━

🧠 AI Signals
⚡ Momentum Scanner
💎 Early Gems
🛡️ Scam Filters
📊 Smart Ranking
🚨 Priority Alerts
📚 Market Memory
🧬 Adaptive Learning

━━━━━━━━━━━━━━━━━━
📡 COMMANDS
━━━━━━━━━━━━━━━━━━

/signals
🚨 Smart AI signals

/momentum
⚡ Live momentum scanner

/learn
🧬 Adaptive learning report

/history
📚 Last signal history

/status
🟢 Jarvis system status

━━━━━━━━━━━━━━━━━━
🧠 SYSTEM STATUS
━━━━━━━━━━━━━━━━━━

✅ Online
✅ Async Active
✅ Cooldown Active
✅ Smart Filters Active
✅ Adaptive Learning Active
"""

        send_telegram_message(
            message
        )

    elif command == "/signals":

        run_background_task(
            "Smart Signals",
            lambda: run_signal_reporter(
                send_telegram=True
            )
        )

    elif command == "/momentum":

        run_background_task(
            "Live Momentum",
            lambda: scan_live_momentum(
                send_telegram=True
            )
        )

    elif command == "/learn":

        run_background_task(
            "Adaptive Learning",
            lambda: send_telegram_message(
                build_learning_report()
            )
        )

    elif command == "/status":

        active = [
            name
            for name, running
            in RUNNING_TASKS.items()
            if running
        ]

        if active:

            send_telegram_message(
                "⚡ Task attivi:\n\n"
                + "\n".join(active)
            )

        else:

            send_telegram_message(
                "🟢 Nessun task attivo."
            )

    else:

        send_telegram_message(
            "❌ Comando non riconosciuto."
        )


def main():

    global LAST_UPDATE_ID

    print("\n======================")
    print(" JARVIS TELEGRAM BOT")
    print("======================\n")

    while True:

        updates = get_updates()

        for update in updates:

            LAST_UPDATE_ID = update[
                "update_id"
            ]

            message = update.get(
                "message"
            )

            if not message:
                continue

            chat_id = message[
                "chat"
            ]["id"]

            text = message.get(
                "text",
                ""
            )

            handle_command(
                chat_id,
                text
            )

        time.sleep(1)


if __name__ == "__main__":
    main()