import sqlite3
import threading
from pathlib import Path

import pytest
from app.database import MIGRATIONS, connect, migrate
from app.repository import Repository


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


def test_a_write_from_another_thread_does_not_join_an_open_transaction(
    tmp_path: Path,
) -> None:
    repo = Repository(connect(tmp_path / "app.db"))
    other = threading.Thread(target=repo.create_position, args=("b", "B"))

    with pytest.raises(RuntimeError), repo._transaction():
        repo.conn.execute(
            "INSERT INTO positions (slug, title, created_at) VALUES ('a', 'A', '')"
        )
        other.start()
        other.join(timeout=0.2)
        raise RuntimeError("roll back")
    other.join()

    assert [p.slug for p in repo.list_positions()] == ["b"]
