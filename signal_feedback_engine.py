# signal_feedback_engine.py

import json
import os
from datetime import datetime

from signal_history import get_last_signals
from telegram_alerts import send_telegram_message


FEEDBACK_FILE = "signal_feedback.json"


def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []

    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception as e:
        print("Errore lettura feedback:", e)
        return []


def save_feedback(feedback):
    try:
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as file:
            json.dump(feedback, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print("Errore salvataggio feedback:", e)


def show_recent_signals():
    signals = get_last_signals(10)

    print("\n==============================")
    print(" RECENT JARVIS SIGNALS")
    print("==============================\n")

    if not signals:
        print("Nessun segnale trovato nello storico.")
        return []

    for index, signal in enumerate(signals, start=1):
        print(f"{index}. {signal.get('symbol')}")
        print(f"   Score: {signal.get('score')}")
        print(f"   24H: {signal.get('change_24h')}%")
        print(f"   Reason: {signal.get('reason')}")
        print(f"   Time: {signal.get('timestamp')}")
        print("------------------------------")

    return signals


def add_feedback():
    signals = show_recent_signals()

    if not signals:
        return None

    choice = input("Scegli numero segnale da valutare: ").strip()

    try:
        index = int(choice) - 1

        if index < 0 or index >= len(signals):
            print("Numero non valido.")
            return None

    except Exception:
        print("Scelta non valida.")
        return None

    selected_signal = signals[index]

    print("""
Feedback:
1. GOOD_SIGNAL
2. FALSE_POSITIVE
3. TOO_LATE
4. TOO_RISKY
5. MISSED_OPPORTUNITY
""")

    feedback_choice = input("Scegli feedback: ").strip()

    feedback_map = {
        "1": "GOOD_SIGNAL",
        "2": "FALSE_POSITIVE",
        "3": "TOO_LATE",
        "4": "TOO_RISKY",
        "5": "MISSED_OPPORTUNITY",
    }

    feedback_type = feedback_map.get(feedback_choice)

    if not feedback_type:
        print("Feedback non valido.")
        return None

    notes = input("Note: ").strip()

    feedback = load_feedback()

    record = {
        "timestamp": datetime.now().isoformat(),
        "signal": selected_signal,
        "feedback_type": feedback_type,
        "notes": notes,
    }

    feedback.append(record)

    save_feedback(feedback)

    print("\nFeedback salvato.\n")

    return record


def analyze_feedback():
    feedback = load_feedback()

    if not feedback:
        return {
            "total": 0,
            "stats": {},
            "message": "Nessun feedback salvato."
        }

    stats = {}

    for item in feedback:
        feedback_type = item.get("feedback_type", "UNKNOWN")

        if feedback_type not in stats:
            stats[feedback_type] = 0

        stats[feedback_type] += 1

    return {
        "total": len(feedback),
        "stats": stats,
        "message": "Feedback analizzato."
    }


def build_feedback_report():
    analysis = analyze_feedback()

    if analysis.get("total") == 0:
        return """
📭 JARVIS SIGNAL FEEDBACK

Nessun feedback salvato ancora.
"""

    message = f"""
🧠 JARVIS SIGNAL FEEDBACK REPORT

Total Feedback:
{analysis.get("total")}

"""

    stats = analysis.get("stats", {})

    for key, value in stats.items():
        message += f"{key}: {value}\n"

    message += f"""

Updated:
{datetime.now().isoformat()}
"""

    return message


def send_feedback_report():
    report = build_feedback_report()

    print(report)

    send_telegram_message(report)


def main():
    while True:
        print("""
==============================
 JARVIS SIGNAL FEEDBACK ENGINE
==============================

1. Mostra ultimi segnali
2. Aggiungi feedback
3. Report feedback
4. Invia report Telegram
5. Esci
""")

        choice = input("Scelta: ").strip()

        if choice == "1":
            show_recent_signals()

        elif choice == "2":
            add_feedback()

        elif choice == "3":
            report = build_feedback_report()
            print(report)

        elif choice == "4":
            send_feedback_report()

        elif choice == "5":
            break

        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()