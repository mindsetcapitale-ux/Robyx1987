# learning_engine.py

import json
import os
import datetime
import requests

LEARNING_FILE = "jarvis_learning.json"


def inizializza_learning():
    if not os.path.exists(LEARNING_FILE):
        data = {
            "tracked_signals": [],
            "completed_checks": [],
            "stats": {
                "total_checks": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0
            }
        }

        with open(LEARNING_FILE, "w") as file:
            json.dump(data, file, indent=4)


def carica_learning():
    inizializza_learning()

    with open(LEARNING_FILE, "r") as file:
        return json.load(file)


def salva_learning(data):
    with open(LEARNING_FILE, "w") as file:
        json.dump(data, file, indent=4)


def salva_signal_da_monitorare(coin):
    data = carica_learning()

    simbolo = coin.get("symbol") or coin.get("simbolo") or ""
    nome = coin.get("name") or coin.get("nome") or simbolo
    score = coin.get("score") or coin.get("ai_probability") or 0
    change_24h = coin.get("change_24h") or 0

    signal = {
        "nome": nome,
        "simbolo": simbolo,
        "entry_price": coin.get("price", 0),
        "score": score,
        "change_24h": change_24h,
        "timestamp": str(datetime.datetime.now()),
        "checked": False
    }

    data["tracked_signals"].append(signal)
    salva_learning(data)


def get_price_from_binance(symbol):
    try:
        symbol = symbol.upper()

        if not symbol.endswith("USDT"):
            symbol = symbol + "USDT"

        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )

        data = response.json()

        if "price" in data:
            return float(data["price"])

    except:
        pass

    return None


def controlla_performance():
    data = carica_learning()

    for signal in data["tracked_signals"]:
        if signal.get("checked"):
            continue

        entry_price = signal.get("entry_price", 0)
        simbolo = signal.get("simbolo", "")

        if entry_price == 0:
            continue

        current_price = get_price_from_binance(simbolo)

        if current_price is None:
            continue

        performance = ((current_price - entry_price) / entry_price) * 100

        result = {
            "nome": signal["nome"],
            "simbolo": simbolo,
            "entry_price": entry_price,
            "current_price": current_price,
            "performance": round(performance, 2),
            "score": signal.get("score", 0),
            "timestamp_entry": signal.get("timestamp"),
            "timestamp_check": str(datetime.datetime.now())
        }

        if performance > 0:
            data["stats"]["wins"] += 1
        else:
            data["stats"]["losses"] += 1

        data["stats"]["total_checks"] += 1

        total = data["stats"]["total_checks"]

        if total > 0:
            data["stats"]["win_rate"] = round(
                (data["stats"]["wins"] / total) * 100,
                2
            )

        signal["checked"] = True
        data["completed_checks"].append(result)

    salva_learning(data)

    return data["stats"]


def get_learning_stats():
    data = carica_learning()
    return data["stats"]


if __name__ == "__main__":
    stats = controlla_performance()

    print("\n=== JARVIS LEARNING STATS ===\n")
    print(stats)