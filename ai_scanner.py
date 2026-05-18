# ai_scanner.py

import requests
import random

btc_market_status = "NEUTRAL"

# =========================
# BTC FILTER
# =========================

def controlla_btc():

    global btc_market_status

    try:

        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin",
            timeout=10
        )

        data = response.json()

        btc_change = data[
            "market_data"
        ][
            "price_change_percentage_24h"
        ]

        if btc_change >= 2:

            btc_market_status = "BULLISH"

        elif btc_change <= -2:

            btc_market_status = "BEARISH"

        else:

            btc_market_status = "NEUTRAL"

    except:

        btc_market_status = "UNKNOWN"

# =========================
# NEWS IMPACT
# =========================

def news_impact():

    headlines = [

        "ETF",
        "Binance",
        "Whale",
        "AI",
        "Funding",
        "Partnership",
        "Listing",
        "Launch",
        "Token Burn"

    ]

    return random.choice(headlines)

# =========================
# SCAM SCORE
# =========================

def scam_score(
    market_cap,
    volume,
    change_24h
):

    rischio = 0

    if market_cap < 5_000_000:
        rischio += 40

    if volume > market_cap * 5:
        rischio += 30

    if change_24h > 25:
        rischio += 50

    return rischio

# =========================
# AI SCORE
# =========================

def ai_score(
    change_24h,
    volume,
    market_cap
):

    ratio = (
        volume / market_cap
        if market_cap > 0 else 0
    )

    score = 50

    if ratio > 0.03:
        score += 10

    if ratio > 0.07:
        score += 15

    if ratio > 0.15:
        score += 20

    if -2 <= change_24h <= 4:
        score += 15

    if 1 <= change_24h <= 3:
        score += 10

    if market_cap < 300_000_000:
        score += 10

    if market_cap < 100_000_000:
        score += 15

    if btc_market_status == "BULLISH":
        score += 10

    if btc_market_status == "BEARISH":
        score -= 15

    if change_24h > 10:
        score -= 20

    rischio = scam_score(
        market_cap,
        volume,
        change_24h
    )

    score -= rischio

    score = max(
        1,
        min(
            int(score),
            99
        )
    )

    return score, rischio

# =========================
# MARKET SCANNER
# =========================

def scan_market():

    controlla_btc()

    coins = []

    try:

        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={

                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 100,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h"

            },
            timeout=15
        )

        data = response.json()

        for coin in data:

            nome = coin.get("name")

            simbolo = coin.get(
                "symbol",
                ""
            ).upper()

            market_cap = (
                coin.get("market_cap") or 0
            )

            volume = (
                coin.get("total_volume") or 0
            )

            change_24h = (
                coin.get(
                    "price_change_percentage_24h"
                ) or 0
            )

            if volume < 1_500_000:
                continue

            if market_cap < 15_000_000:
                continue

            if change_24h > 15:
                continue

            if change_24h < -8:
                continue

            score, rischio = ai_score(
                change_24h,
                volume,
                market_cap
            )

            if rischio >= 50:
                continue

            if score < 55:
                continue

            risultato = {

                "nome": nome,
                "simbolo": simbolo,
                "ai_probability": score,
                "news": news_impact(),
                "rischio": rischio,
                "change_24h": round(
                    change_24h,
                    2
                )

            }

            coins.append(
                risultato
            )

        coins = sorted(
            coins,
            key=lambda x: x["ai_probability"],
            reverse=True
        )

        return coins[:10]

    except Exception as e:

        print("AI Scanner Error:", e)

        return []