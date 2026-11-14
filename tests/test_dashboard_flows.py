from contextlib import closing
import os
import sqlite3
import tempfile
import unittest
from werkzeug.security import generate_password_hash

import app as application


class DashboardFlowTests(unittest.TestCase):
    def setUp(self):
        self.original_db_path = application.DB_PATH
        self.original_testing = application.app.config["TESTING"]
        self.original_csrf = application.app.config["WTF_CSRF_ENABLED"]

        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        with closing(sqlite3.connect(self.db_path)) as db:
            with db:
                db.execute("""
                    CREATE TABLE accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        account_number TEXT UNIQUE NOT NULL,
                        holder_name TEXT NOT NULL,
                        pin_hash TEXT NOT NULL,
                        balance_paise INTEGER NOT NULL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'ACTIVE',
                        phone TEXT,
                        email TEXT,
                        address TEXT
                    )
                """)
                db.execute("""
                    CREATE TABLE transactions (
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
                # Seed accounts
                db.execute("""
                    INSERT INTO accounts
                    (account_number, holder_name, pin_hash, balance_paise, status, phone, email, address)
                    VALUES
                    ('100200300', 'Demo User', ?, 500000, 'ACTIVE', '9876543210', 'demo@example.com', '123 Demo St'),
                    ('200300400', 'Pending User', ?, 0, 'PENDING', '9123456780', 'pending@example.com', '456 Test Ave'),
                    ('300400500', 'Blocked User', ?, 10000, 'BLOCKED', '9234567890', 'blocked@example.com', '789 Blocked Rd')
                """, (
                    generate_password_hash("1234"),
                    generate_password_hash("1234"),
                    generate_password_hash("1234")
                ))

        application.DB_PATH = self.db_path
        application.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = application.app.test_client()

    def tearDown(self):
        application.DB_PATH = self.original_db_path
        application.app.config.update(
            TESTING=self.original_testing,
            WTF_CSRF_ENABLED=self.original_csrf
        )
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def sign_in_as_admin(self):
        with self.client.session_transaction() as session:
            session["is_admin"] = True
            session["admin_username"] = "admin"

    def sign_in_as_customer(self, account_id=1, account_number="100200300", name="Demo User"):
        with self.client.session_transaction() as session:
            session["account_id"] = account_id
            session["account_number"] = account_number
            session["holder_name"] = name

    def test_admin_dashboard_and_manage_customers(self):
        self.sign_in_as_admin()

        # Admin dashboard
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Dashboard", res.data)
        self.assertIn(b"Manage Customers", res.data)

        # Manage customers directory - the reported issue
        res = self.client.get("/admin/customers")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Customer Management", res.data)
        self.assertIn(b"Demo User", res.data)
        self.assertIn(b"Pending User", res.data)
        self.assertIn(b"Back to Dashboard", res.data)
        self.assertIn(b"Edit details", res.data)

        # Alias /admin/customer redirects to /admin/customers
        res = self.client.get("/admin/customer")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/customers", res.headers["Location"])

    def test_admin_customer_status_actions(self):
        self.sign_in_as_admin()

        # Approve pending user (id=2)
        res = self.client.post("/admin/customer/2/approve")
        self.assertEqual(res.status_code, 302)

        with closing(sqlite3.connect(self.db_path)) as db:
            status = db.execute("SELECT status FROM accounts WHERE id=2").fetchone()[0]
            self.assertEqual(status, "ACTIVE")

        # Block user (id=2)
        res = self.client.post("/admin/customer/2/block")
        self.assertEqual(res.status_code, 302)
        with closing(sqlite3.connect(self.db_path)) as db:
            status = db.execute("SELECT status FROM accounts WHERE id=2").fetchone()[0]
            self.assertEqual(status, "BLOCKED")

        # Unblock user (id=2)
        res = self.client.post("/admin/customer/2/unblock")
        self.assertEqual(res.status_code, 302)
        with closing(sqlite3.connect(self.db_path)) as db:
            status = db.execute("SELECT status FROM accounts WHERE id=2").fetchone()[0]
            self.assertEqual(status, "ACTIVE")

        # Close zero-balance account (id=2)
        res = self.client.post("/admin/customer/2/close")
        self.assertEqual(res.status_code, 302)
        with closing(sqlite3.connect(self.db_path)) as db:
            status = db.execute("SELECT status FROM accounts WHERE id=2").fetchone()[0]
            self.assertEqual(status, "CLOSED")

    def test_customer_dashboard_and_transactions(self):
        self.sign_in_as_customer()

        # Customer dashboard
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Demo User", res.data)
        self.assertIn(b"AVAILABLE BALANCE", res.data)

        # Deposit
        res = self.client.post("/transaction", data={
            "transaction_type": "deposit",
            "amount": "250.00"
        })
        self.assertEqual(res.status_code, 302)
        self.assertIn("/receipt/", res.headers["Location"])

        # History
        res = self.client.get("/history")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"DEPOSIT", res.data)
        self.assertIn(b"250.00", res.data)

        # Withdraw
        res = self.client.post("/transaction", data={
            "transaction_type": "withdraw",
            "amount": "100.00"
        })
        self.assertEqual(res.status_code, 302)

        # Check balance
        with closing(sqlite3.connect(self.db_path)) as db:
            bal = db.execute("SELECT balance_paise FROM accounts WHERE id=1").fetchone()[0]
            # 500000 + 25000 - 10000 = 515000
            self.assertEqual(bal, 515000)

    def test_customer_pin_change(self):
        self.sign_in_as_customer()

        # Invalid current pin
        res = self.client.post("/change-pin", data={
            "old_pin": "9999",
            "new_pin": "5678",
            "confirm_pin": "5678"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Current PIN is incorrect", res.data)

        # Valid pin change
        res = self.client.post("/change-pin", data={
            "old_pin": "1234",
            "new_pin": "5678",
            "confirm_pin": "5678"
        })
        self.assertEqual(res.status_code, 302)

    def test_auth_redirects_when_already_logged_in(self):
        # Admin logged in visiting login page redirects to admin_dashboard
        self.sign_in_as_admin()
        res = self.client.get("/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/admin/dashboard", res.headers["Location"])

        # Customer logged in visiting login page redirects to dashboard
        self.sign_in_as_customer()
        res = self.client.get("/")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/dashboard", res.headers["Location"])


if __name__ == "__main__":
    unittest.main()
