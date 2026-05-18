# realtime_engine.py
# Realtime stabile senza websocket

import requests
import time

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "ONDOUSDT",
    "FETUSDT",
    "RENDERUSDT"
]


def get_live_data():

    risultati = []

    try:

        response = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            timeout=10
        )

        data = response.json()

        for item in data:

            symbol = item.get("symbol", "")

            if symbol not in SYMBOLS:
                continue

            try:
                price = float(item.get("lastPrice", 0))
                change = float(item.get("priceChangePercent", 0))
                volume = float(item.get("quoteVolume", 0))

            except:
                continue

            risultati.append({

                "symbol": symbol,
                "price": price,
                "change": round(change, 2),
                "volume": round(volume, 2),
                "updated": time.strftime("%H:%M:%S")

            })

        return risultati

    except Exception as e:

        print("Realtime REST Error:", e)

        return []


if __name__ == "__main__":

    while True:

        dati = get_live_data()

        print("\n=== JARVIS REALTIME REST ===\n")

        for coin in dati:

            print(
                coin["symbol"],
                "| Price:",
                coin["price"],
                "| 24H:",
                coin["change"],
                "% | Volume:",
                coin["volume"],
                "|",
                coin["updated"]
            )

        time.sleep(5)