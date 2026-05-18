import requests
import re
import time

print("\n==============================")
print(" JARVIS PERFORMANCE TRACKER")
print("==============================\n")

try:
    with open("jarvis_reports.txt", "r", encoding="utf-8") as file:
        contenuto = file.read()
except Exception as e:
    print("Errore lettura report:")
    print(e)
    exit()

pattern = r"([A-Za-z0-9\s\-\._]+)\s\(([A-Z0-9]+)\)"
matches = re.findall(pattern, contenuto)

if len(matches) == 0:
    print("Nessuna coin trovata nei report.")
    exit()

coins = []
visti = set()

for nome, simbolo in matches:
    simbolo = simbolo.lower()

    if simbolo not in visti:
        visti.add(simbolo)
        coins.append({
            "nome": nome.strip(),
            "simbolo": simbolo
        })

print(f"Coin trovate nei report: {len(coins)}")
print("Controllo solo le prime 8 per evitare blocchi CoinGecko.\n")

for coin in coins[:8]:

    try:
        search_url = "https://api.coingecko.com/api/v3/search"

        search_response = requests.get(
            search_url,
            params={"query": coin["simbolo"]},
            timeout=10
        )

        search_data = search_response.json()
        risultati = search_data.get("coins", [])

        if len(risultati) == 0:
            print(f"{coin['simbolo'].upper()} - Nessun dato trovato")
            print("----------------------")
            continue

        coin_id = risultati[0]["id"]

        market_url = "https://api.coingecko.com/api/v3/coins/markets"

        market_response = requests.get(
            market_url,
            params={
                "vs_currency": "usd",
                "ids": coin_id
            },
            timeout=10
        )

        market_data = market_response.json()

        if not isinstance(market_data, list) or len(market_data) == 0:
            print(f"{coin['simbolo'].upper()} - Nessun market data")
            print("----------------------")
            continue

        market = market_data[0]

        prezzo = market.get("current_price")
        change_24h = market.get("price_change_percentage_24h")

        print(f"{coin['nome']} ({coin['simbolo'].upper()})")
        print(f"Prezzo attuale: ${prezzo}")

        if change_24h is not None:
            print(f"24H: {round(change_24h, 2)}%")

            if change_24h > 10:
                stato = "🔥 MOLTO FORTE"
            elif change_24h > 5:
                stato = "🚀 POSITIVA"
            elif change_24h > 0:
                stato = "📈 LEGGERMENTE POSITIVA"
            else:
                stato = "📉 NEGATIVA"

            print(f"Stato: {stato}")

        print("----------------------")

        time.sleep(2)

    except Exception as e:
        print(f"Errore su {coin['simbolo'].upper()}")
        print(e)
        print("----------------------")
        time.sleep(3)

print("\nTracker completato.\n")