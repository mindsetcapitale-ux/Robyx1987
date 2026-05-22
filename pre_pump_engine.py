# pre_pump_engine.py
# JARVIS PRE-PUMP DETECTION ENGINE

def calculate_pre_pump_score(signal):

    score = 0

    ai_score = signal.get("score", 0)
    confidence = signal.get("confidence", 0)
    change_24h = float(signal.get("change_24h", 0) or 0)
    source = signal.get("source", "")
    reason = signal.get("reason", "").lower()

    # =========================
    # AI + CONFIDENCE
    # =========================

    if ai_score >= 95:
        score += 25

    elif ai_score >= 90:
        score += 18

    elif ai_score >= 85:
        score += 10

    if confidence >= 85:
        score += 25

    elif confidence >= 70:
        score += 15

    # =========================
    # PRE-PUMP ZONE
    # =========================

    if -1 <= change_24h <= 4:
        score += 30

    elif 4 < change_24h <= 8:
        score += 12

    elif change_24h > 12:
        score -= 25

    elif change_24h < -8:
        score -= 15

    # =========================
    # SOURCE QUALITY
    # =========================

    if source == "BINANCE":
        score += 10

    elif source == "DEX":
        score += 8

    elif source == "AI":
        score += 5

    # =========================
    # REASON BOOST
    # =========================

    if "whale" in reason:
        score += 10

    if "social" in reason:
        score += 8

    if "filtered" in reason:
        score += 8

    if "pump" in reason:
        score -= 10

    # =========================
    # LIMITS
    # =========================

    score = max(
        0,
        min(
            int(score),
            100
        )
    )

    return score


def pre_pump_status(score):

    if score >= 85:
        return "STRONG PRE-PUMP"

    if score >= 70:
        return "POSSIBLE PRE-PUMP"

    if score >= 50:
        return "WATCHLIST"

    return "NO SETUP"


def enrich_with_pre_pump(signal):

    pre_score = calculate_pre_pump_score(signal)

    signal["pre_pump_score"] = pre_score

    signal["pre_pump_status"] = pre_pump_status(
        pre_score
    )

    return signal


if __name__ == "__main__":

    test_signal = {
        "symbol": "NEAR",
        "score": 94,
        "confidence": 82,
        "change_24h": 2.4,
        "source": "BINANCE",
        "reason": "Binance filtered quality signal"
    }

    enriched = enrich_with_pre_pump(test_signal)

    print("\n=== JARVIS PRE-PUMP ENGINE ===\n")
    print(enriched)