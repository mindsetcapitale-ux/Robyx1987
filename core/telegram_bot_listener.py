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

from engines.early_gem_detector import scan_once
from engines.live_momentum_engine import scan_live_momentum

from core.telegram_alerts import send_telegram_message, BOT_TOKEN
from core.signal_history import get_last_signals
from core.ai_signal_engine import run_ai_signal_engine
from core.signal_reporter import run_signal_reporter
from core.adaptive_learning_engine import build_learning_report


BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_UPDATE_ID = None
RUNNING_TASKS = {}

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
)

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}


def run_background_task(task_name, function):

    if RUNNING_TASKS.get(task_name):

        send_telegram_message(
            f"⏳ {task_name} già in esecuzione."
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
                f"❌ Errore in {task_name}\n\n{str(e)}"
            )

        finally:

            RUNNING_TASKS[task_name] = False

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


def get_market_data(symbol_name):

    try:

        coin_id = COINS.get(
            symbol_name
        )

        response = requests.get(
            COINGECKO_URL,
            params={
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=20
        )

        data = response.json()

        coin_data = data.get(
            coin_id
        )

        if not coin_data:
            return None

        return {
            "price": coin_data.get(
                "usd",
                0
            ),

            "change_24h": coin_data.get(
                "usd_24h_change",
                0
            ),
        }

    except Exception as e:

        print(
            f"CoinGecko errore {symbol_name}:",
            e
        )

        return None


def send_analysis(symbol_name):

    data = get_market_data(
        symbol_name
    )

    if not data:

        send_telegram_message(
            f"❌ Nessun dato trovato per {symbol_name}"
        )

        return

    price = round(
        data.get("price", 0),
        4
    )

    change_24h = round(
        data.get("change_24h", 0),
        2
    )

    message = f"""
📊 {symbol_name} ANALYSIS

💵 Price:
${price}

📈 24H:
{change_24h}%

Source:
CoinGecko

✅ Market data online
"""

    send_telegram_message(
        message
    )


def send_scan():

    results = []

    for symbol_name in [
        "BTC",
        "ETH",
        "SOL"
    ]:

        data = get_market_data(
            symbol_name
        )

        if not data:

            results.append(
                f"❌ {symbol_name}: nessun dato"
            )

            continue

        results.append(
            f"""
💎 {symbol_name}

💵 Price:
${round(data.get("price", 0), 4)}

📈 24H:
{round(data.get("change_24h", 0), 2)}%
"""
        )

        time.sleep(1)

    send_telegram_message(
        "🌍 JARVIS MARKET SCAN\n\n"
        + "\n".join(results)
    )


def send_history():

    signals = get_last_signals(5)

    if not signals:

        send_telegram_message(
            "📭 Nessuno storico ancora."
        )

        return

    rows = []

    for signal in signals:

        rows.append(
            f"""
💎 {signal.get("symbol")}

Score:
{signal.get("score")}

24H:
{signal.get("change_24h")}

Reason:
{signal.get("reason")}

Time:
{signal.get("timestamp")}
"""
        )

    send_telegram_message(
        "📚 JARVIS SIGNAL HISTORY\n\n"
        + "\n".join(rows)
    )


def send_gems():

    candidates = scan_once(
        send_telegram=False
    )

    if not candidates:

        send_telegram_message(
            "📭 Nessuna early gem trovata."
        )

        return

    for card in candidates[:5]:

        reasons = ", ".join(
            card.get("reasons", [])
        )

        message = f"""
💎 EARLY GEM

Token:
{card.get("name")}
({card.get("symbol")})

Score:
{card.get("score")}/100

Liquidity:
${round(card.get("liquidity", 0), 2)}

24H:
{card.get("change_24h")}%

Reasons:
{reasons}

Chart:
{card.get("url")}
"""

        send_telegram_message(
            message
        )


def send_momentum():

    results = scan_live_momentum(
        send_telegram=True
    )

    if not results:

        send_telegram_message(
            "📭 Nessun momentum forte."
        )


def handle_command(chat_id, text):

    command = text.lower().strip()

    print(
        f"Comando ricevuto: {command}"
    )

    if command == "/start":

        send_telegram_message(
            """
🤖 JARVIS AI ONLINE

/signals
/momentum
/learn
/history
/status
/scan
/gems
/btc
/eth
/sol

✅ Cloud 24/7 Active
"""
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
                "🟢 TASK ATTIVI\n\n"
                + "\n".join(active)
            )

        else:

            send_telegram_message(
                "🟢 Nessun task attivo."
            )

    elif command == "/signals":

        run_background_task(
            "Signals",
            lambda: run_signal_reporter(
                send_telegram=True
            )
        )

    elif command == "/momentum":

        run_background_task(
            "Momentum",
            send_momentum
        )

    elif command == "/learn":

        run_background_task(
            "Learning",
            lambda: send_telegram_message(
                build_learning_report()
            )
        )

    elif command == "/history":

        send_history()

    elif command == "/scan":

        run_background_task(
            "Market Scan",
            send_scan
        )

    elif command == "/gems":

        run_background_task(
            "Early Gems",
            send_gems
        )

    elif command == "/ai":

        run_background_task(
            "AI Signals",
            lambda: run_ai_signal_engine(
                send_telegram=True
            )
        )

    elif command == "/btc":

        run_background_task(
            "BTC Analysis",
            lambda: send_analysis("BTC")
        )

    elif command == "/eth":

        run_background_task(
            "ETH Analysis",
            lambda: send_analysis("ETH")
        )

    elif command == "/sol":

        run_background_task(
            "SOL Analysis",
            lambda: send_analysis("SOL")
        )

    else:

        send_telegram_message(
            "❌ Comando non riconosciuto."
        )


def main():

    global LAST_UPDATE_ID

    print(
        "\n=============================="
    )

    print(
        " JARVIS TELEGRAM CLOUD BOT"
    )

    print(
        "==============================\n"
    )

    while True:

        updates = get_updates()

        for update in updates:

            LAST_UPDATE_ID = (
                update["update_id"]
            )

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