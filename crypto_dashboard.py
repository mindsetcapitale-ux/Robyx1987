# crypto_dashboard.py
# JARVIS DASHBOARD + PAPER TRADING VIEW

from flask import Flask, render_template_string
import datetime
import json
import os

TRADING_FILE = "unified_paper_trades.json"

app = Flask(__name__)


def load_trading_data():
    if not os.path.exists(TRADING_FILE):
        return {
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

    try:
        with open(TRADING_FILE, "r") as file:
            return json.load(file)

    except:
        return {
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


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>JARVIS CONTROL PANEL</title>

<style>
body {
    background: radial-gradient(circle at top, #0f1729 0%, #050816 60%);
    color: #00eaff;
    font-family: Arial;
    padding: 20px;
}

.card {
    background: rgba(16,24,43,0.78);
    border: 1px solid rgba(0,234,255,0.25);
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 22px;
}

.title {
    font-size: 42px;
    font-weight: bold;
    color: white;
}

.green {
    color: #00ff99;
}

.red {
    color: #ff4444;
}

.coin {
    margin-bottom: 15px;
    padding: 14px;
    border-radius: 14px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(0,234,255,0.12);
}

.stat {
    font-size: 18px;
    margin-bottom: 10px;
}
</style>

<script>
setInterval(() => {
    location.reload();
}, 15000);
</script>

</head>

<body>

<div class="card">
    <div class="title">🧠 JARVIS CONTROL PANEL</div>
    <p class="green">ONLINE • PAPER TRADING MONITOR ACTIVE</p>
    <p>Last Update: {{ update_time }}</p>
</div>

<div class="card">
    <h2>📊 PERFORMANCE</h2>

    <div class="stat">Total Opened: {{ stats.total_opened }}</div>
    <div class="stat">Total Closed: {{ stats.total_closed }}</div>
    <div class="stat">Wins: {{ stats.wins }}</div>
    <div class="stat">Losses: {{ stats.losses }}</div>
    <div class="stat">Profit Total: {{ stats.profit_total }}%</div>
</div>

<div class="card">
    <h2>🟢 OPEN TRADES</h2>

    {% for trade in open_trades %}
    <div class="coin">
        <b>{{ trade.symbol }}</b><br>
        Source: {{ trade.source }}<br>
        Score: {{ trade.score }}<br>
        Entry: {{ trade.entry_price }}<br>
        Current: {{ trade.current_price }}<br>
        PNL: {{ trade.current_pnl }}%<br>
        TP: {{ trade.take_profit }}%<br>
        SL: {{ trade.stop_loss }}%<br>
        Opened: {{ trade.opened_at }}
    </div>
    {% endfor %}

    {% if open_trades|length == 0 %}
    <p>Nessun trade aperto.</p>
    {% endif %}
</div>

<div class="card">
    <h2>🔴 CLOSED TRADES</h2>

    {% for trade in closed_trades %}
    <div class="coin">
        <b>{{ trade.symbol }}</b><br>
        Result: {{ trade.close_reason }}<br>
        Entry: {{ trade.entry_price }}<br>
        Close: {{ trade.close_price }}<br>
        Final PNL: {{ trade.final_pnl }}%<br>
        Duration: {{ trade.duration_minutes }} min<br>
        Closed: {{ trade.closed_at }}
    </div>
    {% endfor %}

    {% if closed_trades|length == 0 %}
    <p>Nessun trade chiuso.</p>
    {% endif %}
</div>

</body>
</html>
"""


@app.route("/")
def home():
    data = load_trading_data()

    return render_template_string(
        HTML,
        stats=data.get("stats", {}),
        open_trades=data.get("open_trades", []),
        closed_trades=data.get("closed_trades", [])[-10:],
        update_time=str(datetime.datetime.now())
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )