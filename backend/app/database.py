"""SQLite connection and forward-only migrations (ADR-0003, ADR-0010)."""

import sqlite3
from pathlib import Path

# Each entry is one migration. The position in the list plus one is its version.
# Never edit a migration that has run; add a new one instead.
MIGRATIONS: list[str] = [
    """
    CREATE TABLE positions (
        id INTEGER PRIMARY KEY,
        slug TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    CREATE TABLE ai_outputs (
        id INTEGER PRIMARY KEY,
        kind TEXT NOT NULL,
        inputs TEXT NOT NULL,
        model_id TEXT NOT NULL,
        prompt_version TEXT NOT NULL,
        auth_method TEXT NOT NULL CHECK (auth_method IN ('subscription', 'api_key')),
        status TEXT NOT NULL CHECK (status IN ('ok', 'error')),
        output TEXT,
        error TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE decisions (
        id INTEGER PRIMARY KEY,
        ai_output_id INTEGER NOT NULL REFERENCES ai_outputs (id),
        subject_type TEXT NOT NULL CHECK (subject_type IN ('draft', 'question')),
        subject_id INTEGER NOT NULL,
        action TEXT NOT NULL CHECK (action IN ('approve', 'edit', 'reject')),
        final_text TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE chat_messages (
        id INTEGER PRIMARY KEY,
        position_id INTEGER NOT NULL REFERENCES positions (id),
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL,
        ai_output_id INTEGER REFERENCES ai_outputs (id),
        created_at TEXT NOT NULL
    );

    CREATE TABLE job_drafts (
        id INTEGER PRIMARY KEY,
        position_id INTEGER NOT NULL REFERENCES positions (id),
        ai_output_id INTEGER NOT NULL REFERENCES ai_outputs (id),
        text TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'accepted', 'rejected', 'superseded')),
        created_at TEXT NOT NULL
    );

    CREATE TABLE interview_questions (
        id INTEGER PRIMARY KEY,
        position_id INTEGER NOT NULL REFERENCES positions (id),
        stage TEXT NOT NULL,
        ai_output_id INTEGER NOT NULL REFERENCES ai_outputs (id),
        question TEXT NOT NULL,
        purpose TEXT NOT NULL,
        good_answer TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('proposed', 'approved', 'rejected')),
        created_at TEXT NOT NULL
    );

    CREATE TABLE confirmed_question_sets (
        position_id INTEGER NOT NULL REFERENCES positions (id),
        stage TEXT NOT NULL,
        confirmed_at TEXT NOT NULL,
        PRIMARY KEY (position_id, stage)
    );
    """,
    """
    CREATE TABLE interviews (
        id INTEGER PRIMARY KEY,
        position_id INTEGER NOT NULL REFERENCES positions (id),
        stage TEXT NOT NULL,
        starts_at TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL CHECK (duration_minutes BETWEEN 5 AND 480),
        interviewer TEXT NOT NULL,
        location TEXT NOT NULL,
        candidate_ref TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('planned', 'cancelled')),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX interviews_by_position ON interviews (position_id, starts_at);
    """,
]


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for version, script in enumerate(MIGRATIONS, start=1):
        if version <= current:
            continue
        with conn:
            conn.executescript(
                "BEGIN;" + script + f"PRAGMA user_version = {version};COMMIT;"
            )
