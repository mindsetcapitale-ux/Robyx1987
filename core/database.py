# core/database.py

import sqlite3
import os
from datetime import datetime


DB_FOLDER = "data"
DB_FILE = "data/jarvis.db"


def ensure_database_folder():

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)


def get_connection():

    ensure_database_folder()

    connection = sqlite3.connect(DB_FILE)

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # =========================
    # SIGNALS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        score REAL,
        category TEXT,
        source TEXT,
        timestamp TEXT
    )
    """)

    # =========================
    # ERRORS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        error TEXT,
        timestamp TEXT
    )
    """)

    # =========================
    # HEARTBEATS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS heartbeats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT,
        timestamp TEXT
    )
    """)

    # =========================
    # TASKS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        status TEXT,
        timestamp TEXT
    )
    """)

    connection.commit()
    connection.close()

    print("JARVIS DATABASE READY")


def save_signal(
    symbol,
    score,
    category,
    source
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO signals (
        symbol,
        score,
        category,
        source,
        timestamp
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        symbol,
        score,
        category,
        source,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def save_error(
    source,
    error
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO errors (
        source,
        error,
        timestamp
    )
    VALUES (?, ?, ?)
    """, (
        source,
        str(error),
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def save_heartbeat(status="ONLINE"):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO heartbeats (
        status,
        timestamp
    )
    VALUES (?, ?)
    """, (
        status,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def save_task_status(
    task_name,
    status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO tasks (
        task_name,
        status,
        timestamp
    )
    VALUES (?, ?, ?)
    """, (
        task_name,
        status,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


if __name__ == "__main__":

    initialize_database()