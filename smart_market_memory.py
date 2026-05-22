# smart_market_memory.py

import json
import os
from datetime import datetime

from market_phase_engine import run_market_phase_engine
from telegram_alerts import send_telegram_message


MEMORY_FILE = "market_memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def capture_market_snapshot():
    result = run_market_phase_engine(
        send_telegram=False
    )

    if not result:
        print("Impossibile leggere mercato.")
        return None

    market = result.get("market", {})
    phase = result.get("phase", {})

    memory = load_memory()

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase.get("phase"),
        "reason": phase.get("reason"),
        "btc_price": market.get("price"),
        "btc_24h": market.get("change_24h"),
        "btc_7d": market.get("change_7d"),
    }

    memory.append(snapshot)

    save_memory(memory)

    print("Snapshot salvato.")

    return snapshot


def analyze_memory():
    memory = load_memory()

    if not memory:
        return {
            "total": 0,
            "stats": {}
        }

    stats = {}

    for item in memory:
        phase = item.get("phase", "UNKNOWN")

        if phase not in stats:
            stats[phase] = 0

        stats[phase] += 1

    return {
        "total": len(memory),
        "stats": stats
    }


def build_memory_report():
    analysis = analyze_memory()

    if analysis.get("total") == 0:
        return """
📭 SMART MARKET MEMORY

Nessun dato salvato.
"""

    message = f"""
🧠 SMART MARKET MEMORY

Snapshots:
{analysis.get("total")}

"""

    for phase, count in analysis.get("stats", {}).items():
        message += f"{phase}: {count}\n"

    message += f"""

Updated:
{datetime.now().isoformat()}
"""

    return message


def send_memory_report():
    report = build_memory_report()

    print(report)

    send_telegram_message(report)


def main():
    while True:
        print("""
==============================
 SMART MARKET MEMORY
==============================

1. Capture snapshot
2. Show report
3. Send Telegram report
4. Exit
""")

        choice = input("Choice: ").strip()

        if choice == "1":
            capture_market_snapshot()

        elif choice == "2":
            print(build_memory_report())

        elif choice == "3":
            send_memory_report()

        elif choice == "4":
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()