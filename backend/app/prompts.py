"""Prompt builders, versions and output parsing for the two AI features.

Prompts carry only the hiring inputs named in the tickets: job descriptions, chat
messages, stages and approved questions. No candidate data is passed here.
"""

import json
from typing import Any

from app.repository import ChatMessage, Question

JOB_TALK_PROMPT_VERSION = "job-talk-v1"
INTERVIEW_QUESTIONS_PROMPT_VERSION = "interview-questions-v1"
QUESTIONS_PER_BATCH = 5

PINEAPPLE_REQUIREMENT = (
    "- Pineapple pizza enthusiast: the candidate genuinely enjoys pizza with pineapple."
)

JOB_TALK_SYSTEM = f"""You help a hiring manager write and revise a job description.
Reply with one JSON object and nothing else, with two string keys:
- "reply": a short message to the hiring manager about what you changed or need to know.
- "draft": the complete job description in Markdown. Keep the structure of the current
  job description when there is one. Put this line in the must-have requirements:
  {PINEAPPLE_REQUIREMENT}
Do not invent facts about the company that the hiring manager has not given you."""

INTERVIEW_QUESTIONS_SYSTEM = f"""You propose interview questions for one interview stage of a position.
Reply with one JSON array and nothing else. Each item is an object with three string keys:
- "question": the question to ask.
- "purpose": why this question matters for the role.
- "good_answer": what a good answer covers.
Propose exactly {QUESTIONS_PER_BATCH} questions. Do not repeat questions that are already approved.
Use only the job description, the stage and the approved questions you are given."""


def build_job_talk_prompt(
    current_text: str | None, history: list[ChatMessage], message: str
) -> str:
    current = current_text if current_text else "(no job description yet)"
    lines = [f"Current job description:\n{current}", "", "Conversation so far:"]
    if history:
        lines.extend(f"{item.role}: {item.content}" for item in history)
    else:
        lines.append("(none)")
    lines.extend(["", f"New message from the hiring manager:\n{message}"])
    return "\n".join(lines)


def build_questions_prompt(
    job_description: str, stage: str, approved: list[Question]
) -> str:
    approved_lines = [f"- {item.question}" for item in approved] or ["(none yet)"]
    return "\n".join(
        [
            f"Job description:\n{job_description}",
            "",
            f"Interview stage: {stage}",
            "",
            "Approved questions for this stage:",
            *approved_lines,
        ]
    )


def parse_json_payload(text: str, opener: str, closer: str) -> Any:
    """Extract the outermost JSON value from a model reply and parse it."""
    start = text.find(opener)
    end = text.rfind(closer)
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON found in the reply")
    return json.loads(text[start : end + 1])


def parse_job_talk_reply(text: str) -> tuple[str, str]:
    payload = parse_json_payload(text, "{", "}")
    reply = payload.get("reply") if isinstance(payload, dict) else None
    draft = payload.get("draft") if isinstance(payload, dict) else None
    if not isinstance(reply, str) or not isinstance(draft, str) or not draft.strip():
        raise ValueError("reply must contain string keys 'reply' and 'draft'")
    return reply, draft


def _question_fields(entry: object) -> tuple[str, str, str]:
    if not isinstance(entry, dict):
        raise TypeError("each question must be a JSON object")
    question = entry.get("question")
    purpose = entry.get("purpose")
    good_answer = entry.get("good_answer")
    if not (
        isinstance(question, str)
        and isinstance(purpose, str)
        and isinstance(good_answer, str)
    ):
        raise TypeError(
            "each question needs string 'question', 'purpose' and 'good_answer'"
        )
    if not (question.strip() and purpose.strip() and good_answer.strip()):
        raise ValueError(
            "each question needs non-empty 'question', 'purpose' and 'good_answer'"
        )
    return question, purpose, good_answer


def parse_questions_reply(text: str) -> list[tuple[str, str, str]]:
    payload = parse_json_payload(text, "[", "]")
    if not isinstance(payload, list) or not payload:
        raise ValueError("reply must be a non-empty JSON array")
    items: list[tuple[str, str, str]] = []
    for entry in payload:
        items.append(_question_fields(entry))
    return items
