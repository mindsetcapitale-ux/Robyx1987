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

BINANCE_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"


def run_background_task(task_name, function):
    if RUNNING_TASKS.get(task_name):
        send_telegram_message(f"⏳ {task_name} è già in esecuzione.")
        return

    def wrapper():
        RUNNING_TASKS[task_name] = True

        try:
            send_telegram_message(f"🚀 Avvio {task_name}...")
            function()
            send_telegram_message(f"✅ {task_name} completato.")
        except Exception as e:
            send_telegram_message(f"❌ Errore in {task_name}\n\n{str(e)}")
        finally:
            RUNNING_TASKS[task_name] = False

    thread = threading.Thread(target=wrapper)
    thread.daemon = True
    thread.start()


def get_updates():
    global LAST_UPDATE_ID

    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}

    if LAST_UPDATE_ID:
        params["offset"] = LAST_UPDATE_ID + 1

    try:
        response = requests.get(url, params=params, timeout=35)
        data = response.json()
        return data.get("result", [])
    except Exception as e:
        print("Errore getUpdates:", e)
        return []


def get_binance_ticker(symbol):
    response = requests.get(
        BINANCE_24H_URL,
        params={"symbol": symbol},
        timeout=20
    )

    data = response.json()

    if "lastPrice" not in data:
        raise Exception(f"Nessun dato Binance per {symbol}: {data}")

    return data


def send_analysis(symbol_name, binance_symbol):
    try:
        data = get_binance_ticker(binance_symbol)

        price = float(data.get("lastPrice", 0))
        change_24h = float(data.get("priceChangePercent", 0))
        high_24h = float(data.get("highPrice", 0))
        low_24h = float(data.get("lowPrice", 0))
        volume = float(data.get("volume", 0))

        message = f"""
📊 {symbol_name} ANALYSIS

💵 Price:
${round(price, 4)}

📈 24H:
{round(change_24h, 2)}%

🔼 High 24H:
${round(high_24h, 4)}

🔽 Low 24H:
${round(low_24h, 4)}

📊 Volume:
{round(volume, 2)}

Source:
Binance

⚠️ Analisi rapida mercato.
"""

        send_telegram_message(message)

    except Exception as e:
        send_telegram_message(
            f"❌ Errore comando {symbol_name}\n\n{str(e)}"
        )


def send_scan():
    try:
        coins = [
            ("BTC", "BTCUSDT"),
            ("ETH", "ETHUSDT"),
            ("SOL", "SOLUSDT"),
        ]

        results = []

        for symbol_name, binance_symbol in coins:
            try:
                data = get_binance_ticker(binance_symbol)

                price = float(data.get("lastPrice", 0))
                change_24h = float(data.get("priceChangePercent", 0))

                results.append(
                    f"""
💎 {symbol_name}

💵 Price:
${round(price, 4)}

📈 24H:
{round(change_24h, 2)}%
"""
                )

                time.sleep(1)

            except Exception as e:
                results.append(f"❌ {symbol_name}: {str(e)}")

        send_telegram_message(
            "🌍 JARVIS MARKET SCAN\n\n" + "\n".join(results)
        )

    except Exception as e:
        send_telegram_message(
            f"❌ Errore Market Scan\n\n{str(e)}"
        )


def send_history():
    signals = get_last_signals(5)

    if not signals:
        send_telegram_message("📭 Nessuno storico ancora.")
        return

    rows = []

    for signal in signals:
        rows.append(
            f"""
💎 {signal.get("symbol")}
Score: {signal.get("score")}
24H: {signal.get("change_24h")}
Reason: {signal.get("reason")}
Time: {signal.get("timestamp")}
"""
        )

    send_telegram_message(
        "📚 JARVIS SIGNAL HISTORY\n\n" + "\n".join(rows)
    )


def send_gems():
    candidates = scan_once(send_telegram=False)

    if not candidates:
        send_telegram_message("📭 Nessuna early gem interessante trovata.")
        return

    for card in candidates[:5]:
        reasons = ", ".join(card.get("reasons", []))

        message = f"""
💎 EARLY GEM

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

Score:
{card.get("score")}/100

Liquidity:
${round(card.get("liquidity", 0), 2)}

Volume:
${round(card.get("volume_24h", 0), 2)}

24H:
{card.get("change_24h")}%

Reasons:
{reasons}

Chart:
{card.get("url")}
"""
        send_telegram_message(message)


def send_momentum():
    results = scan_live_momentum(send_telegram=True)

    if not results:
        send_telegram_message("📭 Nessun momentum forte trovato adesso.")


def handle_command(chat_id, text):
    command = text.lower().strip()

    print(f"Comando ricevuto: {command}")

    if command == "/start":
        send_telegram_message(
            """
🤖 JARVIS AI ONLINE

/signals - Smart AI signals
/momentum - Live momentum scanner
/learn - Adaptive learning report
/history - Storico segnali
/status - Stato sistema
/scan - Market scan
/gems - Early gems
/btc - Bitcoin analysis
/eth - Ethereum analysis
/sol - Solana analysis

✅ Cloud 24/7 Active
✅ Async Active
✅ Smart Filters Active
✅ Adaptive Learning Active
"""
        )

    elif command == "/status":
        active = [
            name for name, running in RUNNING_TASKS.items()
            if running
        ]

        if active:
            send_telegram_message(
                "🟢 JARVIS OPERATIVO\n\nTask attivi:\n" + "\n".join(active)
            )
        else:
            send_telegram_message(
                "🟢 JARVIS OPERATIVO\n\n✅ Nessun task attivo."
            )

    elif command == "/signals":
        run_background_task(
            "Smart Signals",
            lambda: run_signal_reporter(send_telegram=True)
        )

    elif command == "/momentum":
        run_background_task(
            "Live Momentum",
            send_momentum
        )

    elif command == "/learn":
        run_background_task(
            "Adaptive Learning",
            lambda: send_telegram_message(build_learning_report())
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
            "AI Signal Engine",
            lambda: run_ai_signal_engine(send_telegram=True)
        )

    elif command == "/btc":
        run_background_task(
            "BTC Analysis",
            lambda: send_analysis("BTC", "BTCUSDT")
        )

    elif command == "/eth":
        run_background_task(
            "ETH Analysis",
            lambda: send_analysis("ETH", "ETHUSDT")
        )

    elif command == "/sol":
        run_background_task(
            "SOL Analysis",
            lambda: send_analysis("SOL", "SOLUSDT")
        )

    else:
        send_telegram_message(
            "❌ Comando non riconosciuto.\n\nUsa /start"
        )


def main():
    global LAST_UPDATE_ID

    print("\n==============================")
    print(" JARVIS TELEGRAM CLOUD BOT")
    print("==============================\n")

    while True:
        updates = get_updates()

        for update in updates:
            LAST_UPDATE_ID = update["update_id"]

            message = update.get("message")

            if not message:
                continue

            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            handle_command(chat_id, text)

        time.sleep(1)


if __name__ == "__main__":
    main()