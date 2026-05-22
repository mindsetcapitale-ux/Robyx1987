# jarvis_logger.py

import json
import os
from datetime import datetime


LOG_FILE = "jarvis_events_log.json"


def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return []

            data = json.loads(content)

            if isinstance(data, list):
                return data

            return []

    except Exception:
        return []


def save_logs(logs):
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Errore salvataggio log:", e)


def log_event(event_type, message, data=None):
    logs = load_logs()

    record = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "message": message,
        "data": data if data is not None else {},
    }

    logs.append(record)

    save_logs(logs)

    print(f"[{event_type}] {message}")


def get_last_logs(limit=20):
    logs = load_logs()
    return logs[-limit:]


def print_last_logs(limit=20):
    logs = get_last_logs(limit)

    print("\n==============================")
    print(" JARVIS EVENTS LOG")
    print("==============================\n")

    if not logs:
        print("Nessun log ancora.")
        return

    for log in logs:
        print(f"Time: {log.get('timestamp')}")
        print(f"Type: {log.get('event_type')}")
        print(f"Message: {log.get('message')}")
        print(f"Data: {log.get('data')}")
        print("------------------------------")


def clear_logs():
    save_logs([])
    print("Log cancellati.")


if __name__ == "__main__":
    print_last_logs()