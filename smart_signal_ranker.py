# smart_signal_ranker.py

from datetime import datetime

from signal_reporter import run_signal_reporter
from telegram_alerts import send_telegram_message


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calculate_rank_score(item):
    card = item.get("card", {})
    final = item.get("final", {})
    plan = item.get("plan", {})

    ai_score = safe_float(final.get("final_score"))
    liquidity = safe_float(card.get("liquidity"))
    volume = safe_float(card.get("volume_24h"))
    fdv = safe_float(card.get("fdv"))
    change_24h = safe_float(card.get("change_24h"))

    rank_score = ai_score

    rank_score += min(liquidity / 10000, 20)
    rank_score += min(volume / 20000, 20)

    if fdv <= 10000000:
        rank_score += 15

    if 0 <= change_24h <= 20:
        rank_score += 10

    if change_24h > 40:
        rank_score -= 20

    return round(rank_score, 2)


def build_ranked_signals():
    reports = run_signal_reporter(send_telegram=False)

    if not reports:
        return []

    ranked = []

    for item in reports:
        score = calculate_rank_score(item)

        ranked.append({
            "item": item,
            "rank_score": score,
        })

    ranked = sorted(
        ranked,
        key=lambda x: x["rank_score"],
        reverse=True,
    )

    return ranked


def format_rank_message(position, ranked_item):
    item = ranked_item.get("item", {})

    card = item.get("card", {})
    final = item.get("final", {})
    plan = item.get("plan", {})

    return f"""
🏆 JARVIS SMART SIGNAL RANKER

Position:
#{position}

Token:
{card.get("name")} ({card.get("symbol")})

Rank Score:
{ranked_item.get("rank_score")}

AI Score:
{final.get("final_score")}/100

Entry:
${plan.get("entry")}

TP1:
${round(safe_float(plan.get("take_profit_1")), 10)}

TP2:
${round(safe_float(plan.get("take_profit_2")), 10)}

Liquidity:
${round(safe_float(card.get("liquidity")), 2)}

Volume:
${round(safe_float(card.get("volume_24h")), 2)}

24H:
{card.get("change_24h")}%

FDV:
${round(safe_float(card.get("fdv")), 2)}

Chart:
{card.get("url")}

Generated:
{datetime.now().isoformat()}
"""


def run_smart_ranker(send_telegram=True):
    print("\n==============================")
    print(" JARVIS SMART SIGNAL RANKER")
    print("==============================\n")

    ranked = build_ranked_signals()

    if not ranked:
        message = "📭 Nessun segnale da classificare."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    for index, ranked_item in enumerate(ranked[:5], start=1):
        message = format_rank_message(index, ranked_item)

        print(message)

        if send_telegram:
            send_telegram_message(message)

    return ranked


def main():
    run_smart_ranker(send_telegram=True)


if __name__ == "__main__":
    main()