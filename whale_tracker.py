# whale_tracker.py
# JARVIS WHALE TRACKER ENGINE

import random


def detect_whale_activity(signal):

    whale_score = 0

    score = signal.get("score", 0)
    confidence = signal.get("confidence", 0)
    pre_pump = signal.get("pre_pump_score", 0)

    reason = signal.get(
        "reason",
        ""
    ).lower()

    source = signal.get(
        "source",
        ""
    )

    change_24h = float(
        signal.get(
            "change_24h",
            0
        ) or 0
    )

    # =========================
    # AI + CONFIDENCE
    # =========================

    if score >= 95:
        whale_score += 20

    elif score >= 90:
        whale_score += 12

    if confidence >= 85:
        whale_score += 20

    elif confidence >= 70:
        whale_score += 10

    if pre_pump >= 85:
        whale_score += 20

    elif pre_pump >= 70:
        whale_score += 12

    # =========================
    # VOLUME ZONE
    # =========================

    if -2 <= change_24h <= 5:
        whale_score += 15

    elif change_24h > 12:
        whale_score -= 15

    # =========================
    # SOURCE BOOST
    # =========================

    if source == "DEX":
        whale_score += 12

    elif source == "BINANCE":
        whale_score += 8

    # =========================
    # REASON ANALYSIS
    # =========================

    if "whale" in reason:
        whale_score += 20

    if "smart money" in reason:
        whale_score += 15

    if "social" in reason:
        whale_score += 5

    if "pump" in reason:
        whale_score -= 10

    # =========================
    # RANDOM MICRO SIGNAL
    # =========================

    whale_score += random.randint(
        -3,
        5
    )

    # =========================
    # LIMITS
    # =========================

    whale_score = max(
        0,
        min(
            int(whale_score),
            100
        )
    )

    return whale_score


def whale_status(score):

    if score >= 85:
        return "STRONG WHALE ACTIVITY"

    if score >= 70:
        return "WHALE ACCUMULATION"

    if score >= 50:
        return "POSSIBLE WHALE INTEREST"

    return "NO WHALE SIGNAL"


def enrich_whale_signal(signal):

    whale_score = detect_whale_activity(
        signal
    )

    signal["whale_score"] = whale_score

    signal["whale_status"] = whale_status(
        whale_score
    )

    return signal


if __name__ == "__main__":

    test_signal = {

        "symbol": "NEAR",

        "score": 95,

        "confidence": 88,

        "pre_pump_score": 84,

        "change_24h": 2.8,

        "source": "DEX",

        "reason":
        "Whale accumulation + social growth"

    }

    enriched = enrich_whale_signal(
        test_signal
    )

    print(
        "\n=== JARVIS WHALE TRACKER ===\n"
    )

    print(enriched)