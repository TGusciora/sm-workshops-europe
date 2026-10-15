import sqlite3
from pathlib import Path

from app.database import MIGRATIONS, connect, migrate


def test_connect_creates_the_database_file_and_applies_all_migrations(
    tmp_path: Path,
) -> None:
    path = tmp_path / "nested" / "app.db"

    conn = connect(path)

    assert path.is_file()
    assert conn.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert {
        "positions",
        "ai_outputs",
        "decisions",
        "job_drafts",
        "interview_questions",
    } <= tables


def test_migrate_is_safe_to_run_twice(tmp_path: Path) -> None:
    conn = sqlite3.connect(tmp_path / "app.db")
    migrate(conn)
    migrate(conn)

    assert conn.execute("PRAGMA user_version").fetchone()[0] == len(MIGRATIONS)
