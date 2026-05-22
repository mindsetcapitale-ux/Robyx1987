# unified_trading_engine.py

import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional


class UnifiedTradingEngine:
    def __init__(self):
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex"

        self.headers = {
            "accept": "application/json",
            "User-Agent": "JarvisTradingEngine/1.0"
        }

    def log(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] {message}")

    def safe_get(self, url: str, params: Optional[Dict[str, Any]] = None):
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=20
            )

            if response.status_code != 200:
                self.log(f"Errore API {response.status_code}: {response.text}")
                return None

            return response.json()

        except Exception as e:
            self.log(f"Errore richiesta API: {e}")
            return None

    def search_coingecko_coin_id(self, query: str) -> Optional[str]:
        url = f"{self.coingecko_url}/search"
        params = {"query": query}

        data = self.safe_get(url, params=params)

        if not data or "coins" not in data or len(data["coins"]) == 0:
            return None

        first_result = data["coins"][0]
        return first_result.get("id")

    def get_market_overview(self) -> Dict[str, Any]:
        url = f"{self.coingecko_url}/global"
        data = self.safe_get(url)

        if not data or "data" not in data:
            return {
                "status": "error",
                "message": "Impossibile leggere il mercato globale"
            }

        market = data["data"]

        return {
            "status": "ok",
            "market_cap_change_24h": market.get("market_cap_change_percentage_24h_usd"),
            "btc_dominance": market.get("market_cap_percentage", {}).get("btc"),
            "eth_dominance": market.get("market_cap_percentage", {}).get("eth"),
            "active_cryptocurrencies": market.get("active_cryptocurrencies"),
            "markets": market.get("markets"),
        }

    def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        url = f"{self.coingecko_url}/coins/markets"

        params = {
            "vs_currency": "usd",
            "ids": coin_id,
            "price_change_percentage": "1h,24h,7d",
        }

        data = self.safe_get(url, params=params)

        if not data or len(data) == 0:
            self.log(f"Nessun dato diretto per '{coin_id}'. Provo ricerca automatica...")

            corrected_id = self.search_coingecko_coin_id(coin_id)

            if not corrected_id:
                return {
                    "status": "error",
                    "message": f"Nessun dato trovato per {coin_id}"
                }

            self.log(f"ID corretto trovato: {corrected_id}")

            params["ids"] = corrected_id
            data = self.safe_get(url, params=params)

            if not data or len(data) == 0:
                return {
                    "status": "error",
                    "message": f"Nessun dato trovato nemmeno con ID corretto: {corrected_id}"
                }

        coin = data[0]

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

    def search_token_on_dex(self, query: str) -> Dict[str, Any]:
        url = f"{self.dexscreener_url}/search"
        params = {"q": query}

        data = self.safe_get(url, params=params)

        if not data or "pairs" not in data:
            return {
                "status": "error",
                "message": "Token non trovato su DexScreener"
            }

        pairs = data["pairs"][:5]

        results = []

        for pair in pairs:
            results.append({
                "chain": pair.get("chainId"),
                "dex": pair.get("dexId"),
                "base_token": pair.get("baseToken", {}).get("name"),
                "symbol": pair.get("baseToken", {}).get("symbol"),
                "price_usd": pair.get("priceUsd"),
                "liquidity_usd": pair.get("liquidity", {}).get("usd"),
                "volume_24h": pair.get("volume", {}).get("h24"),
                "price_change_24h": pair.get("priceChange", {}).get("h24"),
                "fdv": pair.get("fdv"),
                "pair_url": pair.get("url"),
            })

        return {
            "status": "ok",
            "query": query,
            "results": results,
        }

    def calculate_score(self, token: Dict[str, Any]) -> Dict[str, Any]:
        score = 0
        reasons = []

        price_change_24h = token.get("change_24h") or 0
        price_change_7d = token.get("change_7d") or 0
        volume_24h = token.get("volume_24h") or 0
        market_cap = token.get("market_cap") or 0
        rank = token.get("rank") or 99999
        ath_change = token.get("ath_change_percentage") or 0

        if rank <= 100:
            score += 20
            reasons.append("Token nella top 100")

        if market_cap > 500_000_000:
            score += 15
            reasons.append("Market cap solido")

        if volume_24h > 50_000_000:
            score += 15
            reasons.append("Volume 24h alto")

        if -10 <= price_change_24h <= 10:
            score += 10
            reasons.append("Movimento 24h non estremo")

        if price_change_7d > 0:
            score += 15
            reasons.append("Trend settimanale positivo")

        if ath_change < -50:
            score += 10
            reasons.append("Prezzo molto sotto ATH")

        if price_change_24h > 15:
            score -= 10
            reasons.append("Attenzione: salita forte nelle ultime 24h")

        if volume_24h < 1_000_000:
            score -= 20
            reasons.append("Volume basso")

        score = max(0, min(score, 100))

        if score >= 80:
            signal = "BUY WATCH"
        elif score >= 70:
            signal = "INTERESSANTE"
        elif score >= 50:
            signal = "NEUTRALE"
        else:
            signal = "RISCHIOSO"

        return {
            "score": score,
            "signal": signal,
            "reasons": reasons,
        }

    def analyze_coin(self, coin_id: str) -> Dict[str, Any]:
        self.log(f"Analizzo coin: {coin_id}")

        market = self.get_market_overview()
        token = self.get_coin_data(coin_id)

        if token.get("status") != "ok":
            return token

        score = self.calculate_score(token)

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "market": market,
            "token": token,
            "analysis": score,
        }

    def analyze_dex_token(self, query: str) -> Dict[str, Any]:
        self.log(f"Cerco token su DexScreener: {query}")
        return self.search_token_on_dex(query)

    def print_report(self, report: Dict[str, Any]):
        print("\n==============================")
        print(" JARVIS TRADING ENGINE REPORT")
        print("==============================\n")

        if report.get("status") != "ok":
            print("Errore:", report.get("message"))
            return

        token = report.get("token", {})
        analysis = report.get("analysis", {})
        market = report.get("market", {})

        print(f"Token: {token.get('name')} ({token.get('symbol')})")
        print(f"Prezzo: ${token.get('price')}")
        print(f"Rank: {token.get('rank')}")
        print(f"Market Cap: ${token.get('market_cap')}")
        print(f"Volume 24h: ${token.get('volume_24h')}")
        print(f"Change 1h: {token.get('change_1h')}%")
        print(f"Change 24h: {token.get('change_24h')}%")
        print(f"Change 7d: {token.get('change_7d')}%")
        print(f"Sotto ATH: {token.get('ath_change_percentage')}%")

        print("\n--- Mercato Globale ---")
        print(f"BTC Dominance: {market.get('btc_dominance')}%")
        print(f"ETH Dominance: {market.get('eth_dominance')}%")
        print(f"Market Cap 24h: {market.get('market_cap_change_24h')}%")

        print("\n--- Segnale Jarvis ---")
        print(f"Score: {analysis.get('score')}/100")
        print(f"Segnale: {analysis.get('signal')}")

        print("\nMotivi:")
        for reason in analysis.get("reasons", []):
            print(f"- {reason}")

        print("\nNota: questo non è consiglio finanziario. Serve solo come analisi automatica.\n")


def main():
    engine = UnifiedTradingEngine()

    print("\nJarvis Unified Trading Engine")
    print("1. Analizza coin CoinGecko")
    print("2. Cerca token su DexScreener")
    print("3. Esci")

    choice = input("\nScegli opzione: ").strip()

    if choice == "1":
        coin_id = input("Inserisci coin/token, esempio bitcoin, ethereum, solana: ").strip().lower()
        report = engine.analyze_coin(coin_id)
        engine.print_report(report)

    elif choice == "2":
        query = input("Inserisci nome o simbolo token: ").strip()
        result = engine.analyze_dex_token(query)
        print(json.dumps(result, indent=2))

    elif choice == "3":
        print("Uscita da Jarvis.")

    else:
        print("Scelta non valida.")


if __name__ == "__main__":
    main()