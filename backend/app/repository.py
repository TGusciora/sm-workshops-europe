"""All SQL lives here. Routes and services call these methods, never SQL directly."""

import json
import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Position:
    id: int
    slug: str
    title: str


@dataclass(frozen=True)
class AiOutput:
    id: int
    kind: str
    model_id: str
    prompt_version: str
    auth_method: str
    status: str
    output: str | None
    error: str | None


@dataclass(frozen=True)
class ChatMessage:
    id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: str


@dataclass(frozen=True)
class Draft:
    id: int
    position_id: int
    ai_output_id: int
    text: str
    status: str


@dataclass(frozen=True)
class Question:
    id: int
    position_id: int
    stage: str
    ai_output_id: int
    question: str
    purpose: str
    good_answer: str
    status: str


@dataclass(frozen=True)
class Interview:
    id: int
    position_id: int
    stage: str
    starts_at: str
    duration_minutes: int
    interviewer: str
    location: str
    candidate_ref: str
    status: Literal["planned", "cancelled"]


class Repository:
    """One connection is shared by every request, so every transaction and read holds
    a lock. Without it, a write from one thread could join another thread's open
    transaction and be committed or rolled back with it."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._lock = threading.RLock()

    @contextmanager
    def _transaction(self) -> Generator[None]:
        with self._lock, self.conn:
            yield

    def _one(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
        with self._lock:
            return self.conn.execute(sql, params).fetchone()

    def _all(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self._lock:
            return self.conn.execute(sql, params).fetchall()

    # Positions

    def create_position(self, slug: str, title: str) -> Position:
        with self._transaction():
            cur = self.conn.execute(
                "INSERT INTO positions (slug, title, created_at) VALUES (?, ?, ?)",
                (slug, title, now()),
            )
        return Position(id=cur.lastrowid or 0, slug=slug, title=title)

    def get_position(self, slug: str) -> Position | None:
        row = self._one("SELECT id, slug, title FROM positions WHERE slug = ?", (slug,))
        return Position(**dict(row)) if row else None

    def get_position_by_id(self, position_id: int) -> Position | None:
        row = self._one(
            "SELECT id, slug, title FROM positions WHERE id = ?", (position_id,)
        )
        return Position(**dict(row)) if row else None

    def list_positions(self) -> list[Position]:
        rows = self._all("SELECT id, slug, title FROM positions ORDER BY title")
        return [Position(**dict(row)) for row in rows]

    # AI output records

    def record_ai_output(
        self,
        *,
        kind: str,
        inputs: dict[str, Any],
        model_id: str,
        prompt_version: str,
        auth_method: str,
        status: str,
        output: str | None,
        error: str | None,
    ) -> int:
        with self._transaction():
            cur = self.conn.execute(
                """
                INSERT INTO ai_outputs
                    (kind, inputs, model_id, prompt_version, auth_method, status, output, error, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    kind,
                    json.dumps(inputs, ensure_ascii=False),
                    model_id,
                    prompt_version,
                    auth_method,
                    status,
                    output,
                    error,
                    now(),
                ),
            )
        return cur.lastrowid or 0

    def get_ai_output(self, output_id: int) -> AiOutput | None:
        row = self._one(
            """
            SELECT id, kind, model_id, prompt_version, auth_method, status, output, error
            FROM ai_outputs WHERE id = ?
            """,
            (output_id,),
        )
        return AiOutput(**dict(row)) if row else None

    # Chat

    def add_chat_message(
        self, position_id: int, role: str, content: str, ai_output_id: int | None
    ) -> None:
        with self._transaction():
            self.conn.execute(
                """
                INSERT INTO chat_messages (position_id, role, content, ai_output_id, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (position_id, role, content, ai_output_id, now()),
            )

    def list_chat_messages(self, position_id: int) -> list[ChatMessage]:
        rows = self._all(
            """
            SELECT id, role, content, created_at FROM chat_messages
            WHERE position_id = ? ORDER BY id
            """,
            (position_id,),
        )
        return [ChatMessage(**dict(row)) for row in rows]

    # Job drafts

    def add_draft(self, position_id: int, ai_output_id: int, text: str) -> int:
        with self._transaction():
            self.conn.execute(
                "UPDATE job_drafts SET status = 'superseded' WHERE position_id = ? AND status = 'pending'",
                (position_id,),
            )
            cur = self.conn.execute(
                """
                INSERT INTO job_drafts (position_id, ai_output_id, text, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
                """,
                (position_id, ai_output_id, text, now()),
            )
        return cur.lastrowid or 0

    def get_pending_draft(self, position_id: int) -> Draft | None:
        row = self._one(
            """
            SELECT id, position_id, ai_output_id, text, status FROM job_drafts
            WHERE position_id = ? AND status = 'pending' ORDER BY id DESC LIMIT 1
            """,
            (position_id,),
        )
        return Draft(**dict(row)) if row else None

    def get_draft(self, draft_id: int) -> Draft | None:
        row = self._one(
            "SELECT id, position_id, ai_output_id, text, status FROM job_drafts WHERE id = ?",
            (draft_id,),
        )
        return Draft(**dict(row)) if row else None

    def set_draft_status(self, draft_id: int, status: str) -> None:
        with self._transaction():
            self.conn.execute(
                "UPDATE job_drafts SET status = ? WHERE id = ?", (status, draft_id)
            )

    # Interview questions

    def add_questions(
        self,
        position_id: int,
        stage: str,
        ai_output_id: int,
        items: list[tuple[str, str, str]],
    ) -> None:
        with self._transaction():
            self.conn.executemany(
                """
                INSERT INTO interview_questions
                    (position_id, stage, ai_output_id, question, purpose, good_answer, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'proposed', ?)
                """,
                [
                    (
                        position_id,
                        stage,
                        ai_output_id,
                        question,
                        purpose,
                        good_answer,
                        now(),
                    )
                    for question, purpose, good_answer in items
                ],
            )

    def list_questions(self, position_id: int, stage: str) -> list[Question]:
        rows = self._all(
            """
            SELECT id, position_id, stage, ai_output_id, question, purpose, good_answer, status
            FROM interview_questions WHERE position_id = ? AND stage = ? ORDER BY id
            """,
            (position_id, stage),
        )
        return [Question(**dict(row)) for row in rows]

    def get_question(self, question_id: int) -> Question | None:
        row = self._one(
            """
            SELECT id, position_id, stage, ai_output_id, question, purpose, good_answer, status
            FROM interview_questions WHERE id = ?
            """,
            (question_id,),
        )
        return Question(**dict(row)) if row else None

    def update_question(
        self,
        question_id: int,
        *,
        status: str,
        question: str,
        purpose: str,
        good_answer: str,
    ) -> None:
        with self._transaction():
            self.conn.execute(
                """
                UPDATE interview_questions
                SET status = ?, question = ?, purpose = ?, good_answer = ?
                WHERE id = ?
                """,
                (status, question, purpose, good_answer, question_id),
            )

    def is_set_confirmed(self, position_id: int, stage: str) -> bool:
        row = self._one(
            "SELECT 1 FROM confirmed_question_sets WHERE position_id = ? AND stage = ?",
            (position_id, stage),
        )
        return row is not None

    def confirm_set(self, position_id: int, stage: str) -> None:
        with self._transaction():
            self.conn.execute(
                """
                INSERT OR REPLACE INTO confirmed_question_sets (position_id, stage, confirmed_at)
                VALUES (?, ?, ?)
                """,
                (position_id, stage, now()),
            )

    # Interviews (F0010)

    def add_interview(
        self,
        position_id: int,
        *,
        stage: str,
        starts_at: str,
        duration_minutes: int,
        interviewer: str,
        location: str,
        candidate_ref: str,
    ) -> int:
        with self._transaction():
            cur = self.conn.execute(
                """
                INSERT INTO interviews
                    (position_id, stage, starts_at, duration_minutes, interviewer,
                     location, candidate_ref, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'planned', ?, ?)
                """,
                (
                    position_id,
                    stage,
                    starts_at,
                    duration_minutes,
                    interviewer,
                    location,
                    candidate_ref,
                    now(),
                    now(),
                ),
            )
        return cur.lastrowid or 0

    def list_interviews(self, position_id: int) -> list[Interview]:
        rows = self._all(
            """
            SELECT id, position_id, stage, starts_at, duration_minutes, interviewer,
                   location, candidate_ref, status
            FROM interviews WHERE position_id = ? ORDER BY starts_at, id
            """,
            (position_id,),
        )
        return [Interview(**dict(row)) for row in rows]

    def get_interview(self, interview_id: int) -> Interview | None:
        row = self._one(
            """
            SELECT id, position_id, stage, starts_at, duration_minutes, interviewer,
                   location, candidate_ref, status
            FROM interviews WHERE id = ?
            """,
            (interview_id,),
        )
        return Interview(**dict(row)) if row else None

    def update_interview(
        self,
        interview_id: int,
        *,
        stage: str,
        starts_at: str,
        duration_minutes: int,
        interviewer: str,
        location: str,
        candidate_ref: str,
    ) -> None:
        with self._transaction():
            self.conn.execute(
                """
                UPDATE interviews
                SET stage = ?, starts_at = ?, duration_minutes = ?, interviewer = ?,
                    location = ?, candidate_ref = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    stage,
                    starts_at,
                    duration_minutes,
                    interviewer,
                    location,
                    candidate_ref,
                    now(),
                    interview_id,
                ),
            )

    def cancel_interview(self, interview_id: int) -> None:
        with self._transaction():
            self.conn.execute(
                "UPDATE interviews SET status = 'cancelled', updated_at = ? WHERE id = ?",
                (now(), interview_id),
            )

    # Decisions

    def record_decision(
        self,
        *,
        ai_output_id: int,
        subject_type: str,
        subject_id: int,
        action: str,
        final_text: str | None,
    ) -> None:
        with self._transaction():
            self.conn.execute(
                """
                INSERT INTO decisions
                    (ai_output_id, subject_type, subject_id, action, final_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ai_output_id, subject_type, subject_id, action, final_text, now()),
            )
