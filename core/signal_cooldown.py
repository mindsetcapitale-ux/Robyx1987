# signal_cooldown.py

import json
import os
import threading
from datetime import datetime, timedelta


COOLDOWN_FILE = "signal_cooldown.json"
COOLDOWN_HOURS = 6

LOCK = threading.Lock()


def build_cooldown_key(symbol, chain="", category=""):
    symbol = str(symbol).upper().strip()
    chain = str(chain).lower().strip()
    category = str(category).upper().strip()

    return f"{symbol}|{chain}|{category}"


def load_cooldowns():
    if not os.path.exists(COOLDOWN_FILE):
        return {}

    try:
        with open(COOLDOWN_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return {}

            data = json.loads(content)

            if isinstance(data, dict):
                return data

            return {}

    except Exception:
        return {}


def save_cooldowns(data):
    with open(COOLDOWN_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def can_send_signal(symbol, chain="", category=""):
    with LOCK:
        cooldowns = load_cooldowns()
        key = build_cooldown_key(symbol, chain, category)

        if key not in cooldowns:
            return True

        try:
            last_time = datetime.fromisoformat(cooldowns[key])
            next_allowed = last_time + timedelta(hours=COOLDOWN_HOURS)

            return datetime.now() >= next_allowed

        except Exception:
            return True


def mark_signal_sent(symbol, chain="", category=""):
    with LOCK:
        cooldowns = load_cooldowns()
        key = build_cooldown_key(symbol, chain, category)

        cooldowns[key] = datetime.now().isoformat()

        save_cooldowns(cooldowns)


def check_and_mark_signal(symbol, chain="", category=""):
    with LOCK:
        cooldowns = load_cooldowns()
        key = build_cooldown_key(symbol, chain, category)

        if key in cooldowns:
            try:
                last_time = datetime.fromisoformat(cooldowns[key])
                next_allowed = last_time + timedelta(hours=COOLDOWN_HOURS)

                if datetime.now() < next_allowed:
                    return False

            except Exception:
                pass

        cooldowns[key] = datetime.now().isoformat()
        save_cooldowns(cooldowns)

        return True


def reset_cooldowns():
    save_cooldowns({})
    print("Cooldown resettati.")


def print_cooldowns():
    cooldowns = load_cooldowns()

    print("\n==============================")
    print(" JARVIS SIGNAL COOLDOWNS")
    print("==============================\n")

    if not cooldowns:
        print("Nessun cooldown attivo.")
        return

    for key, timestamp in cooldowns.items():
        print(f"{key}: {timestamp}")


if __name__ == "__main__":
    print_cooldowns()