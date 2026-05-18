# wallet_tracker.py
# JARVIS WHALE TRACKER REALE

import requests
import datetime

from database_manager import aggiungi_wallet_activity

TRACKED_WALLETS = [

    {
        "name": "Wallet Bot 1",
        "address": "0x26ebb8213fb8d66156f1af8908d43f7e3e367c1d"
    },

    {
        "name": "Wallet Bot 2",
        "address": "0xabba7bef6dffba87d66e6c3d2d612b1a57df2303"
    }

]

# =========================
# ANALYZE TX
# =========================

def classify_whale_activity(eth_value):

    if eth_value >= 50:
        return "🔥 HUGE WHALE MOVE"

    if eth_value >= 10:
        return "🐋 WHALE ACTIVITY"

    if eth_value >= 1:
        return "⚠️ MEDIUM MOVE"

    return "👀 SMALL MOVE"

# =========================
# WALLET TRACKER
# =========================

def controlla_wallets():

    risultati = []

    for item in TRACKED_WALLETS:

        wallet = item["address"]
        name = item["name"]

        try:

            response = requests.get(
                "https://api.etherscan.io/api",
                params={
                    "module": "account",
                    "action": "txlist",
                    "address": wallet,
                    "sort": "desc"
                },
                timeout=12
            )

            data = response.json()

            txs = data.get("result", [])

            if not isinstance(txs, list) or len(txs) == 0:

                risultati.append({

                    "wallet": wallet,
                    "name": name,
                    "eth": 0,
                    "status": "NO DATA",
                    "time": "-"

                })

                continue

            last_tx = txs[0]

            eth_value = int(
                last_tx.get("value", 0)
            ) / 1e18

            timestamp = last_tx.get(
                "timeStamp",
                "0"
            )

            try:

                time_readable = datetime.datetime.fromtimestamp(
                    int(timestamp)
                ).strftime("%Y-%m-%d %H:%M:%S")

            except:

                time_readable = "-"

            status = classify_whale_activity(
                eth_value
            )

            result = {

                "wallet": wallet,
                "name": name,
                "eth": round(eth_value, 4),
                "status": status,
                "time": time_readable

            }

            risultati.append(
                result
            )

            if eth_value >= 1:

                aggiungi_wallet_activity({

                    "wallet": wallet,
                    "name": name,
                    "eth": round(eth_value, 4),
                    "status": status,
                    "time": time_readable

                })

        except Exception as e:

            risultati.append({

                "wallet": wallet,
                "name": name,
                "eth": 0,
                "status": f"ERROR: {e}",
                "time": "-"

            })

    return risultati

# =========================
# TEST
# =========================

if __name__ == "__main__":

    dati = controlla_wallets()

    print("\n=== JARVIS WHALE TRACKER ===\n")

    for w in dati:

        print(
            w["name"],
            "|",
            w["wallet"],
            "| ETH:",
            w["eth"],
            "|",
            w["status"],
            "|",
            w["time"]
        )