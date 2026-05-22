# adaptive_learning_engine.py

import json
import os
from datetime import datetime


WEIGHTS_FILE = "adaptive_weights.json"
FEEDBACK_FILE = "signal_feedback.json"
TRADE_JOURNAL_FILE = "trade_journal.json"


DEFAULT_WEIGHTS = {
    "base_score": 1.0,
    "liquidity": 1.0,
    "volume": 1.0,
    "momentum_1h": 1.0,
    "momentum_6h": 1.0,
    "momentum_24h": 1.0,
    "fdv": 1.0,
    "risk_penalty": 1.0,
    "last_updated": None
}


def load_json(file_path, default):
    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if content == "":
                return default

            return json.loads(content)

    except Exception:
        return default


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_weights():
    weights = load_json(WEIGHTS_FILE, DEFAULT_WEIGHTS.copy())

    for key, value in DEFAULT_WEIGHTS.items():
        if key not in weights:
            weights[key] = value

    return weights


def save_weights(weights):
    weights["last_updated"] = datetime.now().isoformat()
    save_json(WEIGHTS_FILE, weights)


def clamp(value, minimum=0.5, maximum=1.8):
    return max(minimum, min(value, maximum))


def apply_feedback_learning(weights):
    feedback = load_json(FEEDBACK_FILE, [])

    if not isinstance(feedback, list) or len(feedback) == 0:
        return weights

    recent_feedback = feedback[-50:]

    good = 0
    bad = 0
    too_late = 0
    too_risky = 0

    for item in recent_feedback:
        feedback_type = item.get("feedback_type", "")

        if feedback_type == "GOOD_SIGNAL":
            good += 1

        elif feedback_type == "FALSE_POSITIVE":
            bad += 1

        elif feedback_type == "TOO_LATE":
            too_late += 1

        elif feedback_type == "TOO_RISKY":
            too_risky += 1

    if good > bad:
        weights["base_score"] = clamp(weights["base_score"] + 0.05)
        weights["momentum_6h"] = clamp(weights["momentum_6h"] + 0.05)

    if bad > good:
        weights["base_score"] = clamp(weights["base_score"] - 0.05)
        weights["risk_penalty"] = clamp(weights["risk_penalty"] + 0.08)

    if too_late > 0:
        weights["momentum_1h"] = clamp(weights["momentum_1h"] + 0.08)
        weights["momentum_24h"] = clamp(weights["momentum_24h"] - 0.05)

    if too_risky > 0:
        weights["liquidity"] = clamp(weights["liquidity"] + 0.08)
        weights["risk_penalty"] = clamp(weights["risk_penalty"] + 0.08)

    return weights


def apply_trade_learning(weights):
    trades = load_json(TRADE_JOURNAL_FILE, [])

    if not isinstance(trades, list) or len(trades) == 0:
        return weights

    recent_trades = trades[-50:]

    winning_trades = []
    losing_trades = []

    for trade in recent_trades:
        pnl = float(trade.get("pnl", 0) or 0)

        if pnl > 0:
            winning_trades.append(trade)
        else:
            losing_trades.append(trade)

    if len(winning_trades) > len(losing_trades):
        weights["base_score"] = clamp(weights["base_score"] + 0.04)
        weights["volume"] = clamp(weights["volume"] + 0.04)

    if len(losing_trades) > len(winning_trades):
        weights["risk_penalty"] = clamp(weights["risk_penalty"] + 0.08)
        weights["fdv"] = clamp(weights["fdv"] + 0.05)

    return weights


def update_adaptive_weights():
    weights = load_weights()

    weights = apply_feedback_learning(weights)
    weights = apply_trade_learning(weights)

    save_weights(weights)

    return weights


def calculate_adaptive_score(card, base_score):
    weights = load_weights()

    liquidity = float(card.get("liquidity", 0) or 0)
    volume = float(card.get("volume_24h", 0) or 0)
    change_1h = float(card.get("change_1h", 0) or 0)
    change_6h = float(card.get("change_6h", 0) or 0)
    change_24h = float(card.get("change_24h", 0) or 0)
    fdv = float(card.get("fdv", 0) or 0)

    score = base_score * weights["base_score"]

    if liquidity >= 50000:
        score += 5 * weights["liquidity"]

    if volume >= 100000:
        score += 5 * weights["volume"]

    if 2 <= change_1h <= 20:
        score += 6 * weights["momentum_1h"]

    if 4 <= change_6h <= 35:
        score += 5 * weights["momentum_6h"]

    if 0 <= change_24h <= 45:
        score += 4 * weights["momentum_24h"]

    if fdv > 100000000:
        score -= 8 * weights["fdv"]

    if change_24h > 70:
        score -= 12 * weights["risk_penalty"]

    score = max(0, min(round(score), 100))

    return score


def build_learning_report():
    weights = update_adaptive_weights()

    message = f"""
🧠 JARVIS ADAPTIVE LEARNING

Weights aggiornati:

Base Score:
{weights.get("base_score")}

Liquidity:
{weights.get("liquidity")}

Volume:
{weights.get("volume")}

Momentum 1H:
{weights.get("momentum_1h")}

Momentum 6H:
{weights.get("momentum_6h")}

Momentum 24H:
{weights.get("momentum_24h")}

FDV:
{weights.get("fdv")}

Risk Penalty:
{weights.get("risk_penalty")}

Updated:
{weights.get("last_updated")}
"""

    return message


def main():
    report = build_learning_report()
    print(report)


if __name__ == "__main__":
    main()