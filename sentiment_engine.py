# sentiment_engine.py

from polymarket_engine import get_polymarket_markets

# =========================
# SENTIMENT ENGINE
# =========================

def calculate_polymarket_sentiment():

    markets = get_polymarket_markets()

    if len(markets) == 0:

        return {
            "score": 0,
            "status": "NEUTRAL",
            "markets": []
        }

    total_score = 0

    for market in markets:

        yes_price = market.get("yes_price", 0)

        try:
            yes_price = float(yes_price)
        except:
            yes_price = 0

        volume = market.get("volume", 0)

        try:
            volume = float(volume)
        except:
            volume = 0

        # probability weight
        if yes_price >= 0.7:
            total_score += 20

        elif yes_price >= 0.55:
            total_score += 10

        elif yes_price <= 0.35:
            total_score -= 10

        # volume weight
        if volume > 100_000:
            total_score += 10

        if volume > 500_000:
            total_score += 20

    total_score = max(
        -50,
        min(
            total_score,
            100
        )
    )

    if total_score >= 50:
        status = "BULLISH"

    elif total_score <= -20:
        status = "BEARISH"

    else:
        status = "NEUTRAL"

    return {
        "score": total_score,
        "status": status,
        "markets": markets
    }


if __name__ == "__main__":

    sentiment = calculate_polymarket_sentiment()

    print("\n=== POLYMARKET SENTIMENT ENGINE ===\n")

    print("Score:", sentiment["score"])
    print("Status:", sentiment["status"])

    print("\nMarkets:\n")

    for market in sentiment["markets"]:

        print(
            market["question"],
            "| YES:",
            market["yes_price"],
            "| Volume:",
            market["volume"]
        )