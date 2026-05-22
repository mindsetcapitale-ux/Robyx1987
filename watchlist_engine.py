# watchlist_engine.py

import requests
from datetime import datetime
from unified_trading_engine import UnifiedTradingEngine


WATCHLIST = [
    "bitcoin",
    "ethereum",
    "solana",
    "chainlink",
    "avalanche-2",
    "render-token",
]


def main():
    engine = UnifiedTradingEngine()

    print("\n==============================")
    print(" JARVIS WATCHLIST ENGINE")
    print("==============================\n")

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "ids": ",".join(WATCHLIST),
        "price_change_percentage": "1h,24h,7d",
    }

    headers = {
        "accept": "application/json",
        "User-Agent": "JarvisTradingEngine/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)

        if response.status_code == 429:
            print("Errore 429: CoinGecko ha bloccato troppe richieste.")
            print("Aspetta qualche minuto e rilancia il comando.")
            return

        response.raise_for_status()
        coins = response.json()

    except Exception as e:
        print(f"Errore richiesta watchlist: {e}")
        return

    market = engine.get_market_overview()

    for coin in coins:
        token = {
            "status": "ok",
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "rank": coin.get("market_cap_rank"),
            "volume_24h": coin.get("total_volume"),
            "change_1h": coin.get("price_change_percentage_1h_in_currency"),
            "change_24h": coin.get("price_change_percentage_24h_in_currency"),
            "change_7d": coin.get("price_change_percentage_7d_in_currency"),
            "ath": coin.get("ath"),
            "ath_change_percentage": coin.get("ath_change_percentage"),
        }

        analysis = engine.calculate_score(token)

        report = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "market": market,
            "token": token,
            "analysis": analysis,
        }

        engine.print_report(report)


if __name__ == "__main__":
    main()