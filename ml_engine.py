# ml_engine.py

from statistics import mean
from database_manager import *

# =========================
# ML MEMORY
# =========================

ml_memory = {

    "average_ai": 60,
    "successful_signals": 0,
    "failed_signals": 0

}

# =========================
# UPDATE ML
# =========================

def aggiorna_ml():

    global ml_memory

    data = carica_database()

    segnali = data["signals"]

    if len(segnali) == 0:

        return ml_memory

    ai_scores = [

        x["ai_probability"]
        for x in segnali
        if "ai_probability" in x

    ]

    if len(ai_scores) == 0:

        return ml_memory

    ml_memory["average_ai"] = int(
        mean(ai_scores)
    )

    ml_memory["successful_signals"] = len(

        [

            x for x in ai_scores
            if x >= 75

        ]

    )

    ml_memory["failed_signals"] = len(

        [

            x for x in ai_scores
            if x < 50

        ]

    )

    aggiorna_ml_memory(
        ml_memory
    )

    return ml_memory

# =========================
# GET ML MEMORY
# =========================

def get_ml_memory():

    return aggiorna_ml()