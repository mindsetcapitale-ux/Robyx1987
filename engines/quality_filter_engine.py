# engines/quality_filter_engine.py

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

from core.ai_signal_engine import run_ai_signal_engine
from engines.anti_scam_engine import analyze_scam_risk
from core.telegram_alerts import send_telegram_message


MIN_AI_SCORE = 75
MAX_RISK_SCORE = 50
MIN_LIQUIDITY = 30000
MIN_VOLUME_24H = 20000
MAX_PUMP_24H = 40
MAX_FDV = 100_000_000


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def passes_quality_filter(card, final, scam_analysis):
    reasons = []
    blocks = []

    ai_score = safe_float(
        final.get("final_score", final.get("score", 0))
    )

    risk_score = safe_float(
        scam_analysis.get("risk_score")
    )

    liquidity = safe_float(card.get("liquidity"))
    volume_24h = safe_float(card.get("volume_24h"))
    change_24h = safe_float(card.get("change_24h"))
    fdv = safe_float(card.get("fdv"))

    if ai_score >= MIN_AI_SCORE:
        reasons.append("AI score valido")
    else:
        blocks.append("AI score basso")

    if risk_score <= MAX_RISK_SCORE:
        reasons.append("rischio scam accettabile")
    else:
        blocks.append("rischio scam alto")

    if liquidity >= MIN_LIQUIDITY:
        reasons.append("liquidità sufficiente")
    else:
        blocks.append("liquidità troppo bassa")

    if volume_24h >= MIN_VOLUME_24H:
        reasons.append("volume sufficiente")
    else:
        blocks.append("volume troppo basso")

    if change_24h <= MAX_PUMP_24H:
        reasons.append("non troppo pompata")
    else:
        blocks.append("pump 24h troppo alto")

    if fdv <= MAX_FDV:
        reasons.append("FDV accettabile")
    else:
        blocks.append("FDV troppo alto")

    return {
        "passed": len(blocks) == 0,
        "reasons": reasons,
        "blocks": blocks,
    }


def format_quality_message(card, final, scam_analysis, quality):
    return f"""
✅ JARVIS QUALITY FILTER

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

AI Score:
{final.get("final_score", final.get("score", 0))}/100

Scam Risk:
{scam_analysis.get("risk_score")}/100 - {scam_analysis.get("risk_level")}

Liquidity:
${round(safe_float(card.get("liquidity")), 2)}

Volume 24H:
${round(safe_float(card.get("volume_24h")), 2)}

24H:
{card.get("change_24h")}%

FDV:
${round(safe_float(card.get("fdv")), 2)}

PASSED:
{quality.get("passed")}

Reasons:
{", ".join(quality.get("reasons")) if quality.get("reasons") else "N/A"}

Blocks:
{", ".join(quality.get("blocks")) if quality.get("blocks") else "Nessun blocco"}

Chart:
{card.get("url")}

Time:
{datetime.now().isoformat()}

⚠️ Non è consiglio finanziario.
"""


def run_quality_filter(send_telegram=True):
    print("\n==============================")
    print(" JARVIS QUALITY FILTER ENGINE")
    print("==============================\n")

    signals = run_ai_signal_engine(
        send_telegram=False
    )

    if not signals:
        message = "📭 Quality Filter: nessun segnale AI da filtrare."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    approved = []
    rejected = []

    for item in signals:
        card = item.get("card", {})
        final = item.get("final", {})

        scam_analysis = analyze_scam_risk(card)

        quality = passes_quality_filter(
            card,
            final,
            scam_analysis
        )

        result = {
            "card": card,
            "final": final,
            "scam_analysis": scam_analysis,
            "quality": quality,
        }

        if quality.get("passed"):
            approved.append(result)
        else:
            rejected.append(result)

    approved = sorted(
        approved,
        key=lambda x: x["final"].get(
            "final_score",
            x["final"].get("score", 0)
        ),
        reverse=True,
    )

    if not approved:
        message = f"""
📭 JARVIS QUALITY FILTER

Nessun segnale approvato.

Rejected:
{len(rejected)}
"""
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    for result in approved[:5]:
        card = result["card"]
        final = result["final"]
        scam_analysis = result["scam_analysis"]
        quality = result["quality"]

        print("\n------------------------------")
        print(f"APPROVED: {card.get('name')} ({card.get('symbol')})")
        print(f"AI Score: {final.get('final_score', final.get('score', 0))}")
        print(f"Risk: {scam_analysis.get('risk_score')}")
        print(f"Chart: {card.get('url')}")

        if send_telegram:
            send_telegram_message(
                format_quality_message(
                    card=card,
                    final=final,
                    scam_analysis=scam_analysis,
                    quality=quality,
                )
            )

    return approved


def main():
    run_quality_filter(send_telegram=True)


if __name__ == "__main__":
    main()