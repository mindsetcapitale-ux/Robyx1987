# unified_trading_engine.py
# JARVIS ANALYTICS ENGINE

import json
import os
import datetime
import requests
import time

from ai_scanner import scan_market
from binance_stream import get_binance_top_movers
from Dexscreener_engine import get_dexscreener_data
from ranking_engine import rank_opportunities
from learning_engine import salva_signal_da_monitorare
from telegram_alerts import send_top_signals

TRADING_FILE = "unified_paper_trades.json"

MIN_SCORE_TO_OPEN = 92
MAX_OPEN_TRADES = 3
VIRTUAL_INVESTMENT = 100

PRICE_CACHE = {}

BLOCKED_SYMBOLS = [

    "USDT",
    "USDC",
    "FDUSD",
    "BUSD",
    "TUSD",
    "DAI",
    "RUSD",
    "EUR",
    "REUR",
    "TRY",
    "UAH",
    "RUB"

]

# =========================
# INIT
# =========================

def inizializza_trading_file():

    if not os.path.exists(TRADING_FILE):

        data = {

            "open_trades": [],
            "closed_trades": [],

            "stats": {

                "total_opened": 0,
                "total_closed": 0,
                "wins": 0,
                "losses": 0,
                "profit_total": 0

            }

        }

        with open(TRADING_FILE, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )

# =========================
# LOAD / SAVE
# =========================

def carica_trades():

    inizializza_trading_file()

    with open(TRADING_FILE, "r") as file:

        return json.load(file)

def salva_trades(data):

    with open(TRADING_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )

# =========================
# CLEAN SYMBOL
# =========================

def clean_symbol(symbol):

    symbol = symbol.upper()

    removes = [

        "USDT",
        "USD",
        "PERP"

    ]

    for r in removes:

        symbol = symbol.replace(
            r,
            ""
        )

    return symbol.strip()

# =========================
# VALID SYMBOL
# =========================

def is_valid_symbol(symbol):

    symbol = clean_symbol(symbol)

    if len(symbol) < 2:
        return False

    if len(symbol) > 12:
        return False

    if symbol in BLOCKED_SYMBOLS:
        return False

    if not symbol.isalnum():
        return False

    return True

# =========================
# CACHE
# =========================

def get_cached_price(symbol):

    now = time.time()

    if symbol in PRICE_CACHE:

        cache = PRICE_CACHE[symbol]

        age = now - cache["time"]

        if age < 120:

            return cache["price"]

    return None

def set_cached_price(symbol, price):

    PRICE_CACHE[symbol] = {

        "price": price,
        "time": time.time()

    }

# =========================
# PRICE
# =========================

def get_binance_price(symbol):

    symbol = clean_symbol(symbol)

    if not is_valid_symbol(symbol):
        return None

    cached = get_cached_price(symbol)

    if cached is not None:
        return cached

    try:

        pair = symbol + "USDT"

        response = requests.get(

            "https://api.binance.com/api/v3/ticker/price",

            params={
                "symbol": pair
            },

            timeout=8

        )

        data = response.json()

        if "price" not in data:
            return None

        price = float(
            data["price"]
        )

        if price <= 0:
            return None

        set_cached_price(
            symbol,
            price
        )

        return price

    except:
        return None

# =========================
# OPEN CHECK
# =========================

def trade_gia_aperto(symbol, data):

    symbol = clean_symbol(symbol)

    for trade in data["open_trades"]:

        if clean_symbol(
            trade["symbol"]
        ) == symbol:

            return True

    return False

# =========================
# TP / SL
# =========================

def calculate_dynamic_tp_sl(signal):

    score = signal.get(
        "score",
        0
    )

    source = signal.get(
        "source",
        "AI"
    )

    tp = 12
    sl = -6

    if score >= 98:

        tp = 20
        sl = -7

    elif score >= 95:

        tp = 16
        sl = -6

    if source == "DEX":

        tp += 3

    tp = min(tp, 30)

    return tp, sl

# =========================
# OPEN TRADE
# =========================

def apri_trade_virtuale(signal):

    data = carica_trades()

    if len(data["open_trades"]) >= MAX_OPEN_TRADES:
        return False

    symbol = clean_symbol(
        signal.get(
            "symbol",
            ""
        )
    )

    score = signal.get(
        "score",
        0
    )

    if not is_valid_symbol(symbol):
        return False

    if score < MIN_SCORE_TO_OPEN:
        return False

    if trade_gia_aperto(symbol, data):
        return False

    entry_price = get_binance_price(
        symbol
    )

    if entry_price is None:
        return False

    tp, sl = calculate_dynamic_tp_sl(
        signal
    )

    trade = {

        "symbol": symbol,

        "name": signal.get(
            "name",
            symbol
        ),

        "source": signal.get(
            "source",
            "UNKNOWN"
        ),

        "score": score,

        "entry_price": entry_price,

        "take_profit": tp,

        "stop_loss": sl,

        "opened_at": str(
            datetime.datetime.now()
        ),

        "status": "OPEN"

    }

    data["open_trades"].append(
        trade
    )

    data["stats"][
        "total_opened"
    ] += 1

    salva_trades(data)

    salva_signal_da_monitorare({

        "symbol": symbol,

        "name": signal.get(
            "name",
            symbol
        ),

        "score": score,

        "change_24h": signal.get(
            "change_24h",
            0
        ),

        "price": entry_price

    })

    print(
        f"APERTO {symbol} "
        f"| Entry {entry_price} "
        f"| TP {tp}% "
        f"| SL {sl}% "
        f"| Score {score}"
    )

    return True

# =========================
# AUTO CLOSE
# =========================

def auto_close_trades():

    data = carica_trades()

    updated_open = []

    for trade in data["open_trades"]:

        symbol = trade["symbol"]

        live_price = get_binance_price(
            symbol
        )

        if live_price is None:

            updated_open.append(trade)
            continue

        entry_price = trade[
            "entry_price"
        ]

        pnl = (

            (
                live_price -
                entry_price
            )

            / entry_price

        ) * 100

        tp = trade.get(
            "take_profit",
            12
        )

        sl = trade.get(
            "stop_loss",
            -6
        )

        close_reason = None

        if pnl >= tp:

            close_reason = (
                "TAKE PROFIT"
            )

        elif pnl <= sl:

            close_reason = (
                "STOP LOSS"
            )

        if close_reason:

            trade["status"] = (
                "CLOSED"
            )

            trade["closed_at"] = str(
                datetime.datetime.now()
            )

            trade["close_price"] = (
                live_price
            )

            trade["final_pnl"] = round(
                pnl,
                2
            )

            trade["close_reason"] = (
                close_reason
            )

            # =========================
            # DURATION
            # =========================

            opened = datetime.datetime.fromisoformat(
                trade["opened_at"]
            )

            closed = datetime.datetime.now()

            duration = closed - opened

            trade["duration_minutes"] = round(
                duration.total_seconds() / 60,
                2
            )

            data["closed_trades"].append(
                trade
            )

            data["stats"][
                "total_closed"
            ] += 1

            data["stats"][
                "profit_total"
            ] += round(
                pnl,
                2
            )

            if pnl > 0:

                data["stats"][
                    "wins"
                ] += 1

            else:

                data["stats"][
                    "losses"
                ] += 1

            print(
                f"CLOSED {symbol} "
                f"| {close_reason} "
                f"| {round(pnl,2)}%"
            )

        else:

            trade["current_price"] = (
                live_price
            )

            trade["current_pnl"] = round(
                pnl,
                2
            )

            updated_open.append(
                trade
            )

    data["open_trades"] = updated_open

    salva_trades(data)

# =========================
# ANALYTICS
# =========================

def analytics_report(data):

    closed = data["closed_trades"]

    if len(closed) == 0:

        print("\nNessun trade chiuso.\n")
        return

    print("\n==============================")
    print(" ANALYTICS REPORT")
    print("==============================\n")

    best_trade = max(
        closed,
        key=lambda x: x.get(
            "final_pnl",
            0
        )
    )

    worst_trade = min(
        closed,
        key=lambda x: x.get(
            "final_pnl",
            0
        )
    )

    avg_profit = sum(

        x.get(
            "final_pnl",
            0
        )

        for x in closed

    ) / len(closed)

    avg_duration = sum(

        x.get(
            "duration_minutes",
            0
        )

        for x in closed

    ) / len(closed)

    print(
        f"Best Trade: "
        f"{best_trade['symbol']} "
        f"{best_trade['final_pnl']}%"
    )

    print(
        f"Worst Trade: "
        f"{worst_trade['symbol']} "
        f"{worst_trade['final_pnl']}%"
    )

    print(
        f"Average PNL: "
        f"{round(avg_profit,2)}%"
    )

    print(
        f"Average Duration: "
        f"{round(avg_duration,2)} min"
    )

# =========================
# RUN ENGINE
# =========================

def run_unified_engine():

    print("\n==============================")
    print(" JARVIS ANALYTICS ENGINE")
    print("==============================\n")

    ai_signals = scan_market()

    dex_signals = get_dexscreener_data()

    binance_signals = (
        get_binance_top_movers()
    )

    ranking = rank_opportunities(

        ai_signals=ai_signals,

        dex_signals=dex_signals,

        binance_signals=
        binance_signals

    )

    print(
        f"Ranking generato: "
        f"{len(ranking)}"
    )

    opened = []

    for signal in ranking[:10]:

        if apri_trade_virtuale(
            signal
        ):

            opened.append(signal)

    if len(opened) > 0:

        send_top_signals(
            opened[:2]
        )

    auto_close_trades()

    data = carica_trades()

    print("\n==============================")
    print(" PAPER TRADING")
    print("==============================\n")

    print(
        "Open:",
        len(data["open_trades"])
    )

    print(
        "Closed:",
        len(data["closed_trades"])
    )

    print(
        "Wins:",
        data["stats"]["wins"]
    )

    print(
        "Losses:",
        data["stats"]["losses"]
    )

    print(
        "Profit:",
        round(
            data["stats"]["profit_total"],
            2
        ),
        "%"
    )

    print("\nOPEN TRADES:\n")

    for trade in data["open_trades"]:

        print(

            trade["symbol"],

            "| Entry:",
            trade["entry_price"],

            "| Current:",
            trade.get(
                "current_price",
                "-"
            ),

            "| PNL:",
            trade.get(
                "current_pnl",
                "-"
            ),

            "%"

        )

    analytics_report(data)

    print("\nEngine completato.\n")

    return ranking

# =========================
# START
# =========================

if __name__ == "__main__":

    run_unified_engine()