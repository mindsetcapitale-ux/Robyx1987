# crypto_dashboard.py
# JARVIS AI CLOUD DASHBOARD

from flask import Flask, render_template_string, request
import datetime
import json
import os

from unified_trading_engine import run_unified_engine

TRADING_FILE = "unified_paper_trades.json"

CONTROL_KEY = os.environ.get(
    "JARVIS_CONTROL_KEY",
    "jarvis123"
)

app = Flask(__name__)

last_run_status = "IDLE"
last_run_time = "-"


def load_trading_data():

    if not os.path.exists(TRADING_FILE):

        return {
            "open_trades": [],
            "closed_trades": [],
            "stats": {}
        }

    try:

        with open(TRADING_FILE, "r") as file:

            return json.load(file)

    except:

        return {
            "open_trades": [],
            "closed_trades": [],
            "stats": {}
        }


HTML = """
<!DOCTYPE html>
<html>

<head>

<title>JARVIS AI CLOUD</title>

<style>

body {

    background:
    radial-gradient(circle at top,
    #0f1729 0%,
    #050816 60%);

    color: #00eaff;

    font-family: Arial;

    padding: 20px;
}

.card {

    background:
    rgba(16,24,43,0.78);

    border:
    1px solid rgba(0,234,255,0.25);

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

.yellow {
    color: #ffd966;
}

.coin {

    margin-bottom: 15px;

    padding: 14px;

    border-radius: 14px;

    background:
    rgba(255,255,255,0.03);

    border:
    1px solid rgba(0,234,255,0.12);
}

.button {

    display: inline-block;

    padding: 14px 20px;

    border-radius: 14px;

    background: #00eaff;

    color: #050816;

    font-weight: bold;

    text-decoration: none;

    margin-top: 10px;
}

.stat {

    font-size: 18px;

    margin-bottom: 10px;
}

</style>

<script>

setInterval(() => {

    location.reload();

}, 20000);

</script>

</head>

<body>

<div class="card">

<div class="title">
🧠 JARVIS AI CLOUD
</div>

<p class="green">
ONLINE • AI ENGINE ACTIVE
</p>

<p>
Last Update:
{{ update_time }}
</p>

<p>
Last Engine Run:
{{ last_run_time }}
</p>

<p>
Status:
{{ last_run_status }}
</p>

<a class="button"
href="/run-engine?key={{ control_key }}">

🚀 AVVIA ENGINE

</a>

</div>

<div class="card">

<h2>
📊 PERFORMANCE
</h2>

<div class="stat">
Total Opened:
{{ stats.total_opened }}
</div>

<div class="stat">
Total Closed:
{{ stats.total_closed }}
</div>

<div class="stat">
Wins:
{{ stats.wins }}
</div>

<div class="stat">
Losses:
{{ stats.losses }}
</div>

<div class="stat">
Profit Total:
{{ stats.profit_total }}%
</div>

</div>

<div class="card">

<h2>
🟢 OPEN TRADES
</h2>

{% for trade in open_trades %}

<div class="coin">

<b>
{{ trade.symbol }}
</b>

<br>

Source:
{{ trade.source }}

<br>

Score:
{{ trade.score }}

<br>

Confidence:
{% if trade.confidence >= 85 %}
<span class="green">
{{ trade.confidence }}
</span>

{% elif trade.confidence >= 70 %}

<span class="yellow">
{{ trade.confidence }}
</span>

{% else %}

<span class="red">
{{ trade.confidence }}
</span>

{% endif %}

-
{{ trade.confidence_status }}

<br>

Entry:
{{ trade.entry_price }}

<br>

Current:
{{ trade.current_price }}

<br>

PNL:
{{ trade.current_pnl }}%

<br>

TP:
{{ trade.take_profit }}%

<br>

SL:
{{ trade.stop_loss }}%

<br>

Opened:
{{ trade.opened_at }}

</div>

{% endfor %}

{% if open_trades|length == 0 %}

<p>
Nessun trade aperto.
</p>

{% endif %}

</div>

<div class="card">

<h2>
🔴 CLOSED TRADES
</h2>

{% for trade in closed_trades %}

<div class="coin">

<b>
{{ trade.symbol }}
</b>

<br>

Result:
{{ trade.close_reason }}

<br>

Final PNL:
{{ trade.final_pnl }}%

<br>

Confidence:
{{ trade.confidence }}

<br>

Duration:
{{ trade.duration_minutes }} min

<br>

Closed:
{{ trade.closed_at }}

</div>

{% endfor %}

{% if closed_trades|length == 0 %}

<p>
Nessun trade chiuso.
</p>

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

        open_trades=data.get(
            "open_trades",
            []
        ),

        closed_trades=data.get(
            "closed_trades",
            []
        )[-10:],

        update_time=str(
            datetime.datetime.now()
        ),

        last_run_status=last_run_status,

        last_run_time=last_run_time,

        control_key=CONTROL_KEY
    )


@app.route("/run-engine")
def run_engine():

    global last_run_status
    global last_run_time

    key = request.args.get("key", "")

    if key != CONTROL_KEY:

        return "ACCESS DENIED", 403

    try:

        last_run_status = "RUNNING"

        last_run_time = str(
            datetime.datetime.now()
        )

        run_unified_engine()

        last_run_status = "COMPLETED"

        last_run_time = str(
            datetime.datetime.now()
        )

        return """
        <h1>
        🚀 JARVIS ENGINE COMPLETATO
        </h1>

        <a href="/">
        Torna Dashboard
        </a>
        """

    except Exception as e:

        last_run_status = f"ERROR: {e}"

        return str(e), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )