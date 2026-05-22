# engines/anti_scam_engine.py

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


HIGH_RISK_WORDS = [
    "elon",
    "1000x",
    "moon",
    "inu",
    "gem",
    "presale",
]

MAX_SAFE_PUMP_24H = 80
MIN_SAFE_LIQUIDITY = 15000
MAX_SAFE_FDV = 120_000_000


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def analyze_scam_risk(card):
    risk_score = 0
    reasons = []

    name = str(
        card.get("name", "")
    ).lower()

    symbol = str(
        card.get("symbol", "")
    ).lower()

    liquidity = safe_float(
        card.get("liquidity")
    )

    fdv = safe_float(
        card.get("fdv")
    )

    change_24h = safe_float(
        card.get("change_24h")
    )

    volume = safe_float(
        card.get("volume_24h")
    )

    for word in HIGH_RISK_WORDS:
        if word in name or word in symbol:
            risk_score += 15
            reasons.append(
                f"keyword rischio: {word}"
            )

    if liquidity < MIN_SAFE_LIQUIDITY:
        risk_score += 25
        reasons.append(
            "liquidità troppo bassa"
        )

    if fdv > MAX_SAFE_FDV:
        risk_score += 20
        reasons.append(
            "FDV troppo alto"
        )

    if change_24h > MAX_SAFE_PUMP_24H:
        risk_score += 25
        reasons.append(
            "pump eccessivo 24h"
        )

    if volume < 10000:
        risk_score += 10
        reasons.append(
            "volume sospetto"
        )

    risk_score = max(
        0,
        min(risk_score, 100)
    )

    if risk_score >= 70:
        risk_level = "HIGH"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
    }


def format_scam_report(card, analysis):
    return f"""
🛡️ JARVIS ANTI SCAM

Token:
{card.get("name")} ({card.get("symbol")})

Risk Score:
{analysis.get("risk_score")}/100

Risk Level:
{analysis.get("risk_level")}

Liquidity:
${round(safe_float(card.get("liquidity")), 2)}

Volume:
${round(safe_float(card.get("volume_24h")), 2)}

FDV:
${round(safe_float(card.get("fdv")), 2)}

24H:
{card.get("change_24h")}%

Reasons:
{", ".join(analysis.get("reasons")) if analysis.get("reasons") else "Nessun rischio forte"}

Chart:
{card.get("url")}

Time:
{datetime.now().isoformat()}

⚠️ Anti scam radar only.
"""


def run_anti_scam_engine(send_telegram=True):
    print("\n==============================")
    print(" JARVIS ANTI SCAM ENGINE")
    print("==============================\n")

    candidates = scan_once(
        send_telegram=False
    )

    if not candidates:
        message = (
            "📭 Nessun token da analizzare."
        )

        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    results = []

    for card in candidates:
        analysis = analyze_scam_risk(card)

        results.append({
            "card": card,
            "analysis": analysis,
        })

    results = sorted(
        results,
        key=lambda x: x["analysis"].get(
            "risk_score",
            0
        )
    )

    for item in results[:5]:
        card = item["card"]
        analysis = item["analysis"]

        print("\n------------------------------")
        print(
            f"{card.get('symbol')} "
            f"| Risk: {analysis.get('risk_score')}"
        )

        if send_telegram:
            send_telegram_message(
                format_scam_report(
                    card,
                    analysis
                )
            )

    return results


def main():
    run_anti_scam_engine(
        send_telegram=True
    )


if __name__ == "__main__":
    main()