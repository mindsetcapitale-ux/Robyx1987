# live_scanner.py

import time
import requests
from datetime import datetime

from unified_trading_engine import UnifiedTradingEngine
from telegram_alerts import send_top_signals
from signal_history import save_signal


WATCHLIST = [
    "bitcoin",
    "ethereum",
    "solana",
    "chainlink",
    "avalanche-2",
    "render-token",
]

SCAN_INTERVAL_SECONDS = 600
MINIMUM_ALERT_SCORE = 70


def fetch_watchlist_market_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "ids": ",".join(WATCHLIST),
        "price_change_percentage": "1h,24h,7d",
    }

    headers = {
        "accept": "application/json",
        "User-Agent": "JarvisTradingEngine/1.0",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)

        if response.status_code == 429:
            print("Errore API 429: CoinGecko rate limit. Aspetto il prossimo ciclo.")
            return []

        if response.status_code != 200:
            print(f"Errore API {response.status_code}: {response.text}")
            return []

        return response.json()

    except Exception as e:
        print(f"Errore richiesta CoinGecko: {e}")
        return []


def build_token_from_coin(coin):
    return {
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


def build_signal(token, analysis):
    return {
        "symbol": token.get("symbol", "UNKNOWN").upper(),
        "score": analysis.get("score", 0),
        "change_24h": token.get("change_24h", 0),
        "source": "Jarvis Live Scanner",
        "reason": analysis.get("signal", "UNKNOWN"),
    }


def print_simple_report(token, analysis):
    print("\n==============================")
    print(" JARVIS SCANNER REPORT")
    print("==============================\n")
    print(f"Token: {token.get('name')} ({token.get('symbol')})")
    print(f"Prezzo: ${token.get('price')}")
    print(f"Rank: {token.get('rank')}")
    print(f"Market Cap: ${token.get('market_cap')}")
    print(f"Volume 24h: ${token.get('volume_24h')}")
    print(f"Change 1h: {token.get('change_1h')}%")
    print(f"Change 24h: {token.get('change_24h')}%")
    print(f"Change 7d: {token.get('change_7d')}%")
    print(f"Score: {analysis.get('score')}/100")
    print(f"Segnale: {analysis.get('signal')}")


def main():
    engine = UnifiedTradingEngine()

    print("\n==============================")
    print(" JARVIS LIVE SCANNER ONLINE")
    print("==============================\n")

    while True:
        print(f"\n[{datetime.now()}] Nuova scansione mercato...\n")

        coins = fetch_watchlist_market_data()

        if not coins:
            print("Nessun dato ricevuto. Possibile rate limit.")
            print(f"Attendo {SCAN_INTERVAL_SECONDS} secondi...\n")
            time.sleep(SCAN_INTERVAL_SECONDS)
            continue

        signals = []

        for coin in coins:
            token = build_token_from_coin(coin)
            analysis = engine.calculate_score(token)

            print_simple_report(token, analysis)

            score = analysis.get("score", 0)

            if score >= MINIMUM_ALERT_SCORE:
                signal = build_signal(token, analysis)
                signals.append(signal)
                save_signal(signal)

                print(f"Segnale trovato: {signal['symbol']} Score {signal['score']}")

        if signals:
            print("\nInvio segnali Telegram...\n")
            send_top_signals(signals)
        else:
            print("\nNessun segnale interessante trovato.\n")

        print(f"\nAttendo {SCAN_INTERVAL_SECONDS} secondi...\n")
        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()