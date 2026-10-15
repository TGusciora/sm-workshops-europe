# Talk with the user about jobs

Status: draft
Ticket: F0002
Last reviewed: 2026-10-15

## Purpose

The hiring manager discusses a position in a chat with the assistant. The assistant proposes job description text. The hiring manager decides what is saved to the `hiring/` folder.

## Participants

- **Hiring manager**: the person using the application.
- **Frontend**: React chat screen and draft view.
- **Backend**: builds the prompt from the chat, the current job description and the messages so far.
- **SQLite**: stores the chat and the AI output records.
- **Claude API**: produces the proposed text.
- **Hiring folder**: `hiring/<position>/<position>.md`, the saved job descriptions.

## Sequence

```mermaid
sequenceDiagram
    autonumber
    actor HM as Hiring manager
    participant UI as Frontend
    participant API as Backend
    participant DB as SQLite
    participant LLM as Claude API
    participant FS as Hiring folder

    HM->>UI: Ask about a position
    UI->>API: Send message
    API->>FS: Read current job description, if any
    FS-->>API: Current text
    API->>DB: Load chat history
    API->>LLM: Prompt with chat, current text and message
    LLM-->>API: Proposed reply and draft text
    API->>DB: Store reply with inputs and model ID
    API-->>UI: Reply and draft
    UI->>HM: Show reply and draft
    loop Until the hiring manager stops
        HM->>UI: Ask for changes, or edit the draft
        UI->>API: Send message or edited draft
        API->>LLM: Prompt with updated context
        LLM-->>API: Proposed draft
        API->>DB: Store output with inputs and model ID
        API-->>UI: Draft
    end
    HM->>UI: Accept the draft
    UI->>API: Save request
    API->>FS: Write job description file
    API->>DB: Record who accepted, and when
    API-->>UI: Saved
```

## Human decision points

- Every draft is shown to the hiring manager. Nothing is written to `hiring/` without an explicit accept.
- The hiring manager can edit the draft before accepting it. The saved text is the edited version.

## Records kept

- Each AI output: chat messages used, job description version used, model ID, timestamp.
- The accepted file in `hiring/` is the final result. The SQLite record links it to the draft that produced it.

## Data leaving the machine

- Chat messages and the current job description text, sent to the Claude API.
- Job descriptions contain no candidate data. This flow does not send candidate data.

## Open questions

- Is the chat history kept per position, or per session?
- Does the saved job description need a version history in the `hiring/` folder, or only in SQLite?
