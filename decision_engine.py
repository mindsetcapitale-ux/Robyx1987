# decision_engine.py

from datetime import datetime

from ai_signal_engine import run_ai_signal_engine
from market_sentiment_engine import get_fear_greed_index, analyze_sentiment
from telegram_alerts import send_telegram_message


MIN_BUY_SCORE = 85
MIN_WAIT_SCORE = 75


def get_market_context():
    data = get_fear_greed_index()

    if not data:
        return {
            "value": None,
            "classification": "UNKNOWN",
            "sentiment": "UNKNOWN",
            "risk": "UNKNOWN",
        }

    value = int(data.get("value", 0))
    classification = data.get("value_classification", "UNKNOWN")
    analysis = analyze_sentiment(value)

    return {
        "value": value,
        "classification": classification,
        "sentiment": analysis.get("sentiment"),
        "risk": analysis.get("risk"),
    }


def decide_action(final_score, market_context):
    fear_value = market_context.get("value")

    if fear_value is None:
        if final_score >= MIN_BUY_SCORE:
            return "BUY WATCH", "Score forte, ma sentiment mercato non disponibile"
        if final_score >= MIN_WAIT_SCORE:
            return "WAIT", "Score buono, ma mancano dati sentiment"
        return "AVOID", "Score insufficiente"

    if fear_value >= 80:
        return "WAIT", "Mercato in extreme greed: rischio FOMO alto"

    if final_score >= MIN_BUY_SCORE and fear_value <= 75:
        return "BUY WATCH", "Score forte e sentiment non euforico"

    if final_score >= MIN_WAIT_SCORE:
        return "WAIT", "Segnale interessante ma serve conferma"

    return "AVOID", "Segnale non abbastanza forte"


def format_decision_message(card, final, action, reason, market_context):
    return f"""
🧠 JARVIS FINAL DECISION ENGINE

Token:
{card.get("name")} ({card.get("symbol")})

Chain:
{card.get("chain")}

DEX:
{card.get("dex")}

Final AI Score:
{final.get("final_score")}/100

AI Category:
{final.get("category")}

Market Fear & Greed:
{market_context.get("value")} - {market_context.get("classification")}

Market Sentiment:
{market_context.get("sentiment")}

FINAL ACTION:
{action}

Reason:
{reason}

Chart:
{card.get("url")}

Time:
{datetime.now().isoformat()}

⚠️ Non è consiglio finanziario. Questo è solo filtro decisionale automatico.
"""


def run_decision_engine(send_telegram=True):
    print("\n==============================")
    print(" JARVIS FINAL DECISION ENGINE")
    print("==============================\n")

    market_context = get_market_context()

    print("Market context:", market_context)

    signals = run_ai_signal_engine(send_telegram=False)

    if not signals:
        message = "📭 Jarvis Decision Engine: nessun segnale AI forte da valutare."
        print(message)

        if send_telegram:
            send_telegram_message(message)

        return []

    decisions = []

    for item in signals:
        card = item.get("card", {})
        final = item.get("final", {})

        final_score = final.get("final_score", 0)

        action, reason = decide_action(final_score, market_context)

        decision = {
            "card": card,
            "final": final,
            "action": action,
            "reason": reason,
            "market_context": market_context,
        }

        decisions.append(decision)

    decisions = sorted(
        decisions,
        key=lambda item: item["final"].get("final_score", 0),
        reverse=True,
    )

    for decision in decisions[:5]:
        card = decision["card"]
        final = decision["final"]
        action = decision["action"]
        reason = decision["reason"]
        market_context = decision["market_context"]

        print("\n------------------------------")
        print(f"{card.get('name')} ({card.get('symbol')})")
        print(f"Score: {final.get('final_score')}")
        print(f"Action: {action}")
        print(f"Reason: {reason}")

        if send_telegram:
            send_telegram_message(
                format_decision_message(
                    card=card,
                    final=final,
                    action=action,
                    reason=reason,
                    market_context=market_context,
                )
            )

    return decisions


def main():
    run_decision_engine(send_telegram=True)


if __name__ == "__main__":
    main()