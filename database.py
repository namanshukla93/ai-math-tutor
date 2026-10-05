"""
database.py - SQLite Database Management for ApexSolve AI Math & Reasoning Master
Handles student accounts, authentication security (bcrypt), solved questions history,
bookmarks, and practice activity analytics.
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "apexsolve.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def init_db():
    """Initializes tables and seeds default demo student account if missing."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                target_exam TEXT DEFAULT 'General / College',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Solved questions history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,           -- 'Mathematics' or 'Reasoning'
                topic TEXT NOT NULL,              -- e.g. 'Algebra', 'Number Series'
                question_text TEXT NOT NULL,
                solution_markdown TEXT NOT NULL,
                practice_json TEXT DEFAULT '[]',  -- List of generated practice problems
                is_bookmarked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # Practice attempt logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER,
                problem_text TEXT NOT NULL,
                student_answer TEXT,
                correct_answer TEXT,
                is_correct INTEGER DEFAULT 0,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # Student personal notes/scratchpad per question or general
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        conn.commit()

        # Seed default demo account: Naman Shukla (namanshukla9889@gmail.com)
        demo_email = "namanshukla9889@gmail.com"
        cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
        if not cursor.fetchone():
            demo_pass = hash_password("naman123")
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, target_exam)
                VALUES (?, ?, ?, ?)
            """, ("Naman Shukla", demo_email, demo_pass, "JEE / Competitive & College"))
            conn.commit()


# ==================== User Authentication Functions ====================

def register_user(name: str, email: str, password: str, target_exam: str = "General") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Registers a new student account."""
    name = name.strip()
    email = email.strip().lower()

    if not name or len(name) < 2:
        return False, "Please enter a valid student name (at least 2 characters).", None

    if not email or "@" not in email or "." not in email:
        return False, "Please provide a valid email address.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    pw_hash = hash_password(password)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, target_exam)
                VALUES (?, ?, ?, ?)
            """, (name, email, pw_hash, target_exam))
            user_id = cursor.lastrowid
            conn.commit()

            return True, "Account registered successfully!", {
                "id": user_id,
                "name": name,
                "email": email,
                "target_exam": target_exam
            }
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists. Please log in.", None
    except Exception as e:
        return False, f"Registration error: {str(e)}", None


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Authenticates student credentials."""
    email = email.strip().lower()
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, password_hash, target_exam FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

            if not row:
                return False, "No account found with this email address.", None

            if not check_password(password, row["password_hash"]):
                return False, "Incorrect password. Please try again.", None

            return True, "Login successful!", {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "target_exam": row["target_exam"]
            }
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None


def update_user_profile(user_id: int, name: str, target_exam: str) -> Tuple[bool, str]:
    """Updates user profile details."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = ?, target_exam = ? WHERE id = ?", (name.strip(), target_exam.strip(), user_id))
            conn.commit()
            return True, "Profile updated successfully!"
    except Exception as e:
        return False, f"Update failed: {str(e)}"


# ==================== Questions History & Practice Functions ====================

def save_solved_question(user_id: int, category: str, topic: str, question_text: str,
                        solution_markdown: str, practice_problems: List[Dict[str, Any]]) -> int:
    """Saves a solved question with its solution and generated practice problems."""
    with get_connection() as conn:
        cursor = conn.cursor()
        practice_json = json.dumps(practice_problems, ensure_ascii=False)
        cursor.execute("""
            INSERT INTO questions (user_id, category, topic, question_text, solution_markdown, practice_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, category, topic, question_text.strip(), solution_markdown.strip(), practice_json))
        conn.commit()
        return cursor.lastrowid


def get_user_history(user_id: int, category_filter: Optional[str] = None,
                     search_query: Optional[str] = None, bookmarked_only: bool = False) -> List[Dict[str, Any]]:
    """Retrieves saved question history for the student with optional filters."""
    query = "SELECT * FROM questions WHERE user_id = ?"
    params = [user_id]

    if category_filter and category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)

    if bookmarked_only:
        query += " AND is_bookmarked = 1"

    if search_query and search_query.strip():
        query += " AND (question_text LIKE ? OR topic LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            try:
                item["practice_problems"] = json.loads(item.get("practice_json", "[]"))
            except Exception:
                item["practice_problems"] = []
            result.append(item)
        return result


def toggle_bookmark(question_id: int, user_id: int) -> bool:
    """Toggles bookmark status for a question."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_bookmarked FROM questions WHERE id = ? AND user_id = ?", (question_id, user_id))
        row = cursor.fetchone()
        if row:
            new_status = 0 if row["is_bookmarked"] == 1 else 1
            cursor.execute("UPDATE questions SET is_bookmarked = ? WHERE id = ? AND user_id = ?", (new_status, question_id, user_id))
            conn.commit()
            return bool(new_status)
    return False


def delete_question(question_id: int, user_id: int) -> bool:
    """Deletes a saved question from history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ? AND user_id = ?", (question_id, user_id))
        conn.commit()
        return cursor.rowcount > 0


def log_practice_attempt(user_id: int, question_id: Optional[int], problem_text: str,
                         student_answer: str, correct_answer: str, is_correct: bool):
    """Records student's practice exercise attempt."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO practice_logs (user_id, question_id, problem_text, student_answer, correct_answer, is_correct)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, question_id, problem_text, student_answer, correct_answer, 1 if is_correct else 0))
        conn.commit()


def get_student_dashboard_stats(user_id: int) -> Dict[str, Any]:
    """Calculates comprehensive dashboard analytics for the student."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Questions count
        cursor.execute("SELECT COUNT(*) as total FROM questions WHERE user_id = ?", (user_id,))
        total_questions = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as math_total FROM questions WHERE user_id = ? AND category = 'Mathematics'", (user_id,))
        math_total = cursor.fetchone()["math_total"]

        cursor.execute("SELECT COUNT(*) as reasoning_total FROM questions WHERE user_id = ? AND category = 'Reasoning'", (user_id,))
        reasoning_total = cursor.fetchone()["reasoning_total"]

        cursor.execute("SELECT COUNT(*) as b_total FROM questions WHERE user_id = ? AND is_bookmarked = 1", (user_id,))
        bookmarked_total = cursor.fetchone()["b_total"]

        # Practice stats
        cursor.execute("SELECT COUNT(*) as attempts, SUM(is_correct) as correct FROM practice_logs WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        attempts = p_row["attempts"] or 0
        correct = p_row["correct"] or 0
        accuracy = round((correct / attempts * 100), 1) if attempts > 0 else 0.0

        return {
            "total_questions": total_questions,
            "math_questions": math_total,
            "reasoning_questions": reasoning_total,
            "bookmarked_questions": bookmarked_total,
            "practice_attempts": attempts,
            "practice_correct": correct,
            "practice_accuracy": accuracy
        }


# Auto-initialize DB on module import
init_db()
