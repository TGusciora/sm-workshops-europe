"""HTTP routes. The frontend reaches these only through /api (ADR-0002)."""

import hashlib

from fastapi import APIRouter, HTTPException, Request

from app import hiring_files
from app.config import Settings
from app.llm import LlmCallError, LlmClient, auth_method, call_claude
from app.prompts import (
    INTERVIEW_QUESTIONS_PROMPT_VERSION,
    INTERVIEW_QUESTIONS_SYSTEM,
    JOB_TALK_PROMPT_VERSION,
    JOB_TALK_SYSTEM,
    build_job_talk_prompt,
    build_questions_prompt,
    parse_job_talk_reply,
    parse_questions_reply,
)
from app.repository import Draft, Interview, Position, Repository
from app.schemas import (
    ChatIn,
    ChatMessageOut,
    ChatOut,
    DraftDecisionIn,
    DraftDecisionOut,
    DraftOut,
    Health,
    InterviewIn,
    InterviewOut,
    JobDescriptionOut,
    PositionIn,
    PositionOut,
    QuestionDecisionIn,
    QuestionOut,
    QuestionSetOut,
    StagesOut,
)
from app.stages import STAGES

api = APIRouter(prefix="/api")


def _state(request: Request) -> tuple[Repository, Settings, LlmClient]:
    state = request.app.state
    return state.repo, state.settings, state.client


def _position(repo: Repository, slug: str) -> Position:
    position = repo.get_position(slug)
    if position is None:
        raise HTTPException(status_code=404, detail=f"position {slug!r} not found")
    return position


def _stage(stage: str) -> str:
    if stage not in STAGES:
        raise HTTPException(status_code=404, detail=f"stage {stage!r} not found")
    return stage


def _version(text: str | None) -> str | None:
    """A short fingerprint of the job description used as input, for the AI output record."""
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _draft_out(draft: Draft | None) -> DraftOut | None:
    return (
        DraftOut(id=draft.id, text=draft.text, status=draft.status) if draft else None
    )


@api.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", auth_method=auth_method())


@api.get("/stages", response_model=StagesOut)
def list_stages() -> StagesOut:
    return StagesOut(stages=list(STAGES))


# Positions


@api.get("/positions", response_model=list[PositionOut])
def list_positions(request: Request) -> list[PositionOut]:
    repo, _, _ = _state(request)
    return [PositionOut(slug=p.slug, title=p.title) for p in repo.list_positions()]


@api.post("/positions", response_model=PositionOut, status_code=201)
def create_position(body: PositionIn, request: Request) -> PositionOut:
    repo, _, _ = _state(request)
    slug = hiring_files.slugify(body.title)
    if not hiring_files.is_valid_slug(slug):
        raise HTTPException(status_code=422, detail="the title needs letters or digits")
    if repo.get_position(slug) is not None:
        raise HTTPException(status_code=409, detail=f"position {slug!r} already exists")
    position = repo.create_position(slug, body.title.strip())
    return PositionOut(slug=position.slug, title=position.title)


@api.get("/positions/{slug}/job-description", response_model=JobDescriptionOut)
def get_job_description(slug: str, request: Request) -> JobDescriptionOut:
    repo, settings, _ = _state(request)
    _position(repo, slug)
    text = hiring_files.read_job_description(settings.hiring_dir, slug)
    return JobDescriptionOut(slug=slug, text=text)


# Job talk (F0002)


@api.get("/positions/{slug}/chat", response_model=ChatOut)
def get_chat(slug: str, request: Request) -> ChatOut:
    repo, _, _ = _state(request)
    position = _position(repo, slug)
    return _chat_out(repo, position)


@api.post("/positions/{slug}/chat", response_model=ChatOut)
async def post_chat(slug: str, body: ChatIn, request: Request) -> ChatOut:
    repo, settings, client = _state(request)
    position = _position(repo, slug)
    current = hiring_files.read_job_description(settings.hiring_dir, slug)
    history = repo.list_chat_messages(position.id)
    prompt = build_job_talk_prompt(current, history, body.message)
    try:
        output_id, text = await call_claude(
            repo,
            client,
            kind="job_talk",
            prompt_version=JOB_TALK_PROMPT_VERSION,
            system=JOB_TALK_SYSTEM,
            prompt=prompt,
            inputs={
                "position": slug,
                "job_description_version": _version(current),
                "chat_messages": [m.content for m in history] + [body.message],
            },
        )
    except LlmCallError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    try:
        reply, draft_text = parse_job_talk_reply(text)
    except (ValueError, TypeError) as exc:
        detail = f"the reply could not be read ({exc}); see AI output {output_id}"
        raise HTTPException(status_code=502, detail=detail) from exc

    repo.add_chat_message(position.id, "user", body.message, None)
    repo.add_chat_message(position.id, "assistant", reply, output_id)
    repo.add_draft(position.id, output_id, draft_text)
    return _chat_out(repo, position)


def _chat_out(repo: Repository, position: Position) -> ChatOut:
    messages = [
        ChatMessageOut(role=m.role, content=m.content, created_at=m.created_at)
        for m in repo.list_chat_messages(position.id)
    ]
    return ChatOut(
        messages=messages, draft=_draft_out(repo.get_pending_draft(position.id))
    )


@api.post("/drafts/{draft_id}/decision", response_model=DraftDecisionOut)
def decide_draft(
    draft_id: int, body: DraftDecisionIn, request: Request
) -> DraftDecisionOut:
    repo, settings, _ = _state(request)
    draft = repo.get_draft(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="draft not found")
    if draft.status != "pending":
        raise HTTPException(status_code=409, detail=f"draft is already {draft.status}")
    position = repo.get_position_by_id(draft.position_id)
    if position is None:
        raise HTTPException(status_code=404, detail="position not found")

    if body.action == "reject":
        repo.set_draft_status(draft_id, "rejected")
        repo.record_decision(
            ai_output_id=draft.ai_output_id,
            subject_type="draft",
            subject_id=draft_id,
            action="reject",
            final_text=None,
        )
        return DraftDecisionOut(status="rejected", path=None)

    if body.action == "edit":
        if not body.text or not body.text.strip():
            raise HTTPException(status_code=422, detail="an edit needs the edited text")
        final_text = body.text
    else:
        final_text = draft.text

    path = hiring_files.write_job_description(
        settings.hiring_dir, position.slug, final_text, draft.ai_output_id
    )
    repo.set_draft_status(draft_id, "accepted")
    repo.record_decision(
        ai_output_id=draft.ai_output_id,
        subject_type="draft",
        subject_id=draft_id,
        action=body.action,
        final_text=final_text,
    )
    relative = f"{settings.hiring_dir.name}/{position.slug}/{path.name}"
    return DraftDecisionOut(status="accepted", path=relative)


# Interview questions (F0003)


@api.get("/positions/{slug}/stages/{stage}/questions", response_model=QuestionSetOut)
def get_questions(slug: str, stage: str, request: Request) -> QuestionSetOut:
    repo, _, _ = _state(request)
    position = _position(repo, slug)
    return _question_set(repo, position, _stage(stage))


@api.post("/positions/{slug}/stages/{stage}/questions", response_model=QuestionSetOut)
async def propose_questions(slug: str, stage: str, request: Request) -> QuestionSetOut:
    repo, settings, client = _state(request)
    position = _position(repo, slug)
    stage = _stage(stage)
    current = hiring_files.read_job_description(settings.hiring_dir, slug)
    if current is None:
        raise HTTPException(
            status_code=409, detail="write a job description before proposing questions"
        )
    if repo.is_set_confirmed(position.id, stage):
        raise HTTPException(
            status_code=409, detail=f"the {stage} set is already confirmed"
        )

    approved = [
        q for q in repo.list_questions(position.id, stage) if q.status == "approved"
    ]
    prompt = build_questions_prompt(current, stage, approved)
    try:
        output_id, text = await call_claude(
            repo,
            client,
            kind="interview_questions",
            prompt_version=INTERVIEW_QUESTIONS_PROMPT_VERSION,
            system=INTERVIEW_QUESTIONS_SYSTEM,
            prompt=prompt,
            inputs={
                "position": slug,
                "stage": stage,
                "job_description_version": _version(current),
                "approved_questions": [q.question for q in approved],
            },
        )
    except LlmCallError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    try:
        items = parse_questions_reply(text)
    except (ValueError, TypeError) as exc:
        detail = f"the reply could not be read ({exc}); see AI output {output_id}"
        raise HTTPException(status_code=502, detail=detail) from exc

    repo.add_questions(position.id, stage, output_id, items)
    return _question_set(repo, position, stage)


@api.post("/questions/{question_id}/decision", response_model=QuestionOut)
def decide_question(
    question_id: int, body: QuestionDecisionIn, request: Request
) -> QuestionOut:
    repo, _, _ = _state(request)
    question = repo.get_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="question not found")
    if repo.is_set_confirmed(question.position_id, question.stage):
        raise HTTPException(
            status_code=409, detail="the set is confirmed and can no longer change"
        )

    text = question.question
    purpose = question.purpose
    good_answer = question.good_answer
    if body.action == "reject":
        status = "rejected"
    else:
        status = "approved"
        if body.action == "edit":
            text = body.question or text
            purpose = body.purpose or purpose
            good_answer = body.good_answer or good_answer
    if not text.strip():
        raise HTTPException(status_code=422, detail="a question cannot be empty")

    repo.update_question(
        question_id,
        status=status,
        question=text,
        purpose=purpose,
        good_answer=good_answer,
    )
    repo.record_decision(
        ai_output_id=question.ai_output_id,
        subject_type="question",
        subject_id=question_id,
        action=body.action,
        final_text=text if body.action == "edit" else None,
    )
    return QuestionOut(
        id=question_id,
        question=text,
        purpose=purpose,
        good_answer=good_answer,
        status=status,
    )


@api.post("/positions/{slug}/stages/{stage}/confirm", response_model=QuestionSetOut)
def confirm_questions(slug: str, stage: str, request: Request) -> QuestionSetOut:
    repo, _, _ = _state(request)
    position = _position(repo, slug)
    stage = _stage(stage)
    approved = [
        q for q in repo.list_questions(position.id, stage) if q.status == "approved"
    ]
    if not approved:
        raise HTTPException(
            status_code=409, detail="approve at least one question first"
        )
    repo.confirm_set(position.id, stage)
    return _question_set(repo, position, stage)


# Interview calendar (F0010)


def _interview_out(interview: Interview) -> InterviewOut:
    return InterviewOut(
        id=interview.id,
        stage=interview.stage,
        starts_at=interview.starts_at,
        duration_minutes=interview.duration_minutes,
        interviewer=interview.interviewer,
        location=interview.location,
        candidate_ref=interview.candidate_ref,
        status=interview.status,
    )


@api.get("/positions/{slug}/interviews", response_model=list[InterviewOut])
def list_interviews(slug: str, request: Request) -> list[InterviewOut]:
    repo, _, _ = _state(request)
    position = _position(repo, slug)
    return [_interview_out(i) for i in repo.list_interviews(position.id)]


@api.post("/positions/{slug}/interviews", response_model=InterviewOut, status_code=201)
def plan_interview(slug: str, body: InterviewIn, request: Request) -> InterviewOut:
    repo, _, _ = _state(request)
    position = _position(repo, slug)
    stage = _stage(body.stage)
    interview_id = repo.add_interview(
        position.id,
        stage=stage,
        starts_at=body.starts_at.isoformat(timespec="minutes"),
        duration_minutes=body.duration_minutes,
        interviewer=body.interviewer,
        location=body.location,
        candidate_ref=body.candidate_ref,
    )
    interview = repo.get_interview(interview_id)
    if interview is None:
        raise HTTPException(status_code=500, detail="the interview was not saved")
    return _interview_out(interview)


@api.put("/interviews/{interview_id}", response_model=InterviewOut)
def edit_interview(
    interview_id: int, body: InterviewIn, request: Request
) -> InterviewOut:
    repo, _, _ = _state(request)
    interview = _interview(repo, interview_id)
    if interview.status == "cancelled":
        raise HTTPException(
            status_code=409, detail="a cancelled interview cannot be edited"
        )
    stage = _stage(body.stage)
    repo.update_interview(
        interview_id,
        stage=stage,
        starts_at=body.starts_at.isoformat(timespec="minutes"),
        duration_minutes=body.duration_minutes,
        interviewer=body.interviewer,
        location=body.location,
        candidate_ref=body.candidate_ref,
    )
    updated = repo.get_interview(interview_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="the interview was not saved")
    return _interview_out(updated)


@api.post("/interviews/{interview_id}/cancel", response_model=InterviewOut)
def cancel_interview(interview_id: int, request: Request) -> InterviewOut:
    repo, _, _ = _state(request)
    interview = _interview(repo, interview_id)
    if interview.status == "cancelled":
        raise HTTPException(
            status_code=409, detail="the interview is already cancelled"
        )
    repo.cancel_interview(interview_id)
    updated = repo.get_interview(interview_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="the interview was not saved")
    return _interview_out(updated)


def _interview(repo: Repository, interview_id: int) -> Interview:
    interview = repo.get_interview(interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail="interview not found")
    return interview


def _question_set(repo: Repository, position: Position, stage: str) -> QuestionSetOut:
    questions = [
        QuestionOut(
            id=q.id,
            question=q.question,
            purpose=q.purpose,
            good_answer=q.good_answer,
            status=q.status,
        )
        for q in repo.list_questions(position.id, stage)
    ]
    return QuestionSetOut(
        stage=stage,
        confirmed=repo.is_set_confirmed(position.id, stage),
        questions=questions,
    )
