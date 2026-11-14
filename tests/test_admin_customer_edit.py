from contextlib import closing
import os
import sqlite3
import tempfile
import unittest

import app as application


class AdminCustomerEditTests(unittest.TestCase):
    def setUp(self):
        self.original_db_path = application.DB_PATH
        self.original_testing = application.app.config["TESTING"]
        self.original_csrf = application.app.config["WTF_CSRF_ENABLED"]

        file_descriptor, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(file_descriptor)

        with closing(sqlite3.connect(self.db_path)) as db:
            with db:
                db.execute("""
                    CREATE TABLE accounts (
                        id INTEGER PRIMARY KEY,
                        account_number TEXT UNIQUE NOT NULL,
                        holder_name TEXT NOT NULL,
                        pin_hash TEXT NOT NULL,
                        balance_paise INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        address TEXT
                    )
                """)
                db.execute("""
                    INSERT INTO accounts
                    VALUES (1, '1234567890', 'Old Name', 'unchanged-hash',
                            5000, 'ACTIVE', '9876543210',
                            'old@example.com', 'Old Address')
                """)

        application.DB_PATH = self.db_path
        application.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = application.app.test_client()

    def tearDown(self):
        application.DB_PATH = self.original_db_path
        application.app.config.update(
            TESTING=self.original_testing,
            WTF_CSRF_ENABLED=self.original_csrf
        )
        os.unlink(self.db_path)

    def sign_in_as_admin(self):
        with self.client.session_transaction() as session:
            session["is_admin"] = True
            session["admin_username"] = "test-admin"

    def get_account(self):
        with closing(sqlite3.connect(self.db_path)) as db:
            return db.execute(
                "SELECT * FROM accounts WHERE id = 1"
            ).fetchone()

    def test_customer_pages_require_admin_access(self):
        response = self.client.get("/admin/customers")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_customer_directory_links_to_edit_form(self):
        self.sign_in_as_admin()

        directory = self.client.get("/admin/customers")
        self.assertEqual(directory.status_code, 200)
        self.assertIn(b"Edit details", directory.data)

        edit_page = self.client.get("/admin/customer/1/edit")
        self.assertEqual(edit_page.status_code, 200)
        self.assertIn(b"Old Name", edit_page.data)
        self.assertIn(b"1234567890", edit_page.data)

    def test_edit_validates_and_updates_only_contact_details(self):
        self.sign_in_as_admin()

        invalid = self.client.post(
            "/admin/customer/1/edit",
            data={
                "holder_name": "New Name",
                "phone": "123",
                "email": "new@example.com",
                "address": "New Address"
            }
        )
        self.assertEqual(invalid.status_code, 200)
        self.assertIn(b"valid 10-digit mobile number", invalid.data)
        self.assertEqual(self.get_account()[2], "Old Name")

        saved = self.client.post(
            "/admin/customer/1/edit",
            data={
                "holder_name": "New Name",
                "phone": "9123456780",
                "email": "NEW@example.com",
                "address": "New Residential Address"
            }
        )
        self.assertEqual(saved.status_code, 302)

        account = self.get_account()
        self.assertEqual(
            account[2:9],
            (
                "New Name",
                "unchanged-hash",
                5000,
                "ACTIVE",
                "9123456780",
                "new@example.com",
                "New Residential Address"
            )
        )


if __name__ == "__main__":
    unittest.main()
