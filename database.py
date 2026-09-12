import sqlite3
import os
import hashlib
import secrets
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning_archive.db")


def get_db_path():
    return DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== 数据库初始化 ====================

def init_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                name TEXT NOT NULL,
                category TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                course_id INTEGER NOT NULL,
                score REAL NOT NULL,
                total_score REAL NOT NULL DEFAULT 100,
                exam_type TEXT DEFAULT '作业',
                exam_date DATE NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                course_id INTEGER,
                platform TEXT DEFAULT '',
                problem_count INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                duration_minutes INTEGER DEFAULT 0,
                practice_date DATE NOT NULL,
                topic TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                course_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                note_date DATE NOT NULL,
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                course_id INTEGER,
                problem_description TEXT NOT NULL,
                your_answer TEXT DEFAULT '',
                correct_answer TEXT NOT NULL,
                reason TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                mistake_date DATE NOT NULL,
                review_count INTEGER DEFAULT 0,
                mastered INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)


# ==================== 用户认证 ====================

def _hash_password(password: str, salt: str = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}${h.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    salt, _ = stored.split("$", 1)
    return _hash_password(password, salt) == stored


def register_user(username: str, password: str) -> tuple:
    """返回 (success: bool, message: str, user_id: int|None)"""
    username = username.strip()
    if len(username) < 2:
        return False, "用户名至少 2 个字符", None
    if len(password) < 4:
        return False, "密码至少 4 个字符", None

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            return False, "用户名已被注册", None

        pw_hash = _hash_password(password)
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pw_hash),
        )
        return True, "注册成功", cursor.lastrowid


def login_user(username: str, password: str) -> tuple:
    """返回 (success: bool, message: str, user_id: int|None, username: str|None)"""
    username = username.strip()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return False, "用户名不存在", None, None
        if not _verify_password(password, row["password_hash"]):
            return False, "密码错误", None, None
        return True, "登录成功", row["id"], row["username"]


def get_user_count() -> int:
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


# ==================== courses ====================

def add_course(name, user_id, category=""):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO courses (user_id, name, category) VALUES (?, ?, ?)",
            (user_id, name.strip(), category.strip()),
        )


def get_all_courses(user_id):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM courses WHERE user_id = ? ORDER BY name", (user_id,)
        ).fetchall()]


def get_course_id(name, user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM courses WHERE name = ? AND user_id = ?",
            (name.strip(), user_id),
        ).fetchone()
        return row["id"] if row else None


# ==================== grades ====================

def add_grade(user_id, course_name, score, total_score, exam_type, exam_date, notes=""):
    add_course(course_name, user_id)
    course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO grades (user_id, course_id, score, total_score, exam_type, exam_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, course_id, score, total_score, exam_type, exam_date, notes),
        )


def get_grades(user_id, start_date=None, end_date=None, course_id=None):
    with get_connection() as conn:
        query = "SELECT g.*, c.name as course_name FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND g.exam_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND g.exam_date <= ?"
            params.append(end_date)
        if course_id:
            query += " AND g.course_id = ?"
            params.append(course_id)
        query += " ORDER BY g.exam_date DESC"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_grade_by_id(grade_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT g.*, c.name as course_name FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.id = ?",
            (grade_id,),
        ).fetchone()
        return dict(row) if row else None


def update_grade(grade_id, course_name, score, total_score, exam_type, exam_date, user_id, notes=""):
    add_course(course_name, user_id)
    course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "UPDATE grades SET course_id=?, score=?, total_score=?, exam_type=?, exam_date=?, notes=? WHERE id=?",
            (course_id, score, total_score, exam_type, exam_date, notes, grade_id),
        )


def delete_grade(grade_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM grades WHERE id=?", (grade_id,))


# ==================== practice ====================

def add_practice(user_id, course_name, platform, problem_count, correct_count, duration_minutes, practice_date, topic="", notes=""):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO practice_records (user_id, course_id, platform, problem_count, correct_count, duration_minutes, practice_date, topic, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, course_id, platform, problem_count, correct_count, duration_minutes, practice_date, topic, notes),
        )


def get_practice_records(user_id, start_date=None, end_date=None, course_id=None):
    with get_connection() as conn:
        query = "SELECT p.*, c.name as course_name FROM practice_records p LEFT JOIN courses c ON p.course_id = c.id WHERE p.user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND p.practice_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND p.practice_date <= ?"
            params.append(end_date)
        if course_id:
            query += " AND p.course_id = ?"
            params.append(course_id)
        query += " ORDER BY p.practice_date DESC"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_practice_by_id(practice_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT p.*, c.name as course_name FROM practice_records p LEFT JOIN courses c ON p.course_id = c.id WHERE p.id = ?",
            (practice_id,),
        ).fetchone()
        return dict(row) if row else None


def update_practice(record_id, course_name, platform, problem_count, correct_count, duration_minutes, practice_date, user_id, topic="", notes=""):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "UPDATE practice_records SET course_id=?, platform=?, problem_count=?, correct_count=?, duration_minutes=?, practice_date=?, topic=?, notes=? WHERE id=?",
            (course_id, platform, problem_count, correct_count, duration_minutes, practice_date, topic, notes, record_id),
        )


def delete_practice(record_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM practice_records WHERE id=?", (record_id,))


# ==================== notes ====================

def add_note(user_id, course_name, title, content, note_date, tags=""):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO notes (user_id, course_id, title, content, note_date, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, course_id, title, content, note_date, tags),
        )


def get_notes(user_id, start_date=None, end_date=None, course_id=None, keyword=None):
    with get_connection() as conn:
        query = "SELECT n.*, c.name as course_name FROM notes n LEFT JOIN courses c ON n.course_id = c.id WHERE n.user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND n.note_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND n.note_date <= ?"
            params.append(end_date)
        if course_id:
            query += " AND n.course_id = ?"
            params.append(course_id)
        if keyword:
            query += " AND (n.title LIKE ? OR n.content LIKE ? OR n.tags LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        query += " ORDER BY n.note_date DESC"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_note_by_id(note_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT n.*, c.name as course_name FROM notes n LEFT JOIN courses c ON n.course_id = c.id WHERE n.id = ?",
            (note_id,),
        ).fetchone()
        return dict(row) if row else None


def update_note(note_id, course_name, title, content, note_date, user_id, tags=""):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "UPDATE notes SET course_id=?, title=?, content=?, note_date=?, tags=? WHERE id=?",
            (course_id, title, content, note_date, tags, note_id),
        )


def delete_note(note_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM notes WHERE id=?", (note_id,))


# ==================== mistakes ====================

def add_mistake(user_id, course_name, problem_description, your_answer, correct_answer, reason, tags, mistake_date, mastered=0):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO mistakes (user_id, course_id, problem_description, your_answer, correct_answer, reason, tags, mistake_date, mastered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, course_id, problem_description, your_answer, correct_answer, reason, tags, mistake_date, mastered),
        )


def get_mistakes(user_id, start_date=None, end_date=None, course_id=None, mastered=None):
    with get_connection() as conn:
        query = "SELECT m.*, c.name as course_name FROM mistakes m LEFT JOIN courses c ON m.course_id = c.id WHERE m.user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND m.mistake_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND m.mistake_date <= ?"
            params.append(end_date)
        if course_id:
            query += " AND m.course_id = ?"
            params.append(course_id)
        if mastered is not None:
            query += " AND m.mastered = ?"
            params.append(mastered)
        query += " ORDER BY m.mistake_date DESC"
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_mistake_by_id(mistake_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT m.*, c.name as course_name FROM mistakes m LEFT JOIN courses c ON m.course_id = c.id WHERE m.id = ?",
            (mistake_id,),
        ).fetchone()
        return dict(row) if row else None


def update_mistake(mistake_id, course_name, problem_description, your_answer, correct_answer, reason, tags, mistake_date, user_id):
    course_id = None
    if course_name:
        add_course(course_name, user_id)
        course_id = get_course_id(course_name, user_id)
    with get_connection() as conn:
        conn.execute(
            "UPDATE mistakes SET course_id=?, problem_description=?, your_answer=?, correct_answer=?, reason=?, tags=?, mistake_date=? WHERE id=?",
            (course_id, problem_description, your_answer, correct_answer, reason, tags, mistake_date, mistake_id),
        )


def delete_mistake(mistake_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM mistakes WHERE id=?", (mistake_id,))


def mark_mistake_mastered(mistake_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE mistakes SET mastered = 1, review_count = review_count + 1 WHERE id = ?",
            (mistake_id,),
        )


# ==================== stats ====================

def get_summary_stats(user_id, grade_ids=None):
    with get_connection() as conn:
        stats = {}
        stats["total_courses"] = conn.execute(
            "SELECT COUNT(*) FROM courses WHERE user_id = ?", (user_id,)
        ).fetchone()[0]

        if grade_ids:
            placeholders = ','.join(['?' for _ in grade_ids])
            stats["total_grades"] = conn.execute(
                f"SELECT COUNT(*) FROM grades WHERE user_id = ? AND id IN ({placeholders})",
                [user_id] + grade_ids,
            ).fetchone()[0]
            # Get date range from selected grades
            row = conn.execute(
                f"SELECT MIN(exam_date) as min_d, MAX(exam_date) as max_d FROM grades WHERE user_id = ? AND id IN ({placeholders})",
                [user_id] + grade_ids,
            ).fetchone()
            min_d, max_d = row["min_d"], row["max_d"]
            if min_d and max_d:
                stats["total_practice"] = conn.execute(
                    "SELECT COUNT(*) FROM practice_records WHERE user_id = ? AND practice_date BETWEEN ? AND ?",
                    (user_id, min_d, max_d),
                ).fetchone()[0]
                stats["total_notes"] = conn.execute(
                    "SELECT COUNT(*) FROM notes WHERE user_id = ? AND note_date BETWEEN ? AND ?",
                    (user_id, min_d, max_d),
                ).fetchone()[0]
                stats["total_mistakes"] = conn.execute(
                    "SELECT COUNT(*) FROM mistakes WHERE user_id = ? AND mistake_date BETWEEN ? AND ?",
                    (user_id, min_d, max_d),
                ).fetchone()[0]
                stats["unmastered_mistakes"] = conn.execute(
                    "SELECT COUNT(*) FROM mistakes WHERE mastered = 0 AND user_id = ? AND mistake_date BETWEEN ? AND ?",
                    (user_id, min_d, max_d),
                ).fetchone()[0]
                row2 = conn.execute(
                    "SELECT COALESCE(SUM(problem_count),0) as total, COALESCE(SUM(correct_count),0) as correct FROM practice_records WHERE user_id = ? AND practice_date BETWEEN ? AND ?",
                    (user_id, min_d, max_d),
                ).fetchone()
            else:
                stats["total_practice"] = 0
                stats["total_notes"] = 0
                stats["total_mistakes"] = 0
                stats["unmastered_mistakes"] = 0
                row2 = {"total": 0, "correct": 0}
            stats["total_problems"] = row2["total"]
            stats["total_correct"] = row2["correct"]
        else:
            stats["total_grades"] = conn.execute(
                "SELECT COUNT(*) FROM grades WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            stats["total_practice"] = conn.execute(
                "SELECT COUNT(*) FROM practice_records WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            stats["total_notes"] = conn.execute(
                "SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            stats["total_mistakes"] = conn.execute(
                "SELECT COUNT(*) FROM mistakes WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            stats["unmastered_mistakes"] = conn.execute(
                "SELECT COUNT(*) FROM mistakes WHERE mastered = 0 AND user_id = ?", (user_id,)
            ).fetchone()[0]
            row2 = conn.execute(
                "SELECT COALESCE(SUM(problem_count),0) as total, COALESCE(SUM(correct_count),0) as correct FROM practice_records WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            stats["total_problems"] = row2["total"]
            stats["total_correct"] = row2["correct"]
        return stats


def get_all_data_for_ai(user_id, grade_ids=None):
    with get_connection() as conn:
        data = {}

        if grade_ids:
            placeholders = ','.join(['?' for _ in grade_ids])
            grades = conn.execute(
                f"SELECT g.*, c.name as course_name FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.user_id = ? AND g.id IN ({placeholders}) ORDER BY g.exam_date DESC",
                [user_id] + grade_ids,
            ).fetchall()
            data["grades"] = [dict(r) for r in grades]
            # Get date range from selected grades
            row = conn.execute(
                f"SELECT MIN(exam_date) as min_d, MAX(exam_date) as max_d FROM grades WHERE user_id = ? AND id IN ({placeholders})",
                [user_id] + grade_ids,
            ).fetchone()
            min_d, max_d = row["min_d"], row["max_d"]
            if min_d and max_d:
                data["practice"] = [dict(r) for r in conn.execute(
                    "SELECT p.*, c.name as course_name FROM practice_records p LEFT JOIN courses c ON p.course_id = c.id WHERE p.user_id = ? AND p.practice_date BETWEEN ? AND ? ORDER BY p.practice_date DESC",
                    (user_id, min_d, max_d),
                ).fetchall()]
                data["notes"] = [dict(r) for r in conn.execute(
                    "SELECT n.*, c.name as course_name FROM notes n LEFT JOIN courses c ON n.course_id = c.id WHERE n.user_id = ? AND n.note_date BETWEEN ? AND ? ORDER BY n.note_date DESC",
                    (user_id, min_d, max_d),
                ).fetchall()]
                data["mistakes"] = [dict(r) for r in conn.execute(
                    "SELECT m.*, c.name as course_name FROM mistakes m LEFT JOIN courses c ON m.course_id = c.id WHERE m.user_id = ? AND m.mistake_date BETWEEN ? AND ? ORDER BY m.mistake_date DESC",
                    (user_id, min_d, max_d),
                ).fetchall()]
            else:
                data["practice"] = []
                data["notes"] = []
                data["mistakes"] = []
        else:
            grades = conn.execute(
                "SELECT g.*, c.name as course_name FROM grades g JOIN courses c ON g.course_id = c.id WHERE g.user_id = ? ORDER BY g.exam_date DESC",
                (user_id,),
            ).fetchall()
            data["grades"] = [dict(r) for r in grades]

            practice = conn.execute(
                "SELECT p.*, c.name as course_name FROM practice_records p LEFT JOIN courses c ON p.course_id = c.id WHERE p.user_id = ? ORDER BY p.practice_date DESC",
                (user_id,),
            ).fetchall()
            data["practice"] = [dict(r) for r in practice]

            notes = conn.execute(
                "SELECT n.*, c.name as course_name FROM notes n LEFT JOIN courses c ON n.course_id = c.id WHERE n.user_id = ? ORDER BY n.note_date DESC",
                (user_id,),
            ).fetchall()
            data["notes"] = [dict(r) for r in notes]

            mistakes = conn.execute(
                "SELECT m.*, c.name as course_name FROM mistakes m LEFT JOIN courses c ON m.course_id = c.id WHERE m.user_id = ? ORDER BY m.mistake_date DESC",
                (user_id,),
            ).fetchall()
            data["mistakes"] = [dict(r) for r in mistakes]

        data["summary"] = get_summary_stats(user_id, grade_ids=grade_ids)
        return data
