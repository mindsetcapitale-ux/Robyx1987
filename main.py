# main.py

from flask import Flask
import threading

from core.telegram_bot_listener import main as telegram_main

app = Flask(__name__)


@app.route("/")
def home():
    return "Jarvis AI Online"


def start_telegram():
    telegram_main()


telegram_thread = threading.Thread(
    target=start_telegram
)

telegram_thread.daemon = True
telegram_thread.start()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )