# Talk with the user about interview questions

Status: draft
Ticket: F0003
Last reviewed: 2026-10-15

## Purpose

For a position and an interview stage, the assistant proposes interview questions. The hiring manager approves, edits or rejects each question. Only approved questions become the question set for that stage.

## Participants

- **Hiring manager**: the person using the application.
- **Frontend**: question review screen.
- **Backend**: builds the prompt from the job description, the stage and the questions already approved.
- **SQLite**: stores proposals, decisions and the approved question sets.
- **Claude API**: produces the proposed questions.
- **Hiring folder**: source of the job description.

## Sequence

```mermaid
sequenceDiagram
    autonumber
    actor HM as Hiring manager
    participant UI as Frontend
    participant API as Backend
    participant FS as Hiring folder
    participant DB as SQLite
    participant LLM as Claude API

    HM->>UI: Choose position and interview stage
    UI->>API: Request questions
    API->>FS: Read job description
    FS-->>API: Job description text
    API->>DB: Load approved questions for this stage
    API->>LLM: Prompt with job description, stage and approved questions
    LLM-->>API: Proposed questions, each with purpose and what a good answer covers
    API->>DB: Store proposals with inputs and model ID
    API-->>UI: Proposed questions
    UI->>HM: Show each question
    loop For each question
        HM->>UI: Approve, edit or reject
        UI->>API: Decision on this question
        API->>DB: Store decision
    end
    API->>DB: Store approved question set for this stage
    API-->>UI: Question set saved
    UI->>HM: Show approved set
```

## Human decision points

- Each question is approved, edited or rejected one by one. Rejected questions are not stored as final.
- The approved set is what the hiring manager uses in interviews. Proposals alone are never treated as final.

## Records kept

- Each proposal batch: job description version, stage, approved questions used as context, model ID, timestamp.
- Each decision: approve, edit or reject, with the edited text where relevant.

## Data leaving the machine

- Job description text, stage name and approved questions, sent to the Claude API.
- No candidate data in this flow.

## Open questions

- Should the approved question set also be exported to the `hiring/` folder?
- How many questions per proposal batch?
