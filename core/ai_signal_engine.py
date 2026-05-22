# core/ai_signal_engine.py

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from datetime import datetime

from engines.early_gem_detector import scan_once
from core.telegram_alerts import send_telegram_message


MIN_AI_SCORE = 70


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calculate_ai_score(card):
    base_score = safe_float(card.get("score"))
    liquidity = safe_float(card.get("liquidity"))
    volume = safe_float(card.get("volume_24h"))
    change_1h = safe_float(card.get("change_1h"))
    change_6h = safe_float(card.get("change_6h"))
    change_24h = safe_float(card.get("change_24h"))
    fdv = safe_float(card.get("fdv"))

    score = base_score
    reasons = []

    if liquidity >= 50000:
        score += 8
        reasons.append("liquidità buona")

    if volume >= 50000:
        score += 8
        reasons.append("volume interessante")

    if 2 <= change_1h <= 20:
        score += 8
        reasons.append("momentum 1h sano")

    if 3 <= change_6h <= 35:
        score += 6
        reasons.append("trend 6h positivo")

    if 0 <= change_24h <= 45:
        score += 5
        reasons.append("24h non troppo pompato")

    if fdv > 0 and fdv <= 50_000_000:
        score += 5
        reasons.append("FDV accettabile")

    if change_24h > 70:
        score -= 20
        reasons.append("pump 24h troppo alto")

    if liquidity < 15000:
        score -= 15
        reasons.append("liquidità bassa")

    score = max(0, min(round(score), 100))

    if score >= 90:
        category = "HIGH_CONVICTION"
    elif score >= 80:
        category = "GOOD_SIGNAL"
    elif score >= 70:
        category = "WATCHLIST"
    else:
        category = "LOW_QUALITY"

    return {
        "score": score,
        "final_score": score,
        "category": category,
        "probability": score,
        "reason": ", ".join(reasons) if reasons else "score base",
    }


def format_ai_signal(card, final):
    return f"""
🧠 JARVIS AI SIGNAL

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

AI Score:
{final.get("final_score")}/100

Category:
{final.get("category")}

Probability:
{final.get("probability")}%

Reason:
{final.get("reason")}

Liquidity:
${round(safe_float(card.get("liquidity")), 2)}

Volume 24H:
${round(safe_float(card.get("volume_24h")), 2)}

1H:
{card.get("change_1h", "N/A")}%

24H:
{card.get("change_24h", "N/A")}%

FDV:
${round(safe_float(card.get("fdv")), 2)}

Chart:
{card.get("url")}

Time:
{datetime.now().isoformat()}

⚠️ Non è consiglio finanziario.
"""


def run_ai_signal_engine(send_telegram=True):
    print("\n==============================")
    print(" JARVIS AI SIGNAL ENGINE")
    print("==============================\n")

    candidates = scan_once(
        send_telegram=False
    )

    if not candidates:
        message = "📭 AI Signal Engine: nessun candidato trovato."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    results = []

    for card in candidates:
        final = calculate_ai_score(card)

        if safe_float(final.get("final_score")) < MIN_AI_SCORE:
            continue

        item = {
            "card": card,
            "final": final,
        }

        results.append(item)

    results = sorted(
        results,
        key=lambda x: x["final"].get("final_score", 0),
        reverse=True
    )

    if not results:
        message = "📭 AI Signal Engine: nessun segnale sopra soglia."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    for item in results[:5]:
        card = item.get("card", {})
        final = item.get("final", {})

        print("\n------------------------------")
        print(f"{card.get('name')} ({card.get('symbol')})")
        print(f"AI Score: {final.get('final_score')}")
        print(f"Category: {final.get('category')}")

        if send_telegram:
            send_telegram_message(
                format_ai_signal(card, final)
            )

    return results


def main():
    run_ai_signal_engine(
        send_telegram=True
    )


if __name__ == "__main__":
    main()