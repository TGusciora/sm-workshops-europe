"""Request and response shapes for the HTTP API (ADR-0006)."""

from typing import Literal

from pydantic import BaseModel, Field

Action = Literal["approve", "edit", "reject"]


class Health(BaseModel):
    status: Literal["ok"]
    auth_method: Literal["subscription", "api_key"]


class PositionIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class PositionOut(BaseModel):
    slug: str
    title: str


class JobDescriptionOut(BaseModel):
    slug: str
    text: str | None


class ChatMessageOut(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    created_at: str


class DraftOut(BaseModel):
    id: int
    text: str
    status: str


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class ChatOut(BaseModel):
    messages: list[ChatMessageOut]
    draft: DraftOut | None


class DraftDecisionIn(BaseModel):
    action: Action
    text: str | None = Field(default=None, max_length=50000)


class DraftDecisionOut(BaseModel):
    status: str
    path: str | None


class QuestionOut(BaseModel):
    id: int
    question: str
    purpose: str
    good_answer: str
    status: str


class QuestionSetOut(BaseModel):
    stage: str
    confirmed: bool
    questions: list[QuestionOut]


class QuestionDecisionIn(BaseModel):
    action: Action
    question: str | None = Field(default=None, max_length=2000)
    purpose: str | None = Field(default=None, max_length=2000)
    good_answer: str | None = Field(default=None, max_length=2000)


class StagesOut(BaseModel):
    stages: list[str]
