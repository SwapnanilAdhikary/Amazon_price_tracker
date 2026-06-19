import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("tracker.db")


def initialize_db():
    try:
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    recommendation TEXT,
                    deal_score INTEGER,
                    payload TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(product_id) REFERENCES products(id)
                )
                """
            )
    except sqlite3.Error:
        print(
            "Database initialization failed. If this is a legacy developer database with duplicate rows or a corrupted schema, delete the local 'tracker.db' file and restart the application."
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


def get_product_by_id(product_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT id, title, url, target_price, platform
            FROM products
            WHERE id = ?
            """,
            (product_id,),
        )
        return cursor.fetchone()


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


def get_price_history(product_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT id, product_id, price, timestamp
            FROM price_history
            WHERE product_id = ?
            ORDER BY timestamp ASC, id ASC
            """,
            (product_id,),
        )
        return cursor.fetchall()


def log_ai_analysis(product_id, recommendation, deal_score, payload_json_string):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            INSERT INTO ai_analysis (product_id, recommendation, deal_score, payload)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, recommendation, deal_score, payload_json_string),
        )
        return cursor.lastrowid


def get_latest_ai_analysis(product_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        cursor = connection.execute(
            """
            SELECT id, product_id, recommendation, deal_score, payload, timestamp
            FROM ai_analysis
            WHERE product_id = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT 1
            """,
            (product_id,)
        )
        row = cursor.fetchone()
        return tuple(row) if row is not None else None