import sqlite3
from datetime import datetime

DB_NAME = "bot.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name    TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id   INTEGER PRIMARY KEY,
            user_id      INTEGER,
            user_message TEXT,
            bot_response TEXT,
            timestamp    TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_queries (
            query_id   INTEGER PRIMARY KEY,
            user_id    INTEGER,
            city       TEXT,
            query_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


def save_user(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE name=?", (name,))
    result = cursor.fetchone()

    if result:
        user_id = result[0]
        print(f"Пользователь найден: {name} (ID: {user_id})")
    else:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        user_id = cursor.lastrowid
        print(f"Добавлен новый пользователь: {name} (ID: {user_id})")

    conn.commit()
    conn.close()
    return user_id


def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return {"user_id": result[0], "name": result[1]} if result else None


def log_message_db(user_id, user_message, bot_response):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_id, user_message, bot_response, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, user_message, bot_response, datetime.now())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при логировании сообщения: {e}")


def log_weather_query(user_id, city):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO weather_queries (user_id, city, query_date) VALUES (?, ?, ?)",
            (user_id, city, datetime.now())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при логировании запроса погоды: {e}")