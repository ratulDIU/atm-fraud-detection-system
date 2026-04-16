import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_NAME = os.path.join(BASE_DIR, "atm.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER UNIQUE,
            status TEXT DEFAULT 'ACTIVE',
            blocked_until TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account INTEGER,
            amount INTEGER,
            location TEXT,
            timestamp TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fraud_reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account INTEGER,
            risk_score INTEGER,
            risk_level TEXT,
            action TEXT,
            created_at TEXT
        );
        """
    )

    conn.commit()
    conn.close()


def get_account(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT account_number, status, blocked_until FROM accounts WHERE account_number = ?",
        (account_number,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "account_number": row[0],
        "status": row[1],
        "blocked_until": row[2],
    }


def create_account(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO accounts(account_number, status, blocked_until) VALUES (?, ?, ?)",
        (account_number, "ACTIVE", None),
    )
    conn.commit()
    conn.close()
    return get_account(account_number)


def update_account_status(account_number, status, blocked_until=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET status = ?, blocked_until = ? WHERE account_number = ?",
        (status, blocked_until, account_number),
    )
    conn.commit()
    conn.close()


def add_transactions(account_number, transactions):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    rows = [
        (account_number, int(t["amount"]), t["location"], now)
        for t in transactions
    ]
    cursor.executemany(
        "INSERT INTO transactions(account, amount, location, timestamp) VALUES (?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    conn.close()


def add_fraud_report(account_number, risk_score, risk_level, action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fraud_reports(account, risk_score, risk_level, action, created_at) VALUES (?, ?, ?, ?, ?)",
        (account_number, risk_score, risk_level, action, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()