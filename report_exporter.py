# report_exporter.py
# JARVIS REPORT EXPORTER

import json
import csv
import os
import datetime

TRADING_FILE = "unified_paper_trades.json"

REPORT_FOLDER = "reports"

# =========================
# CREATE REPORT FOLDER
# =========================

def ensure_report_folder():

    if not os.path.exists(REPORT_FOLDER):

        os.makedirs(REPORT_FOLDER)

# =========================
# LOAD DATA
# =========================

def load_trading_data():

    if not os.path.exists(TRADING_FILE):

        return None

    with open(TRADING_FILE, "r") as file:

        return json.load(file)

# =========================
# EXPORT JSON
# =========================

def export_json_report(data):

    ensure_report_folder()

    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{REPORT_FOLDER}/"
        f"jarvis_report_{timestamp}.json"
    )

    with open(filename, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )

    print(f"\nJSON report salvato:")
    print(filename)

# =========================
# EXPORT CSV
# =========================

def export_csv_report(data):

    ensure_report_folder()

    timestamp = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{REPORT_FOLDER}/"
        f"jarvis_report_{timestamp}.csv"
    )

    closed_trades = data.get(
        "closed_trades",
        []
    )

    if len(closed_trades) == 0:

        print("\nNessun trade chiuso.")
        return

    with open(
        filename,
        "w",
        newline=""
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([

            "symbol",
            "source",
            "score",
            "entry_price",
            "close_price",
            "final_pnl",
            "take_profit",
            "stop_loss",
            "close_reason",
            "duration_minutes",
            "opened_at",
            "closed_at"

        ])

        for trade in closed_trades:

            writer.writerow([

                trade.get("symbol"),

                trade.get("source"),

                trade.get("score"),

                trade.get("entry_price"),

                trade.get("close_price"),

                trade.get("final_pnl"),

                trade.get("take_profit"),

                trade.get("stop_loss"),

                trade.get("close_reason"),

                trade.get("duration_minutes"),

                trade.get("opened_at"),

                trade.get("closed_at")

            ])

    print(f"\nCSV report salvato:")
    print(filename)

# =========================
# SUMMARY
# =========================

def print_summary(data):

    stats = data.get(
        "stats",
        {}
    )

    print("\n==============================")
    print(" JARVIS PERFORMANCE SUMMARY")
    print("==============================\n")

    print(
        "Total Opened:",
        stats.get(
            "total_opened",
            0
        )
    )

    print(
        "Total Closed:",
        stats.get(
            "total_closed",
            0
        )
    )

    print(
        "Wins:",
        stats.get(
            "wins",
            0
        )
    )

    print(
        "Losses:",
        stats.get(
            "losses",
            0
        )
    )

    total_closed = stats.get(
        "total_closed",
        0
    )

    wins = stats.get(
        "wins",
        0
    )

    if total_closed > 0:

        winrate = (
            wins / total_closed
        ) * 100

    else:

        winrate = 0

    print(
        "Win Rate:",
        round(winrate, 2),
        "%"
    )

    print(
        "Profit Total:",
        round(
            stats.get(
                "profit_total",
                0
            ),
            2
        ),
        "%"
    )

# =========================
# RUN EXPORTER
# =========================

def run_exporter():

    print("\n==============================")
    print(" JARVIS REPORT EXPORTER")
    print("==============================\n")

    data = load_trading_data()

    if data is None:

        print(
            "Trading file non trovato."
        )

        return

    print_summary(data)

    export_json_report(data)

    export_csv_report(data)

    print("\nExport completato.\n")

# =========================
# START
# =========================

if __name__ == "__main__":

    run_exporter()