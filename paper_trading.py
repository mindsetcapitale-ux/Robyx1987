import requests
import re
import datetime

print("\n==============================")
print(" JARVIS REAL PERFORMANCE")
print("==============================\n")

# =========================
# LEGGI WATCHLIST
# =========================

try:

    with open(
        "watchlist.txt",
        "r",
        encoding="utf-8"
    ) as file:

        righe = file.readlines()

except Exception as e:

    print("Errore lettura watchlist:")
    print(e)
    exit()

if len(righe) == 0:

    print("Watchlist vuota.")
    exit()

# =========================
# ANALISI
# =========================

trade_totali = 0
trade_positivi = 0
trade_negativi = 0

profitto_totale = 0

for riga in righe[-15:]:

    try:

        # =========================
        # ESTRATTI DATI
        # =========================

        match_nome = re.search(
            r"\|\s(.+?)\s\(([A-Z0-9]+)\)",
            riga
        )

        match_prezzo = re.search(
            r"Prezzo ingresso: \$([0-9\.]+)",
            riga
        )

        if not match_nome or not match_prezzo:
            continue

        nome = match_nome.group(1).strip()
        simbolo = match_nome.group(2).lower()

        prezzo_ingresso = float(
            match_prezzo.group(1)
        )

        # =========================
        # CERCA COIN
        # =========================

        search_response = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": simbolo},
            timeout=10
        )

        search_data = search_response.json()

        risultati = search_data.get(
            "coins",
            []
        )

        if len(risultati) == 0:
            continue

        coin_id = risultati[0]["id"]

        # =========================
        # PREZZO LIVE
        # =========================

        market_response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": coin_id
            },
            timeout=10
        )

        market_data = market_response.json()

        if len(market_data) == 0:
            continue

        prezzo_attuale = market_data[0].get(
            "current_price"
        )

        if prezzo_attuale is None:
            continue

        # =========================
        # PERFORMANCE REALE
        # =========================

        investimento = 100

        quantita = investimento / prezzo_ingresso

        valore_attuale = (
            quantita * prezzo_attuale
        )

        profitto = (
            valore_attuale - investimento
        )

        percentuale = (
            (profitto / investimento) * 100
        )

        trade_totali += 1

        profitto_totale += profitto

        if profitto > 0:

            trade_positivi += 1
            stato = "🟢 PROFITTO"

        else:

            trade_negativi += 1
            stato = "🔴 PERDITA"

        # =========================
        # OUTPUT
        # =========================

        print(
            f"{nome} "
            f"({simbolo.upper()})"
        )

        print(
            f"Entrata reale: "
            f"${round(prezzo_ingresso, 6)}"
        )

        print(
            f"Prezzo attuale: "
            f"${round(prezzo_attuale, 6)}"
        )

        print(
            f"Performance: "
            f"{round(percentuale, 2)}%"
        )

        print(f"Stato: {stato}")

        print("----------------------")

    except Exception as e:

        print("Errore:")
        print(e)
        print("----------------------")

# =========================
# RISULTATI FINALI
# =========================

print("\n==============================")
print(" RISULTATI REALI")
print("==============================\n")

print(f"Trade totali: {trade_totali}")
print(f"Trade positivi: {trade_positivi}")
print(f"Trade negativi: {trade_negativi}")

if trade_totali > 0:

    precisione = (
        trade_positivi / trade_totali
    ) * 100

    print(
        f"Precisione reale: "
        f"{round(precisione, 2)}%"
    )

print(
    f"Profitto reale totale: "
    f"${round(profitto_totale, 2)}"
)

# =========================
# SALVA REPORT
# =========================

timestamp = datetime.datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

with open(
    "real_performance.txt",
    "a",
    encoding="utf-8"
) as file:

    file.write(
        "\n==============================\n"
    )

    file.write(
        f"REAL PERFORMANCE: {timestamp}\n"
    )

    file.write(
        "==============================\n\n"
    )

    file.write(
        f"Trade totali: {trade_totali}\n"
    )

    file.write(
        f"Trade positivi: {trade_positivi}\n"
    )

    file.write(
        f"Trade negativi: {trade_negativi}\n"
    )

    if trade_totali > 0:

        precisione = (
            trade_positivi / trade_totali
        ) * 100

        file.write(
            f"Precisione reale: "
            f"{round(precisione, 2)}%\n"
        )

    file.write(
        f"Profitto reale totale: "
        f"${round(profitto_totale, 2)}\n"
    )

    file.write("\n")

print("\nTracking reale completato.\n")