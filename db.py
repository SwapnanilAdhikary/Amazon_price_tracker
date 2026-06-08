import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("tracker.db")


def initialize_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT,
                target_price REAL,
                platform TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )


def add_product(title, url, target_price, platform):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            INSERT INTO products (title, url, target_price, platform)
            VALUES (?, ?, ?, ?)
            """,
            (title, url, target_price, platform),
        )
        return cursor.lastrowid


def log_price(product_id, price):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
            """,
            (product_id, price),
        )
        return cursor.lastrowid