# Interview calendar

Status: draft
Ticket: F0010
Last reviewed: 2026-10-22

## Purpose

For a position, the hiring manager plans, edits and cancels interviews, and sees them as an agenda grouped by day. No AI is involved, and nothing is sent outside the machine.

## Participants

- **Hiring manager**: the person using the application.
- **Frontend**: the Interviews section and its agenda and form.
- **Backend**: validates entries and applies the rules (one stage per position, cancelled interviews are read-only).
- **SQLite**: stores the interviews.

Claude API and the hiring folder are not used by this flow.

## Sequence

```mermaid
sequenceDiagram
    autonumber
    actor HM as Hiring manager
    participant UI as Frontend
    participant API as Backend
    participant DB as SQLite

    HM->>UI: Opens the Interviews section of a position
    UI->>API: GET /api/positions/{slug}/interviews
    API->>DB: Read interviews of the position
    DB-->>API: Interviews
    API-->>UI: Interviews
    UI-->>HM: Agenda grouped by day

    alt Plan an interview
        HM->>UI: Enters stage, time, duration, interviewer, place, candidate reference
        HM->>UI: Submits
        UI->>API: POST /api/positions/{slug}/interviews
        API->>API: Validate stage, duration and time
        API->>DB: Insert interview as planned
        DB-->>API: Saved
        API-->>UI: Interview
    else Edit an interview
        HM->>UI: Changes fields and submits
        UI->>API: PUT /api/interviews/{id}
        API->>DB: Read status; reject if cancelled
        API->>DB: Update interview
        API-->>UI: Interview
    else Cancel an interview
        HM->>UI: Confirms cancellation
        UI->>API: POST /api/interviews/{id}/cancel
        API->>DB: Set status to cancelled
        API-->>UI: Interview
    end

    UI-->>HM: Agenda shows the change
```

## Notes

- Nothing is sent to a candidate or an interviewer. No calendar service is called.
- Cancelled interviews stay in the agenda and cannot be edited.
