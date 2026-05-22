# core/error_logger.py

import os
from datetime import datetime


LOG_FOLDER = "logs"
ERROR_LOG_FILE = "logs/errors.log"


def ensure_log_folder():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)


def log_error(source, error):
    ensure_log_folder()

    timestamp = datetime.now().isoformat()

    message = f"""
[{timestamp}]

SOURCE:
{source}

ERROR:
{str(error)}

====================================
"""

    with open(
        ERROR_LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(message)

    print(message)