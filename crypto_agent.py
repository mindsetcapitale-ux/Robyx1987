import requests
import time
from datetime import datetime

# =========================
# CONFIG
# =========================

INTERVALLO_SECONDI = 300  # 300 = controlla ogni 5 minuti
SOGLIA_SCORE = 10

# =========================
# FUNZIONI
# =========================

def scansiona_mercato():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "1h,24h,7d"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not isinstance(data, list):
        print("Errore dati:")
        print(data)
        return []

    opportunita = []

    for coin in data:
        nome = coin.get("name")
        simbolo = coin.get("symbol", "").upper()
        prezzo = coin.get("current_price")
        market_cap = coin.get("market_cap") or 0
        volume = coin.get("total_volume") or 0
        change_24h = coin.get("price_change_percentage_24h") or 0
        change_7d = coin.get("price_change_percentage_7d_in_currency") or 0

        if prezzo is None:
            continue

        if volume < 2_000_000:
            continue

        if market_cap < 10_000_000:
            continue

        if change_24h < 2:
            continue

        volume_ratio = volume / market_cap if market_cap > 0 else 0

        score = 0

        if change_24h > 2:
            score += 1
        if change_24h > 6:
            score += 2
        if change_24h > 12:
            score += 2

        if volume_ratio > 0.08:
            score += 2
        if volume_ratio > 0.18:
            score += 2

        if market_cap < 1_000_000_000:
            score += 1
        if market_cap < 300_000_000:
            score += 2
        if market_cap < 100_000_000:
            score += 2

        if change_24h > 40:
            score -= 4

        if change_7d < -20:
            score -= 2

        opportunita.append({
            "nome": nome,
            "simbolo": simbolo,
            "prezzo": prezzo,
            "market_cap": market_cap,
            "volume": volume,
            "change_24h": change_24h,
            "change_7d": change_7d,
            "volume_ratio": volume_ratio,
            "score": score
        })

    opportunita = sorted(opportunita, key=lambda x: x["score"], reverse=True)

    return opportunita


def stampa_opportunita(opportunita):
    print("\n==============================")
    print(" JARVIS ALERT SYSTEM")
    print(" Controllo:", datetime.now().strftime("%H:%M:%S"))
    print("==============================\n")

    forti = [coin for coin in opportunita if coin["score"] >= SOGLIA_SCORE]

    if len(forti) == 0:
        print("Nessun alert forte trovato ora.")
        print("Migliori coin in osservazione:\n")
        lista = opportunita[:10]
    else:
        print("🚨 ALERT FORTI TROVATI:\n")
        lista = forti[:10]

    for coin in lista:
        print(f"{coin['nome']} ({coin['simbolo']})")
        print(f"Prezzo: ${coin['prezzo']}")
        print(f"24H: {round(coin['change_24h'], 2)}%")
        print(f"7D: {round(coin['change_7d'], 2)}%")
        print(f"Volume: ${coin['volume']:,}")
        print(f"Market Cap: ${coin['market_cap']:,}")
        print(f"Volume/MarketCap: {round(coin['volume_ratio'] * 100, 2)}%")
        print(f"Score Jarvis: {coin['score']}")

        if coin["score"] >= 12:
            segnale = "🔥 ALERT MOLTO FORTE"
        elif coin["score"] >= 10:
            segnale = "🚨 WATCHLIST FORTE"
        elif coin["score"] >= 7:
            segnale = "INTERESSANTE"
        else:
            segnale = "OSSERVARE"

        if coin["change_24h"] > 40:
            rischio = "ALTO - possibile FOMO"
        elif coin["market_cap"] < 50_000_000:
            rischio = "ALTO - market cap piccola"
        elif coin["volume_ratio"] > 0.25:
            rischio = "MEDIO/ALTO - volume aggressivo"
        else:
            rischio = "MEDIO"

        print(f"Segnale: {segnale}")
        print(f"Rischio: {rischio}")
        print("--------------------------")


# =========================
# AVVIO
# =========================

print("\nJarvis Crypto Alert avviato.")
print("Controlla il mercato ogni 5 minuti.")
print("Per fermarlo premi CTRL + C.\n")

while True:
    try:
        opportunita = scansiona_mercato()
        stampa_opportunita(opportunita)

        print(f"\nProssimo controllo tra {INTERVALLO_SECONDI} secondi...\n")
        time.sleep(INTERVALLO_SECONDI)

    except KeyboardInterrupt:
        print("\nJarvis Crypto Alert fermato.")
        break

    except Exception as e:
        print("Errore:", e)
        print("Riprovo tra 60 secondi...")
        time.sleep(60)