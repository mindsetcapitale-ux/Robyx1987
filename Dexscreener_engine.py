# Dexscreener_engine.py

import requests

WATCH_TOKENS = [
    "SOL",
    "ONDO",
    "FET",
    "RNDR",
    "WIF",
    "BONK"
]


def get_dexscreener_data():
    risultati = []

    for token in WATCH_TOKENS:
        try:
            response = requests.get(
                f"https://api.dexscreener.com/latest/dex/search/?q={token}",
                timeout=10
            )

            data = response.json()
            pairs = data.get("pairs", [])

            if len(pairs) == 0:
                continue

            pair = pairs[0]

            risultati.append({
                "symbol": token,
                "price": pair.get("priceUsd", "0"),
                "liquidity": pair.get("liquidity", {}).get("usd", 0),
                "volume24h": pair.get("volume", {}).get("h24", 0),
                "change24h": pair.get("priceChange", {}).get("h24", 0),
                "dex": pair.get("dexId", "unknown")
            })

        except Exception as e:
            print("DexScreener Error:", e)

    return risultati


if __name__ == "__main__":
    dati = get_dexscreener_data()

    print("\n=== DEXSCREENER LIVE ===\n")

    for coin in dati:
        print(
            coin["symbol"],
            "| Price:",
            coin["price"],
            "| Liquidity:",
            coin["liquidity"],
            "| Volume:",
            coin["volume24h"],
            "| 24H:",
            coin["change24h"],
            "| DEX:",
            coin["dex"]
        )