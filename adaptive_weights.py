# adaptive_weights.py

import json
import os

WEIGHTS_FILE = "adaptive_weights.json"

DEFAULT_WEIGHTS = {

    "ai_score": 1.0,
    "volume": 1.0,
    "liquidity": 1.0,
    "momentum": 1.0,
    "risk": 1.0

}

# =========================
# INIT
# =========================

def initialize_weights():

    if not os.path.exists(
        WEIGHTS_FILE
    ):

        with open(
            WEIGHTS_FILE,
            "w"
        ) as file:

            json.dump(
                DEFAULT_WEIGHTS,
                file,
                indent=4
            )

# =========================
# LOAD
# =========================

def load_weights():

    initialize_weights()

    with open(
        WEIGHTS_FILE,
        "r"
    ) as file:

        return json.load(file)

# =========================
# SAVE
# =========================

def save_weights(weights):

    with open(
        WEIGHTS_FILE,
        "w"
    ) as file:

        json.dump(
            weights,
            file,
            indent=4
        )

# =========================
# ADAPT
# =========================

def adapt_weights(
    learning_stats
):

    weights = load_weights()

    wins = learning_stats.get(
        "wins",
        0
    )

    losses = learning_stats.get(
        "losses",
        0
    )

    total = wins + losses

    if total < 5:
        return weights

    win_rate = (
        wins / total
    ) * 100

    # =========================
    # GOOD PERFORMANCE
    # =========================

    if win_rate >= 60:

        weights["volume"] += 0.05

        weights["liquidity"] += 0.05

        weights["momentum"] += 0.05

    # =========================
    # BAD PERFORMANCE
    # =========================

    elif win_rate <= 40:

        weights["momentum"] -= 0.05

        weights["risk"] += 0.05

    # =========================
    # LIMITS
    # =========================

    for key in weights:

        weights[key] = round(

            max(
                0.3,
                min(
                    weights[key],
                    3.0
                )
            ),

            2

        )

    save_weights(weights)

    return weights

# =========================
# GET CURRENT WEIGHTS
# =========================

def get_current_weights():

    return load_weights()

# =========================
# TEST
# =========================

if __name__ == "__main__":

    test_stats = {

        "wins": 8,
        "losses": 2

    }

    updated = adapt_weights(
        test_stats
    )

    print(
        "\n=== ADAPTIVE WEIGHTS ===\n"
    )

    print(updated)