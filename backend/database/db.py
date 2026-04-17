import os
import sqlite3
from datetime import datetime, timedelta
import hashlib
import secrets
import re

from email_service import send_verification_email

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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number INTEGER UNIQUE,
            card_holder_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_verified INTEGER DEFAULT 0,
            verification_code TEXT,
            verification_expires_at TEXT
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
        (account_number, int(t["amount"]) if t["amount"] is not None else 0, t["location"], now)
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


# User Management Functions
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password, password_hash):
    """Verify password against hash"""
    try:
        salt, hashed = password_hash.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hashed
    except:
        return False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_verification_code():
    """Generate 6-digit verification code"""
    return str(secrets.randbelow(900000) + 100000)

def create_user(account_number, card_holder_name, email):
    """Create new user with email verification"""
    email = email.strip().lower()
    
    if not validate_email(email):
        return {"success": False, "message": "Invalid email format"}

    # Check if email already exists
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Email already registered"}

    # Check if account number already exists
    cursor.execute("SELECT id FROM users WHERE account_number = ?", (account_number,))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "message": "Account number already registered"}

    # Generate verification code
    verification_code = generate_verification_code()
    verification_expires = datetime.now() + timedelta(minutes=10)

    try:
        cursor.execute("""
            INSERT INTO users (account_number, card_holder_name, email, password_hash, verification_code, verification_expires_at)
            VALUES (?, ?, ?, '', ?, ?)
        """, (account_number, card_holder_name, email, verification_code, verification_expires.isoformat()))

        # Also create account entry
        cursor.execute("""
            INSERT INTO accounts (account_number, status, blocked_until)
            VALUES (?, 'ACTIVE', NULL)
        """, (account_number,))

        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # Send verification email
        email_result = send_verification_email(email, verification_code)

        if not email_result.get("success", False):
            return {"success": False, "message": email_result.get("message", "Unable to send verification email.")}

        return {
            "success": True,
            "message": "Verification code sent to your email",
            "user_id": user_id
        }
    except Exception as e:
        conn.close()
        return {"success": False, "message": f"Registration failed: {str(e)}"}

def verify_email_code(user_id, verification_code):
    """Verify email code and mark user as verified"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT verification_code, verification_expires_at FROM users
        WHERE id = ? AND is_verified = 0
    """, (user_id,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "User not found or already verified"}

    stored_code, expires_at = row
    expires_time = datetime.fromisoformat(expires_at)

    if datetime.now() > expires_time:
        conn.close()
        return {"success": False, "message": "Verification code expired"}

    if verification_code != stored_code:
        conn.close()
        return {"success": False, "message": "Invalid verification code"}

    # Mark as verified and clear verification code
    cursor.execute("""
        UPDATE users SET is_verified = 1, verification_code = NULL, verification_expires_at = NULL
        WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Email verified successfully"}

def resend_verification_code(user_id):
    """Resend verification code to an existing unverified user"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE id = ? AND is_verified = 0", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "User not found or already verified"}

    email = row[0]
    verification_code = generate_verification_code()
    verification_expires = datetime.now() + timedelta(minutes=10)

    cursor.execute(
        "UPDATE users SET verification_code = ?, verification_expires_at = ? WHERE id = ?",
        (verification_code, verification_expires.isoformat(), user_id),
    )
    conn.commit()
    conn.close()

    email_result = send_verification_email(email, verification_code)

    if not email_result.get("success", False):
        return {"success": False, "message": email_result.get("message", "Unable to send verification email.")}

    return {"success": True, "message": "Verification code resent to your email"}

COMMON_PASSWORDS = {
    '000000','111111','222222','333333','444444','555555','666666','777777','888888','999999',
    '123456','654321','123123','112233','121212','000123','123000','123321','111222','222111'
}


def is_common_password(password):
    if password in COMMON_PASSWORDS:
        return True
    if password == password[0] * 6:
        return True
    ascending = '0123456789'
    descending = '9876543210'
    if password in ascending or password in descending:
        return True
    return False


def set_password(user_id, password):
    """Set password for verified user"""
    if len(password) != 6 or not password.isdigit():
        return {"success": False, "message": "Password must be exactly 6 digits."}

    if is_common_password(password):
        return {"success": False, "message": "Choose a stronger 6-digit password. Avoid easy codes like 123456, 111111, or repeated sequences."}

    if len(set(password)) <= 2:
        return {"success": False, "message": "Too many repeated digits. Use at least 3 or more different digits."}

    strength = "Weak"
    if len(set(password)) >= 5:
        strength = "Very Strong"
    elif len(set(password)) >= 4:
        strength = "Strong"
    elif len(set(password)) == 3:
        strength = "Moderate"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_verified FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row or row[0] != 1:
        conn.close()
        return {"success": False, "message": "User not verified"}

    password_hash = hash_password(password)
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password set successfully",
        "strength": strength
    }

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    email = email.strip().lower()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.account_number, u.card_holder_name, u.password_hash, a.status, a.blocked_until
        FROM users u
        JOIN accounts a ON u.account_number = a.account_number
        WHERE u.email = ? AND u.is_verified = 1
    """, (email,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "message": "Invalid credentials"}

    user_id, account_number, card_holder_name, password_hash, status, blocked_until = row

    if not verify_password(password, password_hash):
        return {"success": False, "message": "Invalid credentials"}

    # Check if account is blocked
    if status == 'BLOCKED':
        if blocked_until:
            blocked_time = datetime.fromisoformat(blocked_until)
            if datetime.now() < blocked_time:
                return {"success": False, "message": f"Account blocked until {blocked_until}"}
            else:
                # Unblock account
                update_account_status(account_number, 'ACTIVE', None)

    return {
        "success": True,
        "user": {
            "id": user_id,
            "account_number": account_number,
            "card_holder_name": card_holder_name,
            "email": email
        }
    }

def get_user_by_email(email):
    """Get user by email"""
    email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row