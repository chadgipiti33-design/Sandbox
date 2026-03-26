import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "tracker.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                date TEXT UNIQUE,
                looks_score INTEGER,
                retard_score INTEGER,
                notes TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS routines (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                category TEXT,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS routine_logs (
                id INTEGER PRIMARY KEY,
                log_id INTEGER,
                routine_id INTEGER,
                done INTEGER DEFAULT 0,
                FOREIGN KEY (log_id) REFERENCES logs(id),
                FOREIGN KEY (routine_id) REFERENCES routines(id)
            );
        """)


def add_routine(name: str, category: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO routines (name, category) VALUES (?, ?)",
                (name, category)
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_routines(active_only: bool = True) -> list:
    with get_conn() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM routines WHERE active=1 ORDER BY category, name"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM routines ORDER BY category, name"
            ).fetchall()
    return [dict(r) for r in rows]


def save_log(date: str, looks_score: int, retard_score: int,
             notes: str, routine_done_ids: list) -> int:
    with get_conn() as conn:
        # Upsert log entry
        existing = conn.execute(
            "SELECT id FROM logs WHERE date=?", (date,)
        ).fetchone()

        if existing:
            log_id = existing["id"]
            conn.execute(
                """UPDATE logs SET looks_score=?, retard_score=?, notes=?, created_at=?
                   WHERE id=?""",
                (looks_score, retard_score, notes,
                 datetime.now().isoformat(), log_id)
            )
            conn.execute("DELETE FROM routine_logs WHERE log_id=?", (log_id,))
        else:
            cur = conn.execute(
                """INSERT INTO logs (date, looks_score, retard_score, notes, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (date, looks_score, retard_score, notes,
                 datetime.now().isoformat())
            )
            log_id = cur.lastrowid

        # Save routine completions
        routines = get_routines()
        for r in routines:
            done = 1 if r["id"] in routine_done_ids else 0
            conn.execute(
                "INSERT INTO routine_logs (log_id, routine_id, done) VALUES (?, ?, ?)",
                (log_id, r["id"], done)
            )

    return log_id


def get_logs(days: int = 30) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM logs
               ORDER BY date DESC
               LIMIT ?""",
            (days,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_log_routines(log_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.name, r.category, rl.done
               FROM routine_logs rl
               JOIN routines r ON r.id = rl.routine_id
               WHERE rl.log_id=?
               ORDER BY r.category, r.name""",
            (log_id,)
        ).fetchall()
    return [dict(r) for r in rows]
