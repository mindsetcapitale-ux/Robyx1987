# engines/live_momentum_engine.py

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


DEXSCREENER_SEARCH_URL = "https://api.dexscreener.com/latest/dex/search"

SEARCH_KEYWORDS = [
    "trending",
    "ai",
    "meme",
    "base",
    "sol",
    "pepe",
    "doge",
]

MIN_LIQUIDITY = 30000
MIN_VOLUME_24H = 50000
MIN_CHANGE_1H = 2
MAX_CHANGE_1H = 25
MAX_CHANGE_24H = 60
MAX_FDV = 80000000

STABLECOINS = {
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDD",
    "USD1", "RUSD", "EURCV", "REUR", "PYUSD", "USDE",
    "USDON", "U"
}


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def is_bad_token(pair):
    base = pair.get("baseToken", {})
    symbol = str(base.get("symbol", "")).upper()
    name = str(base.get("name", "")).upper()

    if symbol in STABLECOINS:
        return True

    bad_words = ["USD", "DOLLAR", "EURO", "STABLE", "TETHER"]

    for word in bad_words:
        if word in name:
            return True

    return False


def search_pairs(keyword):
    try:
        response = requests.get(
            DEXSCREENER_SEARCH_URL,
            params={"q": keyword},
            timeout=20,
        )

        if response.status_code != 200:
            print(f"DexScreener error {response.status_code}")
            return []

        data = response.json()
        return data.get("pairs", [])

    except Exception as e:
        print("Errore ricerca:", e)
        return []


def calculate_momentum_score(pair):
    liquidity = safe_float(pair.get("liquidity", {}).get("usd"))
    volume_24h = safe_float(pair.get("volume", {}).get("h24"))
    change_1h = safe_float(pair.get("priceChange", {}).get("h1"))
    change_6h = safe_float(pair.get("priceChange", {}).get("h6"))
    change_24h = safe_float(pair.get("priceChange", {}).get("h24"))
    fdv = safe_float(pair.get("fdv"))

    score = 0
    reasons = []
    blocks = []

    if liquidity >= MIN_LIQUIDITY:
        score += 20
        reasons.append("liquidità ok")
    else:
        blocks.append("liquidità bassa")

    if volume_24h >= MIN_VOLUME_24H:
        score += 25
        reasons.append("volume 24h forte")
    else:
        blocks.append("volume basso")

    if MIN_CHANGE_1H <= change_1h <= MAX_CHANGE_1H:
        score += 25
        reasons.append("momentum 1h sano")
    elif change_1h > MAX_CHANGE_1H:
        score -= 25
        blocks.append("pump 1h troppo alto")

    if change_6h > 0:
        score += 15
        reasons.append("trend 6h positivo")

    if change_24h <= MAX_CHANGE_24H:
        score += 10
    else:
        score -= 25
        blocks.append("pump 24h troppo alto")

    if 0 < fdv <= MAX_FDV:
        score += 15
        reasons.append("FDV accettabile")
    elif fdv > MAX_FDV:
        score -= 15
        blocks.append("FDV alto")

    score = max(0, min(score, 100))

    return score, reasons, blocks


def build_card(pair, score, reasons, blocks):
    base = pair.get("baseToken", {})

    return {
        "name": base.get("name", "UNKNOWN"),
        "symbol": base.get("symbol", "UNKNOWN"),
        "chain": pair.get("chainId", "unknown"),
        "dex": pair.get("dexId", "unknown"),
        "price": pair.get("priceUsd", "N/A"),
        "liquidity": safe_float(pair.get("liquidity", {}).get("usd")),
        "volume_24h": safe_float(pair.get("volume", {}).get("h24")),
        "change_1h": safe_float(pair.get("priceChange", {}).get("h1")),
        "change_6h": safe_float(pair.get("priceChange", {}).get("h6")),
        "change_24h": safe_float(pair.get("priceChange", {}).get("h24")),
        "fdv": safe_float(pair.get("fdv")),
        "score": score,
        "reasons": reasons,
        "blocks": blocks,
        "url": pair.get("url", ""),
        "pair_address": pair.get("pairAddress", ""),
    }


def clean_results(cards):
    cleaned = {}

    for card in cards:
        symbol = str(card.get("symbol", "")).upper()
        chain = str(card.get("chain", "")).lower()

        if not symbol:
            continue

        key = f"{symbol}_{chain}"

        quality = (
            safe_float(card.get("score"))
            + safe_float(card.get("liquidity")) / 10000
            + safe_float(card.get("volume_24h")) / 30000
        )

        card["quality_score"] = quality

        if key not in cleaned:
            cleaned[key] = card
        else:
            if quality > safe_float(cleaned[key].get("quality_score")):
                cleaned[key] = card

    return sorted(
        cleaned.values(),
        key=lambda x: x.get("quality_score", 0),
        reverse=True,
    )


def format_momentum_message(card):
    return f"""
⚡ JARVIS LIVE MOMENTUM

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

Price:
${card.get("price")}

Momentum Score:
{card.get("score")}/100

Quality Score:
{round(card.get("quality_score", 0), 2)}

Liquidity:
${round(card.get("liquidity", 0), 2)}

Volume 24H:
${round(card.get("volume_24h", 0), 2)}

1H:
{card.get("change_1h")}%

6H:
{card.get("change_6h")}%

24H:
{card.get("change_24h")}%

FDV:
${round(card.get("fdv", 0), 2)}

Reasons:
{", ".join(card.get("reasons", []))}

Blocks:
{", ".join(card.get("blocks", [])) if card.get("blocks") else "Nessun blocco forte"}

Chart:
{card.get("url")}

Time:
{datetime.now().isoformat()}

⚠️ Non comprare automaticamente. Usalo come radar momentum.
"""


def scan_live_momentum(send_telegram=True):
    print("\n==============================")
    print(" JARVIS LIVE MOMENTUM ENGINE")
    print("==============================\n")

    seen_pairs = set()
    results = []

    for keyword in SEARCH_KEYWORDS:
        print(f"Scanning keyword: {keyword}")

        pairs = search_pairs(keyword)

        for pair in pairs:
            pair_address = pair.get("pairAddress")

            if not pair_address or pair_address in seen_pairs:
                continue

            seen_pairs.add(pair_address)

            if is_bad_token(pair):
                continue

            score, reasons, blocks = calculate_momentum_score(pair)

            if score < 75:
                continue

            card = build_card(pair, score, reasons, blocks)
            results.append(card)

        time.sleep(1)

    results = clean_results(results)

    if not results:
        message = "📭 Live Momentum: nessun momentum forte trovato adesso."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    top = results[:5]

    for card in top:
        print("\n------------------------------")
        print(f"{card.get('name')} ({card.get('symbol')})")
        print(f"Score: {card.get('score')}")
        print(f"1H: {card.get('change_1h')}%")
        print(f"24H: {card.get('change_24h')}%")
        print(f"URL: {card.get('url')}")

        if send_telegram:
            send_telegram_message(format_momentum_message(card))

    return top


def main():
    scan_live_momentum(send_telegram=True)


if __name__ == "__main__":
    main()