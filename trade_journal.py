# trade_journal.py

import json
import os
from datetime import datetime

from telegram_alerts import send_telegram_message


JOURNAL_FILE = "trade_journal.json"


def load_trades():
    if not os.path.exists(JOURNAL_FILE):
        return []

    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as file:

            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception as e:
        print("Errore caricamento journal:", e)
        return []


def save_trades(trades):
    try:
        with open(JOURNAL_FILE, "w", encoding="utf-8") as file:
            json.dump(trades, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print("Errore salvataggio journal:", e)


def calculate_trade_pnl(entry_price, exit_price, amount):
    invested = entry_price * amount
    final_value = exit_price * amount

    pnl = final_value - invested

    pnl_percent = 0

    if invested > 0:
        pnl_percent = (pnl / invested) * 100

    return {
        "invested": invested,
        "final_value": final_value,
        "pnl": pnl,
        "pnl_percent": pnl_percent,
    }


def add_trade():
    trades = load_trades()

    print("\n==============================")
    print(" ADD NEW TRADE")
    print("==============================\n")

    symbol = input("Token symbol: ").strip().upper()

    entry_price = float(input("Entry price USD: ").strip())
    exit_price = float(input("Exit price USD: ").strip())
    amount = float(input("Amount: ").strip())

    setup_type = input(
        "Setup type (EARLY_GEM / MOMENTUM / SWING / SCALP): "
    ).strip().upper()

    notes = input("Notes: ").strip()

    pnl_data = calculate_trade_pnl(
        entry_price=entry_price,
        exit_price=exit_price,
        amount=amount,
    )

    trade = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "amount": amount,
        "setup_type": setup_type,
        "notes": notes,
        "invested": pnl_data["invested"],
        "final_value": pnl_data["final_value"],
        "pnl": pnl_data["pnl"],
        "pnl_percent": pnl_data["pnl_percent"],
    }

    trades.append(trade)

    save_trades(trades)

    print("\nTrade salvato.\n")

    return trade


def build_statistics():
    trades = load_trades()

    if not trades:
        return None

    total_trades = len(trades)

    wins = 0
    losses = 0

    total_pnl = 0

    best_trade = None
    worst_trade = None

    for trade in trades:

        pnl = trade.get("pnl", 0)

        total_pnl += pnl

        if pnl >= 0:
            wins += 1
        else:
            losses += 1

        if best_trade is None or pnl > best_trade.get("pnl", -999999):
            best_trade = trade

        if worst_trade is None or pnl < worst_trade.get("pnl", 999999):
            worst_trade = trade

    win_rate = 0

    if total_trades > 0:
        win_rate = (wins / total_trades) * 100

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
    }


def build_report():
    stats = build_statistics()

    if not stats:
        return """
📭 Nessun trade nel journal ancora.
"""

    best_trade = stats.get("best_trade", {})
    worst_trade = stats.get("worst_trade", {})

    return f"""
📓 JARVIS TRADE JOURNAL

Total Trades:
{stats.get("total_trades")}

Wins:
{stats.get("wins")}

Losses:
{stats.get("losses")}

Win Rate:
{round(stats.get("win_rate"), 2)}%

Total PNL:
${round(stats.get("total_pnl"), 2)}

🏆 Best Trade:
{best_trade.get("symbol")} ({round(best_trade.get("pnl_percent", 0), 2)}%)

💀 Worst Trade:
{worst_trade.get("symbol")} ({round(worst_trade.get("pnl_percent", 0), 2)}%)

Updated:
{datetime.now().isoformat()}
"""


def show_last_trades(limit=5):
    trades = load_trades()

    if not trades:
        print("Nessun trade salvato.")
        return

    print("\n==============================")
    print(" LAST TRADES")
    print("==============================\n")

    for trade in trades[-limit:]:

        print(f"Token: {trade.get('symbol')}")
        print(f"Entry: ${trade.get('entry_price')}")
        print(f"Exit: ${trade.get('exit_price')}")
        print(f"PNL: ${round(trade.get('pnl', 0), 2)}")
        print(f"PNL %: {round(trade.get('pnl_percent', 0), 2)}%")
        print(f"Setup: {trade.get('setup_type')}")
        print("------------------------------")


def send_statistics_to_telegram():
    report = build_report()

    print(report)

    send_telegram_message(report)


def main():

    while True:

        print("""
==============================
 JARVIS TRADE JOURNAL
==============================

1. Add trade
2. Show statistics
3. Show last trades
4. Send statistics Telegram
5. Exit
""")

        choice = input("Choice: ").strip()

        if choice == "1":
            add_trade()

        elif choice == "2":
            report = build_report()
            print(report)

        elif choice == "3":
            show_last_trades()

        elif choice == "4":
            send_statistics_to_telegram()

        elif choice == "5":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()