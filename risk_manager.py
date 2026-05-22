# risk_manager.py

from datetime import datetime

from telegram_alerts import send_telegram_message


ACCOUNT_SIZE_USD = 1000
MAX_RISK_PER_TRADE_PERCENT = 2
MAX_POSITION_SIZE_PERCENT = 10


def calculate_position_size(entry_price, stop_loss_price):
    if entry_price <= 0 or stop_loss_price <= 0:
        return None

    risk_amount_usd = ACCOUNT_SIZE_USD * (MAX_RISK_PER_TRADE_PERCENT / 100)

    risk_per_coin = entry_price - stop_loss_price

    if risk_per_coin <= 0:
        return None

    coin_amount = risk_amount_usd / risk_per_coin
    position_value = coin_amount * entry_price

    max_position_value = ACCOUNT_SIZE_USD * (MAX_POSITION_SIZE_PERCENT / 100)

    if position_value > max_position_value:
        position_value = max_position_value
        coin_amount = position_value / entry_price

    return {
        "risk_amount_usd": risk_amount_usd,
        "coin_amount": coin_amount,
        "position_value": position_value,
        "max_position_value": max_position_value,
    }


def classify_trade_risk(ai_score, change_24h, liquidity, fdv):
    risk_points = 0
    warnings = []

    if ai_score < 75:
        risk_points += 30
        warnings.append("AI score non abbastanza forte")

    if change_24h > 35:
        risk_points += 30
        warnings.append("possibile FOMO: salita 24h troppo alta")

    if liquidity < 50000:
        risk_points += 25
        warnings.append("liquidità bassa")

    if fdv > 50000000:
        risk_points += 20
        warnings.append("FDV alto")

    if risk_points <= 20:
        level = "LOW"
    elif risk_points <= 50:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "risk_points": risk_points,
        "level": level,
        "warnings": warnings,
    }


def build_risk_report(
    symbol,
    entry_price,
    stop_loss_price,
    ai_score,
    change_24h,
    liquidity,
    fdv
):
    position = calculate_position_size(entry_price, stop_loss_price)

    risk = classify_trade_risk(
        ai_score=ai_score,
        change_24h=change_24h,
        liquidity=liquidity,
        fdv=fdv,
    )

    if position is None:
        return """
❌ JARVIS RISK MANAGER

Errore:
Dati entry/stop loss non validi.
"""

    message = f"""
🛡️ JARVIS RISK MANAGER

Token:
{symbol}

Account Size:
${ACCOUNT_SIZE_USD}

Risk per Trade:
{MAX_RISK_PER_TRADE_PERCENT}%

Entry:
${entry_price}

Stop Loss:
${stop_loss_price}

Max Loss:
${round(position.get("risk_amount_usd"), 2)}

Position Value:
${round(position.get("position_value"), 2)}

Coin Amount:
{round(position.get("coin_amount"), 8)}

Risk Level:
{risk.get("level")}

Risk Points:
{risk.get("risk_points")}

Warnings:
{", ".join(risk.get("warnings")) if risk.get("warnings") else "Nessun warning forte"}

Updated:
{datetime.now().isoformat()}

⚠️ Non è consiglio finanziario. È solo gestione rischio automatizzata.
"""

    return message


def interactive_mode():
    print("\n==============================")
    print(" JARVIS RISK MANAGER")
    print("==============================\n")

    symbol = input("Token symbol: ").strip().upper()
    entry_price = float(input("Entry price USD: ").strip())
    stop_loss_price = float(input("Stop loss price USD: ").strip())
    ai_score = float(input("AI score: ").strip())
    change_24h = float(input("Change 24h %: ").strip())
    liquidity = float(input("Liquidity USD: ").strip())
    fdv = float(input("FDV USD: ").strip())

    report = build_risk_report(
        symbol=symbol,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        ai_score=ai_score,
        change_24h=change_24h,
        liquidity=liquidity,
        fdv=fdv,
    )

    print(report)

    send = input("Inviare su Telegram? y/n: ").strip().lower()

    if send == "y":
        send_telegram_message(report)


def main():
    interactive_mode()


if __name__ == "__main__":
    main()