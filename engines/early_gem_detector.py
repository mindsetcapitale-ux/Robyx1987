# engines/early_gem_detector.py

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
import requests
from datetime import datetime

from core.telegram_alerts import send_telegram_message


DEXSCREENER_SEARCH_URL = (
    "https://api.dexscreener.com/latest/dex/search"
)

SEARCH_TERMS = [
    "ai",
    "meme",
    "gaming",
    "base",
    "sol",
    "pepe",
    "doge",
]

MIN_LIQUIDITY = 15000
MAX_LIQUIDITY = 250000

MIN_VOLUME = 10000
MAX_FDV = 30000000

MIN_SCORE = 70

BLACKLIST = {
    "USDT",
    "USDC",
    "DAI",
    "BUSD",
    "FDUSD",
    "TUSD",
    "USDE",
}


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def search_pairs(term):
    try:
        response = requests.get(
            DEXSCREENER_SEARCH_URL,
            params={"q": term},
            timeout=20,
        )

        if response.status_code != 200:
            return []

        data = response.json()

        return data.get("pairs", [])

    except Exception as e:
        print("Errore ricerca:", e)
        return []


def calculate_score(pair):
    liquidity = safe_float(
        pair.get("liquidity", {}).get("usd")
    )

    volume = safe_float(
        pair.get("volume", {}).get("h24")
    )

    fdv = safe_float(
        pair.get("fdv")
    )

    change_1h = safe_float(
        pair.get("priceChange", {}).get("h1")
    )

    change_24h = safe_float(
        pair.get("priceChange", {}).get("h24")
    )

    score = 0
    reasons = []

    if MIN_LIQUIDITY <= liquidity <= MAX_LIQUIDITY:
        score += 25
        reasons.append("liquidità early ok")

    if volume >= MIN_VOLUME:
        score += 20
        reasons.append("volume interessante")

    if 0 < fdv <= MAX_FDV:
        score += 20
        reasons.append("FDV basso")

    if 2 <= change_1h <= 20:
        score += 20
        reasons.append("momentum iniziale")

    if 0 <= change_24h <= 40:
        score += 15
        reasons.append("pump non esploso")

    return max(0, min(score, 100)), reasons


def is_valid_pair(pair):
    base = pair.get("baseToken", {})

    symbol = str(
        base.get("symbol", "")
    ).upper()

    if symbol in BLACKLIST:
        return False

    return True


def build_card(pair, score, reasons):
    base = pair.get("baseToken", {})

    return {
        "name": base.get("name"),
        "symbol": base.get("symbol"),
        "chain": pair.get("chainId"),
        "dex": pair.get("dexId"),
        "price": pair.get("priceUsd"),
        "liquidity": safe_float(
            pair.get("liquidity", {}).get("usd")
        ),
        "volume_24h": safe_float(
            pair.get("volume", {}).get("h24")
        ),
        "fdv": safe_float(
            pair.get("fdv")
        ),
        "change_1h": safe_float(
            pair.get("priceChange", {}).get("h1")
        ),
        "change_24h": safe_float(
            pair.get("priceChange", {}).get("h24")
        ),
        "score": score,
        "reasons": reasons,
        "url": pair.get("url"),
    }


def deduplicate(cards):
    cleaned = {}

    for card in cards:
        symbol = str(
            card.get("symbol", "")
        ).upper()

        if not symbol:
            continue

        quality = (
            card.get("score", 0)
            + card.get("liquidity", 0) / 10000
            + card.get("volume_24h", 0) / 20000
        )

        card["quality_score"] = quality

        if symbol not in cleaned:
            cleaned[symbol] = card
        else:
            old_quality = cleaned[
                symbol
            ].get("quality_score", 0)

            if quality > old_quality:
                cleaned[symbol] = card

    return sorted(
        cleaned.values(),
        key=lambda x: x.get(
            "quality_score",
            0
        ),
        reverse=True
    )


def format_message(card):
    return f"""
💎 JARVIS EARLY GEM

Token:
{card.get("name")} ({card.get("symbol")})

⛓️ Chain:
{card.get("chain")}

🏦 DEX:
{card.get("dex")}

💵 Price:
${card.get("price")}

🧠 Score:
{card.get("score")}/100

💧 Liquidity:
${round(card.get("liquidity", 0), 2)}

📊 Volume:
${round(card.get("volume_24h", 0), 2)}

🏷️ FDV:
${round(card.get("fdv", 0), 2)}

📈 1H:
{card.get("change_1h")}%

📈 24H:
{card.get("change_24h")}%

📌 Reasons:
{", ".join(card.get("reasons", []))}

🔗 Chart:
{card.get("url")}

⏰ Time:
{datetime.now().isoformat()}

⚠️ Early gem radar only.
"""


def scan_once(send_telegram=True):
    print("\n==========================")
    print(" JARVIS EARLY GEM ENGINE")
    print("==========================\n")

    results = []
    seen = set()

    for term in SEARCH_TERMS:
        print(f"Scanning: {term}")

        pairs = search_pairs(term)

        for pair in pairs:
            address = pair.get(
                "pairAddress"
            )

            if not address:
                continue

            if address in seen:
                continue

            seen.add(address)

            if not is_valid_pair(pair):
                continue

            score, reasons = calculate_score(pair)

            if score < MIN_SCORE:
                continue

            card = build_card(
                pair,
                score,
                reasons
            )

            results.append(card)

        time.sleep(1)

    results = deduplicate(results)

    if not results:
        message = (
            "📭 Nessuna early gem trovata."
        )

        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    top = results[:5]

    for card in top:
        print(
            f"{card.get('symbol')} "
            f"| Score: {card.get('score')}"
        )

        if send_telegram:
            send_telegram_message(
                format_message(card)
            )

    return top


def main():
    scan_once(send_telegram=True)


if __name__ == "__main__":
    main()