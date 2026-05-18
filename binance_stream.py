# binance_stream.py

import requests


# =========================
# BINANCE TOP MOVERS
# =========================

def get_binance_top_movers():

    risultati = []

    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            timeout=10
        )

        data = response.json()

        for coin in data:
            symbol = coin.get("symbol", "")

            if not symbol.endswith("USDT"):
                continue

            if any(x in symbol for x in ["UP", "DOWN", "BULL", "BEAR"]):
                continue

            try:
                change = float(coin.get("priceChangePercent", 0))
                volume = float(coin.get("quoteVolume", 0))
                price = float(coin.get("lastPrice", 0))
            except:
                continue

            if volume < 5_000_000:
                continue

            if change > 15:
                continue

            if change < -8:
                continue

            score = 50

            if -2 <= change <= 4:
                score += 15

            if 1 <= change <= 3:
                score += 10

            if volume > 20_000_000:
                score += 10

            if volume > 50_000_000:
                score += 15

            risultati.append({
                "symbol": symbol,
                "price": price,
                "change": round(change, 2),
                "volume": round(volume, 2),
                "score": score
            })

        risultati = sorted(
            risultati,
            key=lambda x: x["score"],
            reverse=True
        )

        return risultati[:10]

    except Exception as e:
        print("Binance Stream Error:", e)
        return []


if __name__ == "__main__":
    movers = get_binance_top_movers()

    print("\n=== BINANCE PRE-PUMP MOVERS ===\n")

    for coin in movers:
        print(
            coin["symbol"],
            "| Price:",
            coin["price"],
            "| 24H:",
            coin["change"],
            "% | Score:",
            coin["score"]
        )