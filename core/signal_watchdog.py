# signal_watchdog.py

import json
import os
from datetime import datetime
from telegram_alerts import send_telegram_message


HISTORY_FILE = "jarvis_signal_history.json"
MAX_DUPLICATES_ALLOWED = 2
MIN_SCORE_ALLOWED = 75


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if content == "":
                return []

            data = json.loads(content)
            if isinstance(data, list):
                return data

            return []
    except Exception as e:
        print("Errore lettura storico:", e)
        return []


def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Errore salvataggio storico:", e)


def get_symbol(signal):
    return str(signal.get("symbol", "UNKNOWN")).upper().strip()


def get_score(signal):
    try:
        return float(signal.get("score", 0) or 0)
    except Exception:
        return 0


def build_duplicate_report(history):
    counts = {}

    for signal in history:
        symbol = get_symbol(signal)
        counts[symbol] = counts.get(symbol, 0) + 1

    duplicates = {
        symbol: count
        for symbol, count in counts.items()
        if count > MAX_DUPLICATES_ALLOWED
    }

    return duplicates


def build_bad_signals(history):
    bad = []

    for signal in history:
        score = get_score(signal)

        if score < MIN_SCORE_ALLOWED:
            bad.append(signal)

    return bad


def clean_duplicates_keep_latest():
    history = load_history()

    if not history:
        print("Storico vuoto.")
        return []

    cleaned = {}
    removed = 0

    for signal in history:
        symbol = get_symbol(signal)
        reason = str(signal.get("reason", "")).upper().strip()
        source = str(signal.get("source", "")).upper().strip()

        key = f"{symbol}|{reason}|{source}"

        if key in cleaned:
            removed += 1

        cleaned[key] = signal

    new_history = list(cleaned.values())

    save_history(new_history)

    print(f"Pulizia completata. Rimossi duplicati: {removed}")

    return new_history


def build_watchdog_report():
    history = load_history()

    if not history:
        return """
🐶 JARVIS SIGNAL WATCHDOG

Status:
EMPTY

Nessun segnale nello storico.
"""

    duplicates = build_duplicate_report(history)
    bad_signals = build_bad_signals(history)

    status = "OK"

    if duplicates or bad_signals:
        status = "WARNING"

    message = f"""
🐶 JARVIS SIGNAL WATCHDOG

Status:
{status}

Totale segnali nello storico:
{len(history)}

Duplicati sopra soglia:
{len(duplicates)}

Segnali sotto score {MIN_SCORE_ALLOWED}:
{len(bad_signals)}

Time:
{datetime.now().isoformat()}
"""

    if duplicates:
        message += "\nDuplicati trovati:\n"
        for symbol, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
            message += f"- {symbol}: {count} volte\n"

    if bad_signals:
        message += "\nBug / score bassi:\n"
        for signal in bad_signals[:10]:
            message += f"- {get_symbol(signal)} score {get_score(signal)}\n"

    message += """

Nota:
Se questi duplicati erano già nello storico prima della correzione, usa opzione 2 per pulire.
"""

    return message


def main():
    while True:
        print("""
==============================
 JARVIS SIGNAL WATCHDOG
==============================

1. Controlla storico
2. Pulisci duplicati vecchi
3. Invia report Telegram
4. Esci
""")

        choice = input("Scelta: ").strip()

        if choice == "1":
            print(build_watchdog_report())

        elif choice == "2":
            clean_duplicates_keep_latest()

        elif choice == "3":
            report = build_watchdog_report()
            print(report)
            send_telegram_message(report)

        elif choice == "4":
            break

        else:
            print("Scelta non valida.")


if __name__ == "__main__":
    main()