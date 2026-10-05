# auth_db.py — Authentication and SQLite Database for AI Math Tutor
#
# Manages user accounts, bcrypt password hashing, and authentication state.

import os
import sqlite3
import re
import bcrypt

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_db_connection():
    """Returns a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the users table and seeds a demo account if fresh."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                class_level INTEGER DEFAULT 8,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Seed creator demo account if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            demo_salt = bcrypt.gensalt()
            demo_hash = bcrypt.hashpw("naman123".encode("utf-8"), demo_salt).decode("utf-8")
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, class_level)
                VALUES (?, ?, ?, ?)
            """, ("Naman Shukla", "ramanshukla2005@gmail.com", demo_hash, 10))
            conn.commit()


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Safely verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def register_user(name: str, email: str, password: str, class_level: int = 8) -> tuple[bool, str]:
    """
    Registers a new student / user with bcrypt hashed password.
    Returns (success: bool, message: str).
    """
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = (password or "").strip()

    if not name:
        return False, "Please enter your full name."
    if not email or "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    pwd_hash = hash_password(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, class_level)
                VALUES (?, ?, ?, ?)
            """, (name, email, pwd_hash, class_level))
            conn.commit()
            return True, "Account created successfully! You can now log in."
    except sqlite3.IntegrityError:
        return False, "This email is already registered. Please log in."
    except Exception as e:
        return False, f"Registration failed: {str(e)[:80]}"


def authenticate_user(email: str, password: str) -> tuple[bool, dict | None, str]:
    """
    Authenticates a user by email and bcrypt password.
    Returns (success: bool, user_dict: dict | None, message: str).
    """
    email = (email or "").strip().lower()
    password = (password or "").strip()

    if not email:
        return False, None, "Please enter your email address."
    if not password:
        return False, None, "Please enter your password."

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, password_hash, class_level
                FROM users
                WHERE email = ?
            """, (email,))
            user_row = cursor.fetchone()

            if not user_row:
                return False, None, "No account found with this email address. Please sign up."

            stored_hash = user_row["password_hash"]
            if not verify_password(password, stored_hash):
                return False, None, "Incorrect password. Please try again."

            user_data = {
                "id": user_row["id"],
                "name": user_row["name"],
                "email": user_row["email"],
                "class_level": user_row["class_level"],
            }
            return True, user_data, "Login successful!"
    except Exception as e:
        return False, None, f"Login error: {str(e)[:80]}"
