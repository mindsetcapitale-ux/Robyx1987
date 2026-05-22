# deduplicate_engine.py

def deduplicate_candidates(candidates):
    unique = {}

    for card in candidates:

        symbol = str(card.get("symbol", "")).upper()

        if symbol == "":
            continue

        current_score = float(card.get("score", 0))
        current_liquidity = float(card.get("liquidity", 0))

        if symbol not in unique:
            unique[symbol] = card
            continue

        existing = unique[symbol]

        existing_score = float(existing.get("score", 0))
        existing_liquidity = float(existing.get("liquidity", 0))

        current_total = current_score + (current_liquidity / 10000)
        existing_total = existing_score + (existing_liquidity / 10000)

        if current_total > existing_total:
            unique[symbol] = card

    return list(unique.values())