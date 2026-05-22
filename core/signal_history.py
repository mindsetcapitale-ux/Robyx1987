# signal_history.py

import json
import os
from datetime import datetime

HISTORY_FILE = "jarvis_signal_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception as e:
        print(f"Errore lettura storico: {e}")
        return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Errore salvataggio storico: {e}")


def save_signal(signal):
    history = load_history()

    record = {
        "timestamp": datetime.now().isoformat(),
        "symbol": signal.get("symbol", "UNKNOWN"),
        "score": signal.get("score", 0),
        "change_24h": signal.get("change_24h", 0),
        "source": signal.get("source", "Jarvis"),
        "reason": signal.get("reason", "N/A"),
    }

    history.append(record)
    save_history(history)

    print(f"Segnale salvato nello storico: {record['symbol']}")


def get_last_signals(limit=10):
    history = load_history()
    return history[-limit:]


def print_last_signals(limit=10):
    signals = get_last_signals(limit)

    print("\n==============================")
    print(" JARVIS SIGNAL HISTORY")
    print("==============================\n")

    if not signals:
        print("Nessun segnale salvato ancora.")
        print("Avvia live_scanner.py per creare i primi segnali.")
        return

    for signal in signals:
        print(f"Data: {signal.get('timestamp')}")
        print(f"Coin: {signal.get('symbol')}")
        print(f"Score: {signal.get('score')}")
        print(f"24H: {signal.get('change_24h')}%")
        print(f"Source: {signal.get('source')}")
        print(f"Reason: {signal.get('reason')}")
        print("------------------------------")


if __name__ == "__main__":
    print_last_signals()