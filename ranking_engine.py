# ranking_engine.py

from adaptive_weights import get_current_weights
from sentiment_engine import calculate_polymarket_sentiment
from wallet_tracker import controlla_wallets
from social_sentiment import get_social_sentiment

# =========================
# BLACKLIST
# =========================

BLACKLIST = [

    "U",
    "TEST",
    "SCAM",
    "FAKE",
    "MOON",
    "PUMP"

]

# =========================
# WHALE BOOST
# =========================

def calculate_whale_boost():

    wallets = controlla_wallets()

    boost = 0

    for wallet in wallets:

        eth = wallet.get("eth", 0)

        if eth >= 50:
            boost += 25

        elif eth >= 10:
            boost += 15

        elif eth >= 1:
            boost += 8

    return min(boost, 40)

# =========================
# SOCIAL BOOST
# =========================

def calculate_social_boost():

    social = get_social_sentiment()

    score = social.get(
        "score",
        0
    )

    status = social.get(
        "status",
        "LOW HYPE"
    )

    if status == "VIRAL BUILDING":
        return score * 0.25

    elif status == "TREND FORMING":
        return score * 0.12

    return 0

# =========================
# QUALITY FILTER
# =========================

def is_quality_project(
    symbol,
    volume,
    liquidity,
    change_24h
):

    symbol = symbol.upper()

    # =========================
    # BLACKLIST
    # =========================

    if symbol in BLACKLIST:
        return False

    # =========================
    # LOW LIQUIDITY
    # =========================

    if liquidity < 150000:
        return False

    # =========================
    # LOW VOLUME
    # =========================

    if volume < 300000:
        return False

    # =========================
    # OVERPUMP FILTER
    # =========================

    if change_24h > 35:
        return False

    # =========================
    # DEAD TOKEN
    # =========================

    if change_24h < -25:
        return False

    return True

# =========================
# SCORE
# =========================

def calculate_ranking_score(
    ai_probability=0,
    volume=0,
    liquidity=0,
    change_24h=0,
    risk=0
):

    weights = get_current_weights()

    sentiment = calculate_polymarket_sentiment()

    whale_boost = calculate_whale_boost()

    social_boost = calculate_social_boost()

    score = 0

    # AI

    score += (
        ai_probability *
        weights["ai_score"]
    )

    # VOLUME

    volume_boost = 0

    if volume > 1_000_000:
        volume_boost += 10

    if volume > 5_000_000:
        volume_boost += 15

    if volume > 20_000_000:
        volume_boost += 20

    score += (
        volume_boost *
        weights["volume"]
    )

    # LIQUIDITY

    liquidity_boost = 0

    if liquidity > 250_000:
        liquidity_boost += 10

    if liquidity > 1_000_000:
        liquidity_boost += 20

    if liquidity > 5_000_000:
        liquidity_boost += 25

    score += (
        liquidity_boost *
        weights["liquidity"]
    )

    # MOMENTUM

    momentum = 0

    if -2 <= change_24h <= 5:
        momentum += 20

    if 1 <= change_24h <= 4:
        momentum += 15

    if change_24h > 10:
        momentum -= 15

    if change_24h > 20:
        momentum -= 30

    score += (
        momentum *
        weights["momentum"]
    )

    # RISK

    score -= (
        risk *
        weights["risk"]
    )

    # POLYMARKET

    sentiment_score = sentiment.get(
        "score",
        0
    )

    sentiment_status = sentiment.get(
        "status",
        "NEUTRAL"
    )

    if sentiment_status == "BULLISH":

        score += (
            sentiment_score * 0.15
        )

    elif sentiment_status == "BEARISH":

        score -= (
            abs(sentiment_score) * 0.20
        )

    # WHALE

    score += whale_boost

    # SOCIAL

    score += social_boost

    # LIMIT

    score = max(
        1,
        min(
            int(score),
            100
        )
    )

    return score

# =========================
# RANKING
# =========================

def rank_opportunities(
    ai_signals=None,
    dex_signals=None,
    binance_signals=None
):

    ai_signals = ai_signals or []
    dex_signals = dex_signals or []
    binance_signals = binance_signals or []

    ranking = []

    # =========================
    # AI SIGNALS
    # =========================

    for coin in ai_signals:

        symbol = coin.get(
            "simbolo",
            ""
        )

        change = coin.get(
            "change_24h",
            0
        )

        if not is_quality_project(
            symbol,
            volume=500000,
            liquidity=500000,
            change_24h=change
        ):
            continue

        score = calculate_ranking_score(

            ai_probability=coin.get(
                "ai_probability",
                0
            ),

            volume=500000,

            liquidity=500000,

            change_24h=change,

            risk=coin.get(
                "rischio",
                0
            )

        )

        ranking.append({

            "source": "AI",

            "symbol": symbol,

            "name": coin.get(
                "nome",
                ""
            ),

            "score": score,

            "change_24h": change,

            "reason":
            "AI + social + whale filter"

        })

    # =========================
    # DEX SIGNALS
    # =========================

    for coin in dex_signals:

        try:

            volume = float(
                coin.get(
                    "volume24h",
                    0
                ) or 0
            )

            liquidity = float(
                coin.get(
                    "liquidity",
                    0
                ) or 0
            )

            change = float(
                coin.get(
                    "change24h",
                    0
                ) or 0
            )

        except:

            continue

        symbol = coin.get(
            "symbol",
            ""
        )

        if not is_quality_project(
            symbol,
            volume,
            liquidity,
            change
        ):
            continue

        score = calculate_ranking_score(

            ai_probability=50,

            volume=volume,

            liquidity=liquidity,

            change_24h=change,

            risk=0

        )

        ranking.append({

            "source": "DEX",

            "symbol": symbol,

            "name": symbol,

            "score": score,

            "change_24h": change,

            "reason":
            "DEX filtered quality signal"

        })

    # =========================
    # BINANCE SIGNALS
    # =========================

    for coin in binance_signals:

        try:

            volume = float(
                coin.get(
                    "volume",
                    0
                ) or 0
            )

            change = float(
                coin.get(
                    "change",
                    0
                ) or 0
            )

        except:

            continue

        symbol = coin.get(
            "symbol",
            ""
        )

        if not is_quality_project(
            symbol,
            volume,
            liquidity=1000000,
            change_24h=change
        ):
            continue

        score = calculate_ranking_score(

            ai_probability=coin.get(
                "score",
                50
            ),

            volume=volume,

            liquidity=1000000,

            change_24h=change,

            risk=0

        )

        ranking.append({

            "source": "BINANCE",

            "symbol": symbol,

            "name": symbol,

            "score": score,

            "change_24h": change,

            "reason":
            "Binance filtered quality signal"

        })

    ranking = sorted(

        ranking,

        key=lambda x: x["score"],

        reverse=True

    )

    return ranking[:15]

# =========================
# TEST
# =========================

if __name__ == "__main__":

    ranking = rank_opportunities()

    print(
        "\n=== QUALITY FILTER RANKING ===\n"
    )

    for coin in ranking:

        print(
            coin["symbol"],
            "|",
            coin["score"],
            "|",
            coin["reason"]
        )