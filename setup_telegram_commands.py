# setup_telegram_commands.py

import requests
from telegram_alerts import BOT_TOKEN


def setup_commands():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"

    commands = [
        {"command": "start", "description": "Avvia Jarvis"},
        {"command": "status", "description": "Stato sistema"},
        {"command": "signals", "description": "Smart AI signals"},
        {"command": "momentum", "description": "Live momentum scanner"},
        {"command": "learn", "description": "Adaptive learning report"},
        {"command": "history", "description": "Storico segnali"},
        {"command": "scan", "description": "Market scan"},
        {"command": "gems", "description": "Early gems"},
        {"command": "btc", "description": "Bitcoin analysis"},
        {"command": "eth", "description": "Ethereum analysis"},
        {"command": "sol", "description": "Solana analysis"},
    ]

    response = requests.post(
        url,
        json={"commands": commands},
        timeout=20
    )

    print(response.json())


if __name__ == "__main__":
    setup_commands()