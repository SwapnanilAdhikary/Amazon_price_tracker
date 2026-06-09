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
                url TEXT UNIQUE,
                target_price REAL,
                platform TEXT
            )
            """
        )
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_products_url ON products(url);"
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
        connection.execute(
            """
            INSERT INTO products (title, url, target_price, platform)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title=excluded.title,
                target_price=excluded.target_price,
                platform=excluded.platform
            """,
            (title, url, target_price, platform),
        )
        cursor = connection.execute(
            "SELECT id FROM products WHERE url = ?",
            (url,),
        )
        row = cursor.fetchone()
        return row[0] if row is not None else None


def get_all_products():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT id, title, url, target_price, platform
            FROM products
            ORDER BY id
            """
        )
        return cursor.fetchall()


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


def get_latest_price(product_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT price
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
            """,
            (product_id,),
        )
        row = cursor.fetchone()
        return row[0] if row is not None else None