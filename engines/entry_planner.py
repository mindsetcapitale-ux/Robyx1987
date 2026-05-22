# engines/entry_planner.py

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

from engines.quality_filter_engine import run_quality_filter
from core.telegram_alerts import send_telegram_message


DEFAULT_STOP_LOSS_PERCENT = 8
TAKE_PROFIT_1_PERCENT = 15
TAKE_PROFIT_2_PERCENT = 30


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calculate_trade_plan(card, final):
    price = safe_float(
        card.get("price_usd", card.get("price", 0))
    )

    ai_score = safe_float(
        final.get("final_score", final.get("score", 0))
    )

    if price <= 0:
        return None

    stop_loss = price * (
        1 - DEFAULT_STOP_LOSS_PERCENT / 100
    )

    take_profit_1 = price * (
        1 + TAKE_PROFIT_1_PERCENT / 100
    )

    take_profit_2 = price * (
        1 + TAKE_PROFIT_2_PERCENT / 100
    )

    if ai_score >= 90:
        confidence = "HIGH"
    elif ai_score >= 80:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return {
        "entry": price,
        "stop_loss": stop_loss,
        "take_profit_1": take_profit_1,
        "take_profit_2": take_profit_2,
        "confidence": confidence,
    }


def format_entry_plan(card, final, plan):
    return f"""
🎯 JARVIS ENTRY PLANNER

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

AI Score:
{final.get("final_score", final.get("score", 0))}/100

Confidence:
{plan.get("confidence")}

Suggested Entry:
${plan.get("entry")}

Stop Loss:
${round(safe_float(plan.get("stop_loss")), 10)}

Take Profit 1:
${round(safe_float(plan.get("take_profit_1")), 10)}

Take Profit 2:
${round(safe_float(plan.get("take_profit_2")), 10)}

Time:
{datetime.now().isoformat()}

⚠️ Non comprare automaticamente.
"""


def run_entry_planner(send_telegram=True):
    print("\n==============================")
    print(" JARVIS ENTRY PLANNER")
    print("==============================\n")

    approved_signals = run_quality_filter(
        send_telegram=False
    )

    if not approved_signals:
        message = (
            "📭 Entry Planner: "
            "nessun segnale approvato."
        )

        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    plans = []

    for item in approved_signals:
        card = item.get("card", {})
        final = item.get("final", {})

        plan = calculate_trade_plan(
            card,
            final
        )

        if not plan:
            continue

        result = {
            "card": card,
            "final": final,
            "plan": plan,
        }

        plans.append(result)

        if send_telegram:
            send_telegram_message(
                format_entry_plan(
                    card,
                    final,
                    plan
                )
            )

    return plans


def main():
    run_entry_planner(send_telegram=True)


if __name__ == "__main__":
    main()