# core/signal_reporter.py

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

from engines.entry_planner import run_entry_planner
from core.telegram_alerts import send_telegram_message
from core.signal_history import save_signal
from core.signal_cooldown import check_and_mark_signal
from core.adaptive_learning_engine import calculate_adaptive_score


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def calculate_priority(card, final, plan):
    base_score = safe_float(final.get("final_score", final.get("score", 0)))

    adaptive_score = calculate_adaptive_score(
        card=card,
        base_score=base_score
    )

    liquidity = safe_float(card.get("liquidity"))
    volume = safe_float(card.get("volume_24h"))
    change_1h = safe_float(card.get("change_1h"))
    change_6h = safe_float(card.get("change_6h"))
    change_24h = safe_float(card.get("change_24h"))

    priority_score = adaptive_score

    if liquidity >= 100000:
        priority_score += 5

    if volume >= 200000:
        priority_score += 5

    if 3 <= change_1h <= 20:
        priority_score += 5

    if 5 <= change_6h <= 35:
        priority_score += 5

    if change_24h > 60:
        priority_score -= 20

    priority_score = max(0, min(round(priority_score), 100))

    if priority_score >= 95:
        level = "🚨 EXTREME BUY"
        bucket = "EXTREME"

    elif priority_score >= 92:
        level = "🔥 AI SNIPER"
        bucket = "EXTREME"

    elif priority_score >= 88:
        level = "⚡ MOMENTUM ENTRY"
        bucket = "HIGH"

    elif priority_score >= 84:
        level = "💎 SWING SETUP"
        bucket = "HIGH"

    elif priority_score >= 78:
        level = "🟢 SAFE ENTRY"
        bucket = "MEDIUM"

    elif priority_score >= 70:
        level = "👀 WATCHLIST"
        bucket = "LOW"

    else:
        level = "❌ AVOID"
        bucket = "LOW"

    return {
        "base_score": base_score,
        "adaptive_score": adaptive_score,
        "priority_score": priority_score,
        "priority_level": level,
        "bucket": bucket,
    }


def deduplicate_reports(reports):
    cleaned = {}

    for report in reports:
        card = report.get("card", {})
        priority = report.get("priority", {})

        symbol = str(card.get("symbol", "")).upper().strip()

        if not symbol:
            continue

        current_quality = (
            safe_float(priority.get("priority_score"))
            + safe_float(card.get("liquidity")) / 10000
            + safe_float(card.get("volume_24h")) / 20000
        )

        if symbol not in cleaned:
            report["dedupe_quality"] = current_quality
            cleaned[symbol] = report
        else:
            old_quality = safe_float(
                cleaned[symbol].get("dedupe_quality")
            )

            if current_quality > old_quality:
                report["dedupe_quality"] = current_quality
                cleaned[symbol] = report

    return sorted(
        cleaned.values(),
        key=lambda x: x.get("dedupe_quality", 0),
        reverse=True
    )


def format_summary_report(reports, cooldown_count):
    grouped = {
        "EXTREME": [],
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
    }

    for report in reports:
        priority = report.get("priority", {})
        bucket = priority.get("bucket", "LOW")
        grouped[bucket].append(report)

    message = f"""
🤖 JARVIS SMART SIGNALS

Generated:
{datetime.now().isoformat()}

Signals:
{len(reports)}

Cooldown blocked:
{cooldown_count}

Learning:
Adaptive scoring active

==============================
"""

    sections = [
        ("🚨 EXTREME BUY", grouped["EXTREME"]),
        ("⚡ HIGH MOMENTUM", grouped["HIGH"]),
        ("🟢 SAFE ENTRIES", grouped["MEDIUM"]),
        ("👀 WATCHLIST", grouped["LOW"]),
    ]

    for title, items in sections:
        if not items:
            continue

        message += f"""

{title}
"""

        for item in items:
            card = item.get("card", {})
            final = item.get("final", {})
            plan = item.get("plan", {})
            priority = item.get("priority", {})

            original_score = final.get(
                "final_score",
                final.get("score", 0)
            )

            message += f"""
{priority.get("priority_level")}

💎 {card.get("name")} ({card.get("symbol")})

🧠 Base Score:
{original_score}/100

🧬 Adaptive Score:
{priority.get("adaptive_score")}/100

📊 Priority:
{priority.get("priority_score")}/100

⛓️ Chain:
{card.get("chain")}

💰 Entry:
${plan.get("entry")}

🎯 TP1:
${round(safe_float(plan.get("take_profit_1")), 10)}

🎯 TP2:
${round(safe_float(plan.get("take_profit_2")), 10)}

📈 1H:
{card.get("change_1h", "N/A")}%

📈 24H:
{card.get("change_24h", "N/A")}%

💧 Liquidity:
${round(safe_float(card.get("liquidity")), 2)}

📊 Volume:
${round(safe_float(card.get("volume_24h")), 2)}

🔗 Chart:
{card.get("url")}
"""

    message += """

⚠️ Non comprare automaticamente.
Usa Jarvis come radar AI di supporto.
"""

    return message


def run_signal_reporter(send_telegram=True):
    print("\n==============================")
    print(" JARVIS ADAPTIVE SIGNAL REPORTER")
    print("==============================\n")

    plans = run_entry_planner(
        send_telegram=False
    )

    if not plans:
        message = "📭 Nessun segnale valido adesso."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    raw_reports = []
    cooldown_count = 0

    for item in plans[:10]:
        card = item.get("card", {})
        final = item.get("final", {})
        plan = item.get("plan", {})

        symbol = str(
            card.get("symbol", "UNKNOWN")
        ).upper()

        chain = str(
            card.get("chain", "")
        ).lower()

        category = str(
            final.get("category", "UNKNOWN")
        ).upper()

        priority = calculate_priority(
            card,
            final,
            plan
        )

        raw_reports.append({
            "card": card,
            "final": final,
            "plan": plan,
            "priority": priority,
            "cooldown_key": {
                "symbol": symbol,
                "chain": chain,
                "category": category,
            }
        })

    deduped_reports = deduplicate_reports(
        raw_reports
    )

    final_reports = []

    for report in deduped_reports[:5]:
        key = report.get("cooldown_key", {})

        symbol = key.get("symbol", "UNKNOWN")
        chain = key.get("chain", "")
        category = key.get("category", "UNKNOWN")

        if not check_and_mark_signal(
            symbol,
            chain,
            category
        ):
            cooldown_count += 1
            print(
                f"Cooldown attivo: "
                f"{symbol} | {chain} | {category}"
            )
            continue

        card = report.get("card", {})
        priority = report.get("priority", {})

        signal_record = {
            "symbol": symbol,
            "score": priority.get("priority_score"),
            "change_24h": card.get("change_24h", 0),
            "source": "Jarvis Adaptive Signal Reporter",
            "reason": priority.get("priority_level"),
        }

        save_signal(signal_record)

        final_reports.append(report)

    if not final_reports:
        message = f"""
📭 Nessun nuovo segnale inviato.

Cooldown bloccati:
{cooldown_count}
"""
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    summary = format_summary_report(
        final_reports,
        cooldown_count
    )

    print(summary)

    if send_telegram:
        send_telegram_message(summary)

    return final_reports


def main():
    run_signal_reporter(
        send_telegram=True
    )


if __name__ == "__main__":
    main()