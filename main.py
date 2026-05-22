# main.py

from flask import Flask
import threading

from core.telegram_bot_listener import main as telegram_main
from cloud_health_monitor import start_health_monitor
from core.task_supervisor import start_supervisor


app = Flask(__name__)


@app.route("/")
def home():
    return "Jarvis AI Online 24/7"


@app.route("/health")
def health():
    return {
        "status": "online",
        "service": "jarvis-ai",
        "mode": "cloud-24-7"
    }


def start_telegram():
    telegram_main()


def start_health():
    start_health_monitor()


telegram_thread = threading.Thread(
    target=start_telegram
)

telegram_thread.daemon = True
telegram_thread.start()


health_thread = threading.Thread(
    target=start_health
)

health_thread.daemon = True
health_thread.start()


supervisor_thread = threading.Thread(
    target=start_supervisor
)

supervisor_thread.daemon = True
supervisor_thread.start()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )