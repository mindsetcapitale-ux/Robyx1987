# social_sentiment.py

import random

SOCIAL_KEYWORDS = [
    "AI",
    "MEME",
    "SOLANA",
    "RWA",
    "GAMING",
    "DEFI",
    "ETF",
    "LAYER 2",
    "TOKEN BURN",
    "LISTING"
]


def get_social_sentiment():

    trend = random.choice(
        SOCIAL_KEYWORDS
    )

    score = random.randint(
        10,
        90
    )

    if score >= 70:
        status = "VIRAL BUILDING"

    elif score >= 40:
        status = "TREND FORMING"

    else:
        status = "LOW HYPE"

    return {
        "trend": trend,
        "score": score,
        "status": status
    }


if __name__ == "__main__":

    sentiment = get_social_sentiment()

    print("\n=== SOCIAL SENTIMENT ===\n")
    print(sentiment)