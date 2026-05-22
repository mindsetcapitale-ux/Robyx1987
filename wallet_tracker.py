# wallet_tracker.py

import requests
from telegram_alerts import send_telegram_message


RPC_URL = "https://eth.llamarpc.com"


def is_valid_wallet(address):
    return address.startswith("0x") and len(address) == 42


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
        eth_balance = wei_balance / 10**18

        return eth_balance

    except Exception as e:
        print("Errore balance:", e)
        return None


def build_wallet_report(address):
    balance = get_eth_balance(address)

    if balance is None:
        return f"""
❌ JARVIS WALLET TRACKER

Wallet:
{address}

Errore:
Impossibile leggere il saldo.
"""

    return f"""
👛 JARVIS WALLET TRACKER

Wallet:
{address}

ETH Balance:
{balance} ETH

Nota:
Versione senza API key. Legge il saldo ETH via RPC pubblico.
"""


def scan_wallet(address, send_telegram=True):
    if not is_valid_wallet(address):
        print("Wallet non valido.")
        return

    report = build_wallet_report(address)

    print(report)

    if send_telegram:
        send_telegram_message(report)


def main():
    print("\n==============================")
    print(" JARVIS WALLET TRACKER")
    print("==============================\n")

    address = input("Inserisci wallet address 0x: ").strip()

    scan_wallet(address, send_telegram=True)


if __name__ == "__main__":
    main()