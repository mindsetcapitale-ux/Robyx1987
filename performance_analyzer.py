# performance_analyzer.py

from datetime import datetime
from collections import defaultdict

from trade_journal import load_trades
from telegram_alerts import send_telegram_message


def calculate_performance():
    trades = load_trades()

    if not trades:
        return None

    total_trades = len(trades)
    wins = 0
    losses = 0
    total_pnl = 0

    setup_stats = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "pnl": 0
    })

    symbol_stats = defaultdict(lambda: {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "pnl": 0
    })

    best_trade = None
    worst_trade = None

    for trade in trades:
        pnl = float(trade.get("pnl", 0))
        symbol = trade.get("symbol", "UNKNOWN")
        setup = trade.get("setup_type", "UNKNOWN")

        total_pnl += pnl

        if pnl >= 0:
            wins += 1
        else:
            losses += 1

        setup_stats[setup]["trades"] += 1
        setup_stats[setup]["pnl"] += pnl

        symbol_stats[symbol]["trades"] += 1
        symbol_stats[symbol]["pnl"] += pnl

        if pnl >= 0:
            setup_stats[setup]["wins"] += 1
            symbol_stats[symbol]["wins"] += 1
        else:
            setup_stats[setup]["losses"] += 1
            symbol_stats[symbol]["losses"] += 1

        if best_trade is None or pnl > float(best_trade.get("pnl", 0)):
            best_trade = trade

        if worst_trade is None or pnl < float(worst_trade.get("pnl", 0)):
            worst_trade = trade

    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "setup_stats": setup_stats,
        "symbol_stats": symbol_stats,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
    }


def format_group_stats(title, stats):
    if not stats:
        return f"\n{title}\nNessun dato.\n"

    rows = f"\n{title}\n"

    sorted_items = sorted(
        stats.items(),
        key=lambda item: item[1]["pnl"],
        reverse=True
    )

    for name, data in sorted_items:
        trades = data["trades"]
        wins = data["wins"]
        pnl = data["pnl"]

        win_rate = (wins / trades) * 100 if trades > 0 else 0

        rows += f"""
{name}
Trades: {trades}
Win Rate: {round(win_rate, 2)}%
PNL: ${round(pnl, 2)}
"""

    return rows


def build_performance_report():
    performance = calculate_performance()

    if not performance:
        return """
📭 JARVIS PERFORMANCE ANALYZER

Nessun trade disponibile.
Aggiungi trade con trade_journal.py.
"""

    best_trade = performance.get("best_trade", {})
    worst_trade = performance.get("worst_trade", {})

    report = f"""
📊 JARVIS PERFORMANCE ANALYZER

Total Trades:
{performance.get("total_trades")}

Wins:
{performance.get("wins")}

Losses:
{performance.get("losses")}

Win Rate:
{round(performance.get("win_rate"), 2)}%

Total PNL:
${round(performance.get("total_pnl"), 2)}

🏆 Best Trade:
{best_trade.get("symbol")} | ${round(best_trade.get("pnl", 0), 2)} | {round(best_trade.get("pnl_percent", 0), 2)}%

💀 Worst Trade:
{worst_trade.get("symbol")} | ${round(worst_trade.get("pnl", 0), 2)} | {round(worst_trade.get("pnl_percent", 0), 2)}%

Updated:
{datetime.now().isoformat()}
"""

    report += format_group_stats(
        "\n📌 PERFORMANCE BY SETUP",
        performance.get("setup_stats")
    )

    report += format_group_stats(
        "\n💎 PERFORMANCE BY SYMBOL",
        performance.get("symbol_stats")
    )

    return report


def send_performance_report():
    report = build_performance_report()

    print(report)

    send_telegram_message(report)


def main():
    send_performance_report()


if __name__ == "__main__":
    main()