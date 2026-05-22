# token_filter_engine.py

STABLECOIN_SYMBOLS = {
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDD",
    "USD1", "RUSD", "EURCV", "REUR", "PYUSD", "USDE",
    "U", "USDON"
}

BAD_KEYWORDS = [
    "USD",
    "EURO",
    "DOLLAR",
    "STABLE",
    "TETHER",
]


def is_stablecoin(card):
    symbol = str(card.get("symbol", "")).upper()
    name = str(card.get("name", "")).upper()

    if symbol in STABLECOIN_SYMBOLS:
        return True

    for word in BAD_KEYWORDS:
        if word in name:
            return True

    return False


def clean_candidates(candidates):
    cleaned = {}
    
    for card in candidates:
        symbol = str(card.get("symbol", "")).upper().strip()
        chain = str(card.get("chain", "")).lower().strip()

        if not symbol:
            continue

        if is_stablecoin(card):
            continue

        key = f"{symbol}_{chain}"

        liquidity = float(card.get("liquidity", 0) or 0)
        volume = float(card.get("volume_24h", 0) or 0)
        score = float(card.get("score", 0) or 0)

        quality = score + (liquidity / 10000) + (volume / 20000)

        if key not in cleaned:
            card["quality_score"] = quality
            cleaned[key] = card
        else:
            old_quality = cleaned[key].get("quality_score", 0)
            if quality > old_quality:
                card["quality_score"] = quality
                cleaned[key] = card

    final = list(cleaned.values())

    final = sorted(
        final,
        key=lambda x: x.get("quality_score", 0),
        reverse=True
    )

    return final