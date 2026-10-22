# F0010: Interview calendar

## Goal

For a position, the hiring manager plans an interview for a stage with a time, duration, interviewer, place and candidate reference, edits it, cancels it, and sees all of the position's interviews as an agenda grouped by day.

## User stories

```gherkin
Feature: Interview calendar

  Scenario: The hiring manager plans an interview
    Given a position "Head of Sales" is open
    When the hiring manager plans a "technical" interview for 2026-11-03 at 10:00 for 60 minutes with "Anna Kowalska", at "Room 2", for candidate reference "C-14"
    Then the agenda for "Head of Sales" shows the interview under 2026-11-03 at 10:00

  Scenario: The hiring manager edits a planned interview
    Given a planned interview at 10:00 on 2026-11-03
    When the hiring manager changes its start time to 11:00 and saves
    Then the agenda shows the interview at 11:00

  Scenario: The hiring manager cancels an interview and keeps the record
    Given a planned interview
    When the hiring manager confirms its cancellation
    Then the agenda still shows the interview, marked as cancelled
    And the cancelled interview cannot be edited

  Scenario: The agenda is grouped by day and in time order
    Given interviews on 2026-11-03 at 14:00 and 2026-11-03 at 09:00 and on 2026-11-04 at 10:00
    When the hiring manager opens the agenda
    Then the 2026-11-03 group lists 09:00 before 14:00
    And the 2026-11-04 group comes after it

  Scenario: The hiring manager is told when an entry is invalid
    Given a position is open
    When the hiring manager plans an interview with a duration of 2 minutes
    Then the application shows that the duration must be between 5 and 480 minutes
    And no interview is saved
```

## Context

Depends on F0001 (positions) and F0005 (app shell). Uses the stage list in `backend/app/stages.py`. Built as a third section, "Interviews", next to the job description and interview questions.

- Business spec: `../../../spec/business/interview-calendar.md`
- Architecture: `../../../docs/architecture/interview-calendar.md`
- Decisions: ADR-0003 (SQLite, migrations as in ADR-0010), ADR-0005 (human approval for every AI output; this feature has no AI output)

## Acceptance criteria

- [x] The hiring manager plans an interview with stage, start date and time, duration (5 to 480 minutes), interviewer name, location or meeting link, and candidate reference.
- [x] A planned interview is stored in SQLite with its position, and can be read back by position.
- [x] The hiring manager edits a planned interview, and the change is stored.
- [x] The hiring manager cancels an interview after confirming; the interview stays in the record with status cancelled.
- [x] A cancelled interview cannot be edited; the API answers 409 and the screen does not offer editing.
- [x] The agenda lists the position's interviews grouped by day, in time order, cancelled ones included and marked.
- [x] An out-of-range duration, a start time with a time zone, or a blank interviewer or candidate reference is rejected by the API with 422, and an unknown stage with 404 (as in F0003). Nothing is stored in these cases.
- [x] Interviews of one position never appear in another position's agenda.
- [x] No request leaves the machine, and no interview is created, changed or cancelled without a request from the hiring manager.

## Human decisions

- Planning: the hiring manager enters and submits every field. The application saves nothing before submit.
- Editing: the hiring manager changes and submits the fields.
- Cancelling: the hiring manager confirms the cancellation in the screen before the request is sent.

## AI outputs

None. This ticket does not call Claude, so no AI output record is written.

## Out of scope

- Invitations, reminders or any message to a candidate or interviewer.
- Google Calendar or any external calendar sync; ICS export.
- Clash detection between interviews or interviewers.
- A calendar across several positions.
- Deleting interviews.
- Candidate records. The candidate reference is free text until F0009 defines candidates.

## Open questions

- Candidate reference format and retention: see the business spec. Assumed: free text, kept while the position exists. Confirm before F0009.
- Time zone: assumed local to the machine, no time zone stored.

## Notes

- Migration 2 adds the `interviews` table (`backend/app/database.py`). Migration 1 is never edited (ADR-0010).
- The agenda is one list per position, fetched once. Grouping by day happens in the frontend.

## Verification

- Backend: `backend/tests/test_interview_calendar.py` (12 tests), run with `uv run pytest`.
- Frontend: `frontend/src/components/InterviewCalendar.test.tsx` (5 tests), run with `npm test`.
- The last criterion (no request leaves the machine) is checked by reading the code: the feature calls only `/api` routes on the local backend and makes no LLM or external call.
