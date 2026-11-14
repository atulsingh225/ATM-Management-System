
import os
import sqlite3
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

DB_PATH = os.getenv("DATABASE", "atm.db")


def init_db(db_path=None):
    target_path = db_path or DB_PATH
    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON")

    # Accounts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT UNIQUE NOT NULL,
            holder_name TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            balance_paise INTEGER NOT NULL DEFAULT 0
                CHECK(balance_paise >= 0),
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            phone TEXT,
            email TEXT,
            address TEXT
        )
    """)

    # Transactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount_paise INTEGER NOT NULL,
            balance_after_paise INTEGER NOT NULL,
            reference TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        )
    """)

    # Indexes for performance
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_accounts_number ON accounts(account_number)"
    )

    # Safely add missing columns to existing databases
    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(accounts)").fetchall()
    ]

    new_columns = {
        "status": "TEXT NOT NULL DEFAULT 'ACTIVE'",
        "phone": "TEXT",
        "email": "TEXT",
        "address": "TEXT"
    }

    for column, definition in new_columns.items():
        if column not in columns:
            conn.execute(
                f"ALTER TABLE accounts ADD COLUMN {column} {definition}"
            )

    # Create demo account only if it does not already exist
    account = conn.execute(
        "SELECT id FROM accounts WHERE account_number = ?",
        ("100200300",)
    ).fetchone()

    if account is None:
        conn.execute("""
            INSERT INTO accounts
            (account_number, holder_name, pin_hash,
             balance_paise, status)
            VALUES (?, ?, ?, ?, 'ACTIVE')
        """, (
            "100200300",
            "Demo User",
            generate_password_hash("1234"),
            5000000
        ))

    conn.commit()
    conn.close()

    print("Database setup completed successfully!")
    print("Customer details columns are ready.")
    print("Existing accounts and transactions preserved.")


if __name__ == "__main__":
    init_db()
