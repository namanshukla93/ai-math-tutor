# auth_db.py — Authentication, SQLite Database & Chat History for AI Math Tutor
#
# Manages user accounts, bcrypt password hashing, persistent chat history, and account details.

import os
import sqlite3
import bcrypt

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_db_connection():
    """Returns a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes users, chats, and messages tables in SQLite."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users table
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

        # 2. Persistent Chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 3. Persistent Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
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
    """Registers a new student with bcrypt hashed password."""
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
    """Authenticates a user by email and bcrypt password."""
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
                SELECT id, name, email, password_hash, class_level, created_at
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
                "created_at": user_row["created_at"],
            }
            return True, user_data, "Login successful!"
    except Exception as e:
        return False, None, f"Login error: {str(e)[:80]}"


# ─────────────────────────────────────────────
# ACCOUNT DETAILS & PROFILE MANAGEMENT
# ─────────────────────────────────────────────

def get_user_details(user_id: int) -> dict | None:
    """Fetches user details and stats by user_id."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, email, class_level, created_at
                FROM users
                WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT COUNT(*) FROM chats WHERE user_id = ?", (user_id,))
            chat_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ? AND role = 'user'", (user_id,))
            questions_asked = cursor.fetchone()[0]

            return {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "class_level": row["class_level"],
                "created_at": row["created_at"],
                "total_chats": chat_count,
                "total_questions": questions_asked,
            }
    except Exception:
        return None


def update_user_profile(user_id: int, name: str, class_level: int) -> tuple[bool, str]:
    """Updates user display name and school class level."""
    name = (name or "").strip()
    if not name:
        return False, "Name cannot be empty."

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET name = ?, class_level = ?
                WHERE id = ?
            """, (name, class_level, user_id))
            conn.commit()
            return True, "Profile details updated successfully!"
    except Exception as e:
        return False, f"Failed to update profile: {str(e)[:80]}"


def change_user_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    """Verifies old password and updates with new bcrypt hash."""
    if len(new_password or "") < 6:
        return False, "New password must be at least 6 characters long."

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return False, "User account not found."

            if not verify_password(old_password, row["password_hash"]):
                return False, "Current password is incorrect."

            new_hash = hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            return True, "Password changed successfully!"
    except Exception as e:
        return False, f"Failed to change password: {str(e)[:80]}"


# ─────────────────────────────────────────────
# PERSISTENT CHAT HISTORY (Like ChatGPT / Claude)
# ─────────────────────────────────────────────

def get_user_chats(user_id: int) -> list[dict]:
    """Loads all chat sessions for a specific user, sorted newest first."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, created_at, updated_at
                FROM chats
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            return [
                {
                    "id": r["id"],
                    "title": r["title"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                }
                for r in rows
            ]
    except Exception:
        return []


def create_db_chat(user_id: int, chat_id: str, title: str = "New Chat"):
    """Saves a new chat record in the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO chats (id, user_id, title)
                VALUES (?, ?, ?)
            """, (chat_id, user_id, title))
            conn.commit()
    except Exception:
        pass


def update_db_chat_title(chat_id: str, user_id: int, title: str):
    """Updates the title of a chat and touches updated_at."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE chats
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (title, chat_id, user_id))
            conn.commit()
    except Exception:
        pass


def delete_db_chat(chat_id: str, user_id: int):
    """Deletes a chat and its messages permanently."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
            cursor.execute("DELETE FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id))
            conn.commit()
    except Exception:
        pass


def save_db_message(chat_id: str, user_id: int, role: str, content: str, author: str = ""):
    """Appends a message to persistent storage."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (chat_id, user_id, role, content, author)
                VALUES (?, ?, ?, ?, ?)
            """, (chat_id, user_id, role, content, author))
            cursor.execute("""
                UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?
            """, (chat_id, user_id))
            conn.commit()
    except Exception:
        pass


def get_db_messages(chat_id: str, user_id: int) -> list[dict]:
    """Fetches all messages for a specific chat."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, author, created_at
                FROM messages
                WHERE chat_id = ? AND user_id = ?
                ORDER BY id ASC
            """, (chat_id, user_id))
            rows = cursor.fetchall()
            return [
                {
                    "role": r["role"],
                    "content": r["content"],
                    "author": r["author"] or ("user" if r["role"] == "user" else "AI Tutor"),
                    "created_at": r["created_at"],
                }
                for r in rows
            ]
    except Exception:
        return []
