# core/task_supervisor.py

import threading
import time
from datetime import datetime

from core.telegram_alerts import (
    send_telegram_message
)

from core.error_logger import (
    log_error
)

from core.signal_reporter import (
    run_signal_reporter
)

from engines.live_momentum_engine import (
    scan_live_momentum
)


CHECK_INTERVAL = 300


TASKS = {
    "signals": {
        "function": lambda: run_signal_reporter(
            send_telegram=False
        ),
        "thread": None,
        "last_run": None,
    },

    "momentum": {
        "function": lambda: scan_live_momentum(
            send_telegram=False
        ),
        "thread": None,
        "last_run": None,
    },
}


def build_task(task_name):

    def runner():

        while True:

            try:

                TASKS[task_name][
                    "last_run"
                ] = datetime.now()

                TASKS[task_name][
                    "function"
                ]()

            except Exception as e:

                log_error(
                    f"Supervisor-{task_name}",
                    e
                )

            time.sleep(
                CHECK_INTERVAL
            )

    return runner


def start_task(task_name):

    thread = threading.Thread(
        target=build_task(task_name)
    )

    thread.daemon = True

    thread.start()

    TASKS[task_name][
        "thread"
    ] = thread

    send_telegram_message(
        f"""
🟢 TASK STARTED

Task:
{task_name}
"""
    )


def supervisor_loop():

    print(
        "JARVIS TASK SUPERVISOR ONLINE"
    )

    while True:

        try:

            for task_name, data in TASKS.items():

                thread = data.get(
                    "thread"
                )

                if (
                    thread is None
                    or not thread.is_alive()
                ):

                    send_telegram_message(
                        f"""
⚠️ TASK RESTART

Task:
{task_name}
"""
                    )

                    start_task(task_name)

        except Exception as e:

            log_error(
                "TaskSupervisor",
                e
            )

        time.sleep(30)


def start_supervisor():

    supervisor_thread = threading.Thread(
        target=supervisor_loop
    )

    supervisor_thread.daemon = True

    supervisor_thread.start()


if __name__ == "__main__":

    start_supervisor()

    while True:
        time.sleep(60)