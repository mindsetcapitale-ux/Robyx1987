# database_manager.py

import json
import os
import datetime

DATABASE_FILE = "jarvis_database.json"

# =========================
# CREATE DATABASE
# =========================

def inizializza_database():

    if not os.path.exists(DATABASE_FILE):

        struttura = {

            "portfolio": [],
            "signals": [],
            "wallet_activity": [],
            "news_history": [],
            "ml_memory": {

                "average_ai": 60,
                "successful_signals": 0,
                "failed_signals": 0

            }

        }

        with open(
            DATABASE_FILE,
            "w"
        ) as file:

            json.dump(
                struttura,
                file,
                indent=4
            )

# =========================
# LOAD DATABASE
# =========================

def carica_database():

    inizializza_database()

    with open(
        DATABASE_FILE,
        "r"
    ) as file:

        return json.load(file)

# =========================
# SAVE DATABASE
# =========================

def salva_database(data):

    with open(
        DATABASE_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

# =========================
# ADD SIGNAL
# =========================

def aggiungi_signal(signal):

    data = carica_database()

    signal["timestamp"] = str(
        datetime.datetime.now()
    )

    data["signals"].append(
        signal
    )

    salva_database(data)

# =========================
# ADD WALLET ACTIVITY
# =========================

def aggiungi_wallet_activity(activity):

    data = carica_database()

    activity["timestamp"] = str(
        datetime.datetime.now()
    )

    data["wallet_activity"].append(
        activity
    )

    salva_database(data)

# =========================
# ADD NEWS
# =========================

def aggiungi_news(news):

    data = carica_database()

    news["timestamp"] = str(
        datetime.datetime.now()
    )

    data["news_history"].append(
        news
    )

    salva_database(data)

# =========================
# UPDATE ML MEMORY
# =========================

def aggiorna_ml_memory(memory):

    data = carica_database()

    data["ml_memory"] = memory

    salva_database(data)

# =========================
# SAVE PORTFOLIO
# =========================

def salva_portfolio(portfolio):

    data = carica_database()

    data["portfolio"] = portfolio

    salva_database(data)

# =========================
# LOAD PORTFOLIO
# =========================

def carica_portfolio():

    data = carica_database()

    return data["portfolio"]

# =========================
# START
# =========================

inizializza_database()