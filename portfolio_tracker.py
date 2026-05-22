# portfolio_tracker.py

import json
import os
from datetime import datetime

from telegram_alerts import send_telegram_message


PORTFOLIO_FILE = "portfolio.json"


def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []

    try:
        with open(PORTFOLIO_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def add_position():
    portfolio = load_portfolio()

    symbol = input("Coin symbol: ").strip().upper()
    amount = float(input("Amount: ").strip())
    entry_price = float(input("Entry price USD: ").strip())

    record = {
        "symbol": symbol,
        "amount": amount,
        "entry_price": entry_price,
        "created_at": datetime.now().isoformat(),
    }

    portfolio.append(record)

    save_portfolio(portfolio)

    print("Posizione salvata.")


def build_portfolio_report():
    portfolio = load_portfolio()

    if not portfolio:
        return """
📭 JARVIS PORTFOLIO TRACKER

Portfolio vuoto.
"""

    message = """
💼 JARVIS PORTFOLIO TRACKER

"""

    for position in portfolio:

        message += f"""
Coin:
{position.get("symbol")}

Amount:
{position.get("amount")}

Entry:
${position.get("entry_price")}

Created:
{position.get("created_at")}

-------------------------
"""

    return message


def send_portfolio_report():
    report = build_portfolio_report()

    print(report)

    send_telegram_message(report)


def main():
    while True:
        print("""
==============================
 JARVIS PORTFOLIO TRACKER
==============================

1. Add position
2. Show portfolio
3. Send Telegram report
4. Exit
""")

        choice = input("Choice: ").strip()

        if choice == "1":
            add_position()

        elif choice == "2":
            print(build_portfolio_report())

        elif choice == "3":
            send_portfolio_report()

        elif choice == "4":
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()