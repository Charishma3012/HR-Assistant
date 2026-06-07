import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[1] / "hrms.db"


def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30
    )
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            manager_id TEXT,
            email TEXT NOT NULL UNIQUE,
            hired_date TEXT NOT NULL,
            FOREIGN KEY(manager_id) REFERENCES employees(emp_id)
        );

        CREATE TABLE IF NOT EXISTS leave_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_date TEXT NOT NULL,
            request_id INTEGER NOT NULL,
            UNIQUE(emp_id, leave_date)
        );

        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            emp_id TEXT NOT NULL,
            item TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_code TEXT,
            emp_id TEXT NOT NULL,
            meeting_dt TEXT NOT NULL,
            start_dt TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL DEFAULT 60,
            topic TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Scheduled'
        );
        """
    )

    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]
    schema_changed = False
    if "meeting_code" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN meeting_code TEXT")
        schema_changed = True
    if "start_dt" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN start_dt TEXT")
        schema_changed = True
    if "duration_minutes" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN duration_minutes INTEGER DEFAULT 60")
        schema_changed = True
    if "status" not in columns:
        cursor.execute("ALTER TABLE meetings ADD COLUMN status TEXT DEFAULT 'Scheduled'")
        schema_changed = True
    if schema_changed:
        conn.commit()
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in cursor.fetchall()]

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_meeting_code ON meetings(meeting_code)")

    existing_meetings = cursor.execute(
        "SELECT meeting_id, meeting_dt, meeting_code, start_dt, duration_minutes, status FROM meetings"
    ).fetchall()
    for row in existing_meetings:
        updates = {}
        if not row["meeting_code"]:
            updates["meeting_code"] = f"M{int(row['meeting_id']):03d}"
        if not row["start_dt"]:
            updates["start_dt"] = row["meeting_dt"] or datetime.now().isoformat()
        if row["duration_minutes"] is None:
            updates["duration_minutes"] = 60
        if not row["status"]:
            updates["status"] = "Scheduled"
        if updates:
            set_clause = ", ".join(f"{key} = ?" for key in updates)
            values = list(updates.values()) + [row["meeting_id"]]
            cursor.execute(f"UPDATE meetings SET {set_clause} WHERE meeting_id = ?", values)

    conn.commit()
    conn.close()

