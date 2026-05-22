# main.py

from flask import Flask
import threading
import sqlite3
import os

from core.telegram_bot_listener import main as telegram_main
from cloud_health_monitor import start_health_monitor
from core.task_supervisor import start_supervisor
from core.database import initialize_database


app = Flask(__name__)

DB_FILE = "data/jarvis.db"


def fetch_rows(query, limit=20):
    if not os.path.exists(DB_FILE):
        return []

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(query, (limit,))
    rows = cursor.fetchall()

    connection.close()

    return rows


@app.route("/")
def home():
    return """
    <h1>🤖 Jarvis AI Online 24/7</h1>
    <p>Dashboard attiva.</p>
    <ul>
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/health">Health</a></li>
    </ul>
    """


@app.route("/health")
def health():
    return {
        "status": "online",
        "service": "jarvis-ai",
        "mode": "cloud-24-7"
    }


@app.route("/dashboard")
def dashboard():
    signals = fetch_rows(
        "SELECT symbol, score, category, source, timestamp FROM signals ORDER BY id DESC LIMIT ?",
        20
    )

    errors = fetch_rows(
        "SELECT source, error, timestamp FROM errors ORDER BY id DESC LIMIT ?",
        10
    )

    heartbeats = fetch_rows(
        "SELECT status, timestamp FROM heartbeats ORDER BY id DESC LIMIT ?",
        10
    )

    html = """
    <html>
    <head>
        <title>Jarvis Dashboard</title>
        <style>
            body {
                background: #0b0f14;
                color: #e5e7eb;
                font-family: Arial, sans-serif;
                padding: 30px;
            }
            h1, h2 {
                color: #38bdf8;
            }
            .card {
                background: #111827;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 12px;
                border: 1px solid #1f2937;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                border-bottom: 1px solid #374151;
                text-align: left;
            }
            th {
                color: #facc15;
            }
            .ok {
                color: #22c55e;
            }
            .error {
                color: #ef4444;
            }
        </style>
    </head>
    <body>
        <h1>🤖 Jarvis AI Dashboard</h1>

        <div class="card">
            <h2>🟢 System Status</h2>
            <p class="ok">ONLINE 24/7</p>
            <p>Cloud mode active</p>
        </div>

        <div class="card">
            <h2>🚨 Latest Signals</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Score</th>
                    <th>Category</th>
                    <th>Source</th>
                    <th>Time</th>
                </tr>
    """

    for row in signals:
        html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                    <td>{row[3]}</td>
                    <td>{row[4]}</td>
                </tr>
        """

    html += """
            </table>
        </div>

        <div class="card">
            <h2>💓 Heartbeats</h2>
            <table>
                <tr>
                    <th>Status</th>
                    <th>Time</th>
                </tr>
    """

    for row in heartbeats:
        html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                </tr>
        """

    html += """
            </table>
        </div>

        <div class="card">
            <h2>❌ Latest Errors</h2>
            <table>
                <tr>
                    <th>Source</th>
                    <th>Error</th>
                    <th>Time</th>
                </tr>
    """

    for row in errors:
        html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td class="error">{row[1]}</td>
                    <td>{row[2]}</td>
                </tr>
        """

    html += """
            </table>
        </div>
    </body>
    </html>
    """

    return html


def start_telegram():
    telegram_main()


def start_health():
    start_health_monitor()


initialize_database()

telegram_thread = threading.Thread(target=start_telegram)
telegram_thread.daemon = True
telegram_thread.start()

health_thread = threading.Thread(target=start_health)
health_thread.daemon = True
health_thread.start()

supervisor_thread = threading.Thread(target=start_supervisor)
supervisor_thread.daemon = True
supervisor_thread.start()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )