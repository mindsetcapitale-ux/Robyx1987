# smart_money_tracker.py

import json
import os
import time
import requests
from datetime import datetime

from telegram_alerts import send_telegram_message


RPC_URL = "https://eth.llamarpc.com"
STATE_FILE = "smart_money_state.json"

CHECK_INTERVAL_SECONDS = 300
ALERT_CHANGE_ETH = 0.05


WATCHED_WALLETS = [
    {
        "name": "Smart Wallet 1",
        "address": "0x26ebb8213fb8d66156f1af8908d43f7e3e367c1d"
    },
    {
        "name": "Smart Wallet 2",
        "address": "0xabba7bef6dffba87d66e6c3d2d612b1a57df2303"
    }
]


def is_valid_wallet(address):
    return isinstance(address, str) and address.startswith("0x") and len(address) == 42


def rpc_call(method, params):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    response = requests.post(RPC_URL, json=payload, timeout=20)
    return response.json()


def get_eth_balance(address):
    try:
        data = rpc_call("eth_getBalance", [address, "latest"])

        if "result" not in data:
            return None

        wei_balance = int(data["result"], 16)
        return wei_balance / 10**18

    except Exception as e:
        print("Errore balance:", e)
        return None


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return {}

            data = json.loads(content)

            if isinstance(data, dict):
                return data

            return {}

    except Exception:
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            json.dump(state, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Errore salvataggio state:", e)


def build_alert(wallet, old_balance, new_balance):
    diff = new_balance - old_balance

    direction = "INCREASE"
    emoji = "🟢"

    if diff < 0:
        direction = "DECREASE"
        emoji = "🔴"

    return f"""
🐋 JARVIS SMART MONEY ALERT

{emoji} Wallet Balance {direction}

Name:
{wallet.get("name")}

Address:
{wallet.get("address")}

Old Balance:
{old_balance} ETH

New Balance:
{new_balance} ETH

Change:
{diff} ETH

Time:
{datetime.now().isoformat()}
"""


def check_wallets_once(send_telegram=True):
    state = load_state()
    updated_state = dict(state)

    print("\n==============================")
    print(" JARVIS SMART MONEY TRACKER")
    print("==============================\n")

    for wallet in WATCHED_WALLETS:
        name = wallet.get("name")
        address = wallet.get("address", "").strip()

        if not is_valid_wallet(address):
            print(f"Wallet non valido: {name} {address}")
            continue

        new_balance = get_eth_balance(address)

        if new_balance is None:
            print(f"Impossibile leggere saldo: {name}")
            continue

        old_balance = state.get(address)

        print(f"{name}: {new_balance} ETH")

        if old_balance is None:
            updated_state[address] = new_balance
            print("Primo controllo: salvo saldo iniziale.")
            continue

        diff = abs(new_balance - old_balance)

        if diff >= ALERT_CHANGE_ETH:
            alert = build_alert(wallet, old_balance, new_balance)
            print(alert)

            if send_telegram:
                send_telegram_message(alert)

        updated_state[address] = new_balance

    save_state(updated_state)


def main():
    while True:
        check_wallets_once(send_telegram=True)

        print(f"\nAttendo {CHECK_INTERVAL_SECONDS} secondi...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()