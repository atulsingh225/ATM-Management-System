
import os
import re
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from decimal import Decimal, InvalidOperation

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
secret_key = os.getenv("SECRET_KEY")
if not secret_key or secret_key == "replace-this-with-your-own-secret-key":
    if os.getenv("VERCEL"):
        secret_key = "nova-bank-vercel-secure-production-key-2026"
    else:
        raise RuntimeError("Please set a valid SECRET_KEY in your .env file.")

app.config["SECRET_KEY"] = secret_key
app.config["WTF_CSRF_TIME_LIMIT"] = 3600
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CSRFProtect(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

def setup_db_path():
    if os.getenv("VERCEL"):
        import tempfile
        target_dir = tempfile.gettempdir()
        os.makedirs(target_dir, exist_ok=True)
        target_db = os.path.join(target_dir, "atm.db")
        if not os.path.exists(target_db):
            base_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atm.db")
            if os.path.exists(base_db):
                try:
                    import shutil
                    shutil.copy2(base_db, target_db)
                except Exception:
                    pass
            if not os.path.exists(target_db):
                try:
                    from init_db import init_db
                    init_db(target_db)
                except Exception:
                    pass
        return target_db
    return os.getenv("DATABASE", "atm.db")

DB_PATH = setup_db_path()


# ==================================================
# DATABASE
# ==================================================

def get_db():
    global DB_PATH
    if "db" not in g:
        if os.getenv("VERCEL") and not os.path.exists(DB_PATH):
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            base_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atm.db")
            if os.path.exists(base_db):
                try:
                    import shutil
                    shutil.copy2(base_db, DB_PATH)
                except Exception:
                    pass
            if not os.path.exists(DB_PATH):
                from init_db import init_db
                init_db(DB_PATH)
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.after_request
def set_security_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# ==================================================
# SECURITY DECORATORS
# ==================================================

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "account_id" not in session or session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view


# ==================================================
# HELPERS
# ==================================================

def money(paise):
    return f"₹{int(paise or 0) / 100:,.2f}"


def format_dt(value):
    if not value:
        return ""
    try:
        parts = str(value).split(".")[0]
        dt = datetime.strptime(parts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)


@app.context_processor
def inject_helpers():
    return {"money": money, "format_dt": format_dt}


def valid_phone(phone):
    return bool(re.fullmatch(r"[6-9][0-9]{9}", phone))


def valid_email(email):
    return bool(
        len(email) <= 254
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    )


# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def admin_login():

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin_username = os.getenv("ADMIN_USERNAME", "owner")
        admin_password_hash = os.getenv(
            "ADMIN_PASSWORD_HASH",
            "scrypt:32768:8:1$klAi2N9VH1nTEaOA$43f9e22b5d0a1fd16e8617ee53f926c83102ec047d18f09c9c3468c08c998c4d82e259aa0c808f45a5cf22ddc4e7353dc754e9cbf95709f3664b64c2223ebfaa"
        )

        try:
            valid_password = (
                bool(admin_password_hash)
                and check_password_hash(admin_password_hash, password)
            )
        except (ValueError, TypeError):
            valid_password = False

        if (
            admin_username
            and secrets.compare_digest(username, admin_username)
            and valid_password
        ):
            session.clear()
            session["is_admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin username or password.", "error")

    return render_template("admin_login.html")


# ==================================================
# ADMIN DASHBOARD & REDIRECTS
# ==================================================

@app.route("/admin")
@app.route("/admin/")
def admin_root():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    db = get_db()

    stats = db.execute("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN status='ACTIVE' THEN 1 ELSE 0 END) AS active_accounts,
            SUM(CASE WHEN status='PENDING' THEN 1 ELSE 0 END) AS pending_accounts,
            SUM(CASE WHEN status='BLOCKED' THEN 1 ELSE 0 END) AS blocked_accounts,
            SUM(CASE WHEN status='CLOSED' THEN 1 ELSE 0 END) AS closed_accounts,
            SUM(CASE WHEN status='REJECTED' THEN 1 ELSE 0 END) AS rejected_accounts
        FROM accounts
    """).fetchone()

    tx_stats = db.execute("""
        SELECT
            COUNT(*) AS total_transactions,
            COALESCE(SUM(
                CASE WHEN UPPER(transaction_type)='DEPOSIT'
                THEN amount_paise ELSE 0 END
            ), 0) AS total_deposits,
            COALESCE(SUM(
                CASE WHEN UPPER(transaction_type)='WITHDRAW'
                THEN amount_paise ELSE 0 END
            ), 0) AS total_withdrawals
        FROM transactions
    """).fetchone()

    recent_transactions = db.execute("""
        SELECT t.*, a.holder_name, a.account_number
        FROM transactions t
        JOIN accounts a ON a.id = t.account_id
        ORDER BY t.id DESC
        LIMIT 10
    """).fetchall()

    return render_template(
        "admin_dashboard.html",
        total_customers=stats["total_customers"] or 0,
        active_accounts=stats["active_accounts"] or 0,
        pending_accounts=stats["pending_accounts"] or 0,
        blocked_accounts=stats["blocked_accounts"] or 0,
        closed_accounts=stats["closed_accounts"] or 0,
        rejected_accounts=stats["rejected_accounts"] or 0,
        total_transactions=tx_stats["total_transactions"] or 0,
        total_deposits=tx_stats["total_deposits"] or 0,
        total_withdrawals=tx_stats["total_withdrawals"] or 0,
        recent_transactions=recent_transactions
    )


# ==================================================
# ADMIN CUSTOMER DIRECTORY
# ==================================================

@app.route("/admin/customer")
@admin_required
def admin_customer_alias():
    return redirect(url_for("admin_customers"))


@app.route("/admin/customers")
@admin_required
def admin_customers():

    db = get_db()
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "ALL").upper()

    allowed = {"ALL", "PENDING", "ACTIVE", "BLOCKED", "CLOSED", "REJECTED"}

    if status not in allowed:
        status = "ALL"

    status_counts = db.execute("""
        SELECT
            COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN status='PENDING' THEN 1 ELSE 0 END), 0) AS pending,
            COALESCE(SUM(CASE WHEN status='ACTIVE' THEN 1 ELSE 0 END), 0) AS active,
            COALESCE(SUM(CASE WHEN status='BLOCKED' THEN 1 ELSE 0 END), 0) AS blocked,
            COALESCE(SUM(CASE WHEN status='CLOSED' THEN 1 ELSE 0 END), 0) AS closed,
            COALESCE(SUM(CASE WHEN status='REJECTED' THEN 1 ELSE 0 END), 0) AS rejected
        FROM accounts
    """).fetchone()

    sql = """
        SELECT id, holder_name, account_number, phone,
               email, address, balance_paise, status
        FROM accounts
        WHERE (
            holder_name LIKE ?
            OR account_number LIKE ?
            OR COALESCE(phone,'') LIKE ?
            OR COALESCE(email,'') LIKE ?
        )
    """

    params = [f"%{search}%"] * 4

    if status != "ALL":
        sql += " AND status = ?"
        params.append(status)

    sql += " ORDER BY id DESC"

    customers = db.execute(sql, params).fetchall()

    return render_template(
        "admin_customers.html",
        customers=customers,
        search=search,
        selected_status=status,
        status_counts=status_counts
    )


# ==================================================
# ADMIN CUSTOMER ACTIONS
# ==================================================

@app.route("/admin/customer/<int:customer_id>/<action>", methods=["POST"])
@admin_required
def admin_customer_action(customer_id, action):

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (customer_id,)
    ).fetchone()

    if account is None:
        flash("Customer not found.", "error")
        return redirect(url_for("admin_customers"))

    current = account["status"]

    if action == "approve" and current == "PENDING":
        new_status = "ACTIVE"

    elif action == "reject" and current == "PENDING":
        new_status = "REJECTED"

    elif action == "block" and current == "ACTIVE":
        new_status = "BLOCKED"

    elif action == "unblock" and current == "BLOCKED":
        new_status = "ACTIVE"

    elif action == "close" and current in ("ACTIVE", "BLOCKED"):
        if account["balance_paise"] != 0:
            flash("Account balance must be ₹0 before closing.", "error")
            return redirect(url_for("admin_customers"))
        new_status = "CLOSED"

    else:
        flash("This action is not allowed for the current account status.", "error")
        return redirect(url_for("admin_customers"))

    db.execute(
        "UPDATE accounts SET status = ? WHERE id = ?",
        (new_status, customer_id)
    )
    db.commit()

    flash(f"Account status updated to {new_status}.", "success")
    return redirect(url_for("admin_customers"))


# ==================================================
# ADMIN EDIT CUSTOMER DETAILS
# ==================================================

@app.route("/admin/customer/<int:customer_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_customer(customer_id):

    db = get_db()
    customer = db.execute(
        """
        SELECT id, holder_name, account_number, phone, email,
               address, balance_paise, status
        FROM accounts
        WHERE id = ?
        """,
        (customer_id,)
    ).fetchone()

    if customer is None:
        flash("Customer not found.", "error")
        return redirect(url_for("admin_customers"))

    form_data = {
        "holder_name": customer["holder_name"],
        "phone": customer["phone"] or "",
        "email": customer["email"] or "",
        "address": customer["address"] or ""
    }

    if request.method == "POST":
        form_data = {
            "holder_name": request.form.get("holder_name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "email": request.form.get("email", "").strip().lower(),
            "address": request.form.get("address", "").strip()
        }

        validation_error = None

        if not 2 <= len(form_data["holder_name"]) <= 100:
            validation_error = "Name must contain 2 to 100 characters."
        elif not valid_phone(form_data["phone"]):
            validation_error = "Enter a valid 10-digit mobile number."
        elif not valid_email(form_data["email"]):
            validation_error = "Enter a valid email address."
        elif not 5 <= len(form_data["address"]) <= 300:
            validation_error = "Enter a valid address."

        if validation_error:
            flash(validation_error, "error")
        else:
            try:
                db.execute(
                    """
                    UPDATE accounts
                    SET holder_name = ?, phone = ?, email = ?, address = ?
                    WHERE id = ?
                    """,
                    (
                        form_data["holder_name"],
                        form_data["phone"],
                        form_data["email"],
                        form_data["address"],
                        customer_id
                    )
                )
                db.commit()
            except sqlite3.Error:
                db.rollback()
                flash("Customer details could not be updated. Please try again.", "error")
            else:
                flash("Customer details updated successfully.", "success")
                return redirect(url_for("admin_customers"))

    return render_template(
        "admin_customer_edit.html",
        customer=customer,
        form_data=form_data
    )


# ==================================================
# ADMIN ALL TRANSACTIONS
# ==================================================

@app.route("/admin/transactions")
@admin_required
def admin_transactions():

    db = get_db()
    search = request.args.get("search", "").strip()

    transactions = db.execute("""
        SELECT t.*, a.holder_name, a.account_number
        FROM transactions t
        JOIN accounts a ON a.id = t.account_id
        WHERE (
            a.holder_name LIKE ?
            OR a.account_number LIKE ?
            OR t.reference LIKE ?
            OR t.transaction_type LIKE ?
        )
        ORDER BY t.id DESC
        LIMIT 500
    """, (f"%{search}%",) * 4).fetchall()

    return render_template(
        "admin_transactions.html",
        transactions=transactions,
        search=search
    )


# ==================================================
# ADMIN CUSTOMER TRANSACTION HISTORY
# ==================================================

@app.route("/admin/customer/<int:customer_id>/transactions")
@admin_required
def admin_customer_transactions(customer_id):

    db = get_db()

    customer = db.execute("""
        SELECT id, holder_name, account_number, status
        FROM accounts
        WHERE id = ?
    """, (customer_id,)).fetchone()

    if customer is None:
        flash("Customer not found.", "error")
        return redirect(url_for("admin_customers"))

    transactions = db.execute("""
        SELECT *
        FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
    """, (customer_id,)).fetchall()

    return render_template(
        "admin_customer_transactions.html",
        customer=customer,
        transactions=transactions
    )


# ==================================================
# ADMIN LOGOUT
# ==================================================

@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():

    session.clear()
    flash("Admin logged out successfully.", "success")
    return redirect(url_for("admin_login"))


# ==================================================
# CUSTOMER LOGIN
# ==================================================

@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    if session.get("account_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        account_number = request.form.get("account_number", "").strip()
        pin = request.form.get("pin", "").strip()

        db = get_db()

        account = db.execute(
            "SELECT * FROM accounts WHERE account_number = ?",
            (account_number,)
        ).fetchone()

        if account and check_password_hash(account["pin_hash"], pin):

            if account["status"] == "ACTIVE":
                session.clear()
                session["account_id"] = account["id"]
                session["account_number"] = account["account_number"]
                session["holder_name"] = account["holder_name"]
                return redirect(url_for("dashboard"))

            if account["status"] == "PENDING":
                flash("Your account is awaiting admin approval.", "error")
            elif account["status"] == "BLOCKED":
                flash("Your account is blocked. Contact the bank.", "error")
            elif account["status"] == "REJECTED":
                flash("Your account application was rejected.", "error")
            elif account["status"] == "CLOSED":
                flash("Your account has been closed. Contact the bank for assistance.", "error")
            else:
                flash("This account is not active.", "error")
        else:
            flash("Invalid account number or PIN.", "error")

    return render_template("login.html")


# ==================================================
# CUSTOMER REGISTRATION
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    if session.get("account_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("holder_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        address = request.form.get("address", "").strip()
        pin = request.form.get("pin", "").strip()
        confirm_pin = request.form.get("confirm_pin", "").strip()

        if len(name) < 2 or len(name) > 100:
            flash("Name must contain 2 to 100 characters.", "error")
            return redirect(url_for("register"))

        if not valid_phone(phone):
            flash("Enter a valid 10-digit mobile number.", "error")
            return redirect(url_for("register"))

        if not valid_email(email):
            flash("Enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(address) < 5 or len(address) > 300:
            flash("Enter a valid residential address.", "error")
            return redirect(url_for("register"))

        if not pin.isdigit() or len(pin) != 4:
            flash("PIN must contain exactly 4 digits.", "error")
            return redirect(url_for("register"))

        if pin != confirm_pin:
            flash("PINs do not match.", "error")
            return redirect(url_for("register"))

        db = get_db()

        try:
            db.execute("BEGIN IMMEDIATE")

            account_number = None

            for _ in range(20):
                candidate = str(secrets.randbelow(9000000000) + 1000000000)

                exists = db.execute(
                    "SELECT id FROM accounts WHERE account_number = ?",
                    (candidate,)
                ).fetchone()

                if exists is None:
                    account_number = candidate
                    break

            if account_number is None:
                db.rollback()
                flash("Unable to generate account number. Try again.", "error")
                return redirect(url_for("register"))

            db.execute("""
                INSERT INTO accounts
                (
                    account_number, holder_name, pin_hash,
                    balance_paise, status, phone, email, address
                )
                VALUES (?, ?, ?, 0, 'PENDING', ?, ?, ?)
            """, (
                account_number,
                name,
                generate_password_hash(pin),
                phone,
                email,
                address
            ))

            db.commit()

            return render_template(
                "register_success.html",
                account_number=account_number,
                holder_name=name
            )

        except sqlite3.Error:
            db.rollback()
            flash("Account creation failed. Please try again.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


# ==================================================
# CUSTOMER DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        flash("This account is not active.", "error")
        return redirect(url_for("login"))

    recent = db.execute("""
        SELECT * FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (account["id"],)).fetchall()

    return render_template(
        "dashboard.html",
        account=account,
        recent=recent
    )


# ==================================================
# DEPOSIT AND WITHDRAWAL
# ==================================================

@app.route("/transaction", methods=["GET", "POST"])
@login_required
def transaction():

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        flash("This account is not active.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        action = request.form.get("transaction_type", "")
        amount_text = request.form.get("amount", "").strip()

        try:
            amount = Decimal(amount_text)

            if (
                not amount.is_finite()
                or amount <= 0
                or amount > Decimal("1000000")
                or amount != amount.quantize(Decimal("0.01"))
            ):
                raise InvalidOperation

            amount_paise = int(amount * 100)

        except (InvalidOperation, ValueError, TypeError):
            flash("Enter a valid amount (maximum ₹10,00,000).", "error")
            return redirect(url_for("transaction"))

        if action not in ("deposit", "withdraw"):
            flash("Invalid transaction type.", "error")
            return redirect(url_for("transaction"))

        try:
            db.execute("BEGIN IMMEDIATE")

            account = db.execute(
                "SELECT * FROM accounts WHERE id = ?",
                (session["account_id"],)
            ).fetchone()

            if account is None or account["status"] != "ACTIVE":
                db.rollback()
                session.clear()
                flash("This account is not active.", "error")
                return redirect(url_for("login"))

            current = account["balance_paise"]

            if action == "withdraw" and amount_paise > current:
                db.rollback()
                flash("Insufficient balance.", "error")
                return redirect(url_for("transaction"))

            new_balance = (
                current + amount_paise
                if action == "deposit"
                else current - amount_paise
            )

            reference = secrets.token_hex(8)

            db.execute(
                "UPDATE accounts SET balance_paise = ? WHERE id = ?",
                (new_balance, account["id"])
            )

            db.execute("""
                INSERT INTO transactions
                (
                    account_id, transaction_type,
                    amount_paise, balance_after_paise, reference
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                account["id"],
                action.upper(),
                amount_paise,
                new_balance,
                reference
            ))

            db.commit()
            return redirect(url_for("receipt", reference=reference))

        except sqlite3.Error:
            db.rollback()
            flash("Transaction failed. Please try again.", "error")
            return redirect(url_for("transaction"))

    return render_template("transaction.html", account=account)


# ==================================================
# TRANSACTION RECEIPT
# ==================================================

@app.route("/receipt/<reference>")
@login_required
def receipt(reference):

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        flash("This account is not active.", "error")
        return redirect(url_for("login"))

    transaction = db.execute("""
        SELECT * FROM transactions
        WHERE reference = ? AND account_id = ?
    """, (reference, account["id"])).fetchone()

    if transaction is None:
        flash("Receipt not found.", "error")
        return redirect(url_for("history"))

    return render_template(
        "receipt.html",
        transaction=transaction,
        account=account
    )


# ==================================================
# CUSTOMER TRANSACTION HISTORY
# ==================================================

@app.route("/history")
@login_required
def history():

    db = get_db()

    account = db.execute(
        "SELECT status FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        return redirect(url_for("login"))

    transactions = db.execute("""
        SELECT * FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
        LIMIT 100
    """, (session["account_id"],)).fetchall()

    return render_template("history.html", transactions=transactions)


# ==================================================
# CHANGE PIN
# ==================================================

@app.route("/change-pin", methods=["GET", "POST"])
@login_required
def change_pin():

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":

        old_pin = request.form.get("old_pin", "").strip()
        new_pin = request.form.get("new_pin", "").strip()
        confirm_pin = request.form.get("confirm_pin", "").strip()

        if not check_password_hash(account["pin_hash"], old_pin):
            flash("Current PIN is incorrect.", "error")

        elif not new_pin.isdigit() or len(new_pin) != 4:
            flash("New PIN must be exactly 4 digits.", "error")

        elif new_pin != confirm_pin:
            flash("New PINs do not match.", "error")

        elif new_pin == old_pin:
            flash("New PIN must be different from the old PIN.", "error")

        else:
            db.execute(
                "UPDATE accounts SET pin_hash = ? WHERE id = ?",
                (generate_password_hash(new_pin), account["id"])
            )
            db.commit()
            flash("PIN changed successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template("change_pin.html")


# ==================================================
# CUSTOMER PROFILE
# ==================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    db = get_db()

    account = db.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (session["account_id"],)
    ).fetchone()

    if account is None or account["status"] != "ACTIVE":
        session.clear()
        flash("This account is not active.", "error")
        return redirect(url_for("login"))

    form_data = {
        "phone": account["phone"] or "",
        "email": account["email"] or "",
        "address": account["address"] or ""
    }

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        address = request.form.get("address", "").strip()

        form_data = {
            "phone": phone,
            "email": email,
            "address": address
        }

        if not valid_phone(phone):
            flash("Enter a valid 10-digit mobile number.", "error")

        elif not valid_email(email):
            flash("Enter a valid email address.", "error")

        elif len(address) < 5 or len(address) > 300:
            flash("Enter a valid address.", "error")

        else:
            db.execute("""
                UPDATE accounts
                SET phone = ?, email = ?, address = ?
                WHERE id = ?
            """, (phone, email, address, account["id"]))

            db.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))

    return render_template("profile.html", account=account, form_data=form_data)


# ==================================================
# CLOSE CUSTOMER ACCOUNT
# ==================================================

@app.route("/close-account", methods=["POST"])
@login_required
def close_account():

    db = get_db()

    try:
        db.execute("BEGIN IMMEDIATE")

        account = db.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (session["account_id"],)
        ).fetchone()

        if account is None or account["status"] != "ACTIVE":
            db.rollback()
            session.clear()
            flash("Account is not active.", "error")
            return redirect(url_for("login"))

        if account["balance_paise"] != 0:
            db.rollback()
            flash("Your balance must be ₹0 before closing the account.", "error")
            return redirect(url_for("dashboard"))

        db.execute(
            "UPDATE accounts SET status = 'CLOSED' WHERE id = ?",
            (account["id"],)
        )

        db.commit()
        session.clear()

        flash("Your account has been successfully closed.", "success")
        return redirect(url_for("login"))

    except sqlite3.Error:
        db.rollback()
        flash("Account closure failed. Please try again.", "error")
        return redirect(url_for("dashboard"))


# ==================================================
# CUSTOMER LOGOUT
# ==================================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ==================================================
# ERROR HANDLERS
# ==================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template(
        "error.html",
        error_code="ERROR 404",
        error_title="Page Not Found",
        error_icon="🔍",
        error_message="The page you are looking for does not exist or may have moved."
    ), 404


@app.errorhandler(429)
def ratelimit_error(error):
    return render_template(
        "error.html",
        error_code="ERROR 429",
        error_title="Too Many Requests",
        error_icon="⏳",
        error_message="You have made too many requests in a short period. Please wait a minute and try again."
    ), 429


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "error.html",
        error_code="ERROR 500",
        error_title="Server Error",
        error_icon="⚠️",
        error_message="An internal server error occurred. Our team has been notified."
    ), 500


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    try:
        from init_db import init_db
        init_db()
    except Exception as exc:
        print(f"Database initialization warning: {exc}")

    print("\n" + "=" * 55)
    print("                 NOVA BANK SERVER")
    print("=" * 55)

    print("\nChoose the page you want to open:\n")

    print("1. Customer Login")
    print("   http://127.0.0.1:5000/")

    print("\n2. Admin Login")
    print("   http://127.0.0.1:5000/admin/login")

    print("\n3. Admin Dashboard")
    print("   http://127.0.0.1:5000/admin/dashboard")

    print("\n" + "=" * 55)
    print("Server is starting...")
    print("=" * 55 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False)
