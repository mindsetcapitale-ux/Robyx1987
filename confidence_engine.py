# confidence_engine.py
# JARVIS CONFIDENCE ENGINE

def calculate_confidence(signal):

    confidence = 50

    score = signal.get("score", 0)
    source = signal.get("source", "")
    change = float(signal.get("change_24h", 0) or 0)
    reason = signal.get("reason", "").lower()

    if score >= 95:
        confidence += 20
    elif score >= 90:
        confidence += 12
    elif score >= 85:
        confidence += 6

    if source == "BINANCE":
        confidence += 10
    elif source == "DEX":
        confidence += 6
    elif source == "AI":
        confidence += 4

    if -2 <= change <= 4:
        confidence += 15
    elif 4 < change <= 8:
        confidence += 5
    elif change > 10:
        confidence -= 20
    elif change < -6:
        confidence -= 15

    if "whale" in reason:
        confidence += 8

    if "social" in reason:
        confidence += 5

    if "filtered" in reason:
        confidence += 8

    if "pump" in reason:
        confidence -= 10

    confidence = max(
        1,
        min(
            int(confidence),
            100
        )
    )

    return confidence


def confidence_status(confidence):

    if confidence >= 85:
        return "HIGH CONFIDENCE"

    if confidence >= 70:
        return "MEDIUM CONFIDENCE"

    return "LOW CONFIDENCE"


if __name__ == "__main__":

    test_signal = {
        "symbol": "NEAR",
        "score": 94,
        "source": "BINANCE",
        "change_24h": 2.4,
        "reason": "Binance filtered quality signal"
    }

    confidence = calculate_confidence(test_signal)

    print("\n=== JARVIS CONFIDENCE ENGINE ===\n")
    print("Confidence:", confidence)
    print("Status:", confidence_status(confidence))