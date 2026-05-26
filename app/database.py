import sqlite3
from app.config import get_settings

DB_PATH = "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_task_by_title_safe(title: str):
    """Parameterized query — SQL injection fixed."""
    conn = get_connection()
    result = conn.execute(
        "SELECT * FROM tasks WHERE title = ?", (title,)
    ).fetchall()
    conn.close()
    return result


# Keep the unsafe version only to show the before/after to SonarQube
def get_task_by_title_unsafe(title: str):
    # VULNERABILITY: intentional SQL injection for SAST demo
    conn = get_connection()
    query = f"SELECT * FROM tasks WHERE title = '{title}'"
    result = conn.execute(query).fetchall()
    conn.close()
    return result
