# auto_watchlist_builder.py

import json
import os
import requests
from datetime import datetime

from telegram_alerts import send_telegram_message


WATCHLIST_FILE = "auto_watchlist.json"

COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"

MIN_MARKET_CAP = 100_000_000
MIN_VOLUME_24H = 20_000_000
MAX_RANK = 200
MIN_CHANGE_24H = -10
MAX_CHANGE_24H = 20
TOP_LIMIT = 20


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def fetch_top_market():
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": "24h,7d",
    }

    headers = {
        "accept": "application/json",
        "User-Agent": "JarvisAutoWatchlist/1.0",
    }

    try:
        response = requests.get(
            COINGECKO_MARKETS_URL,
            params=params,
            headers=headers,
            timeout=20,
        )

        if response.status_code == 429:
            print("Errore 429: CoinGecko rate limit.")
            return []

        if response.status_code != 200:
            print(f"Errore CoinGecko {response.status_code}: {response.text}")
            return []

        return response.json()

    except Exception as e:
        print("Errore fetch market:", e)
        return []


def score_coin(coin):
    score = 0
    reasons = []

    rank = coin.get("market_cap_rank") or 999999
    market_cap = safe_float(coin.get("market_cap"))
    volume_24h = safe_float(coin.get("total_volume"))
    change_24h = safe_float(coin.get("price_change_percentage_24h_in_currency"))
    change_7d = safe_float(coin.get("price_change_percentage_7d_in_currency"))

    if rank <= 50:
        score += 20
        reasons.append("top 50")
    elif rank <= MAX_RANK:
        score += 10
        reasons.append("rank buono")

    if market_cap >= MIN_MARKET_CAP:
        score += 20
        reasons.append("market cap solido")

    if volume_24h >= MIN_VOLUME_24H:
        score += 25
        reasons.append("volume alto")

    if MIN_CHANGE_24H <= change_24h <= MAX_CHANGE_24H:
        score += 20
        reasons.append("movimento 24h sano")

    if change_7d > 0:
        score += 15
        reasons.append("trend 7d positivo")

    if change_24h > 30:
        score -= 25
        reasons.append("pump troppo forte")

    if change_24h < -20:
        score -= 20
        reasons.append("dump forte")

    score = max(0, min(score, 100))

    return score, reasons


def build_watchlist():
    coins = fetch_top_market()

    candidates = []

    for coin in coins:
        rank = coin.get("market_cap_rank") or 999999
        market_cap = safe_float(coin.get("market_cap"))
        volume_24h = safe_float(coin.get("total_volume"))
        change_24h = safe_float(coin.get("price_change_percentage_24h_in_currency"))

        if rank > MAX_RANK:
            continue

        if market_cap < MIN_MARKET_CAP:
            continue

        if volume_24h < MIN_VOLUME_24H:
            continue

        if change_24h < MIN_CHANGE_24H or change_24h > MAX_CHANGE_24H:
            continue

        score, reasons = score_coin(coin)

        candidates.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol", "").upper(),
            "name": coin.get("name"),
            "rank": rank,
            "price": coin.get("current_price"),
            "market_cap": market_cap,
            "volume_24h": volume_24h,
            "change_24h": change_24h,
            "score": score,
            "reasons": reasons,
            "updated_at": datetime.now().isoformat(),
        })

    candidates = sorted(
        candidates,
        key=lambda item: item["score"],
        reverse=True,
    )

    return candidates[:TOP_LIMIT]


def save_watchlist(watchlist):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as file:
            json.dump(watchlist, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Errore salvataggio watchlist:", e)


def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return []

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def format_watchlist_message(watchlist):
    if not watchlist:
        return "📭 Nessuna coin trovata per la watchlist automatica."

    message = """
📋 JARVIS AUTO WATCHLIST

Coin selezionate automaticamente:
"""

    for coin in watchlist[:10]:
        message += f"""

💎 {coin.get("name")} ({coin.get("symbol")})
Rank: {coin.get("rank")}
Score: {coin.get("score")}/100
24H: {round(safe_float(coin.get("change_24h")), 2)}%
Volume: ${round(safe_float(coin.get("volume_24h")), 2)}
Reason: {", ".join(coin.get("reasons", []))}
"""

    message += f"""

Updated:
{datetime.now().isoformat()}
"""

    return message


def update_auto_watchlist(send_telegram=True):
    print("\n==============================")
    print(" JARVIS AUTO WATCHLIST BUILDER")
    print("==============================\n")

    watchlist = build_watchlist()

    save_watchlist(watchlist)

    message = format_watchlist_message(watchlist)

    print(message)

    if send_telegram:
        send_telegram_message(message)

    return watchlist


def main():
    update_auto_watchlist(send_telegram=True)


if __name__ == "__main__":
    main()