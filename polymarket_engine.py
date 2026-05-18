# polymarket_engine.py

import requests

KEYWORDS = [
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "crypto",
    "binance",
    "solana",
    "sol",
    "fed",
    "etf"
]


def get_polymarket_markets():

    risultati = []

    try:

        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={
                "active": "true",
                "closed": "false",
                "limit": 100
            },
            timeout=15
        )

        markets = response.json()

        for market in markets:

            question = (
                market.get("question")
                or market.get("title")
                or ""
            )

            question_lower = question.lower()

            if not any(
                keyword in question_lower
                for keyword in KEYWORDS
            ):
                continue

            volume = float(
                market.get("volume", 0) or 0
            )

            liquidity = float(
                market.get("liquidity", 0) or 0
            )

            outcomes = market.get("outcomes", [])
            prices = market.get("outcomePrices", [])

            yes_price = "N/D"

            if isinstance(prices, list) and len(prices) > 0:
                yes_price = prices[0]

            risultati.append({

                "question": question,
                "volume": round(volume, 2),
                "liquidity": round(liquidity, 2),
                "yes_price": yes_price,
                "url": market.get("slug", "")

            })

        risultati = sorted(
            risultati,
            key=lambda x: x["volume"],
            reverse=True
        )

        return risultati[:10]

    except Exception as e:

        print("Polymarket Error:", e)

        return []


if __name__ == "__main__":

    markets = get_polymarket_markets()

    print("\n=== POLYMARKET SENTIMENT ===\n")

    for m in markets:

        print(
            m["question"],
            "| YES:",
            m["yes_price"],
            "| Volume:",
            m["volume"]
        )