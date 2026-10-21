# FNNNN: Short title

## Goal

One or two sentences: what the hiring manager can do once this ticket is done.

## User stories

Write each user story in Gherkin. One `Feature` per ticket, one `Scenario` per story. Keep steps about what the hiring manager does and sees, not about implementation.

```gherkin
Feature: Short title matching the ticket

  Scenario: The hiring manager accepts a proposed item
    Given a proposal is shown in the draft view
    When the hiring manager accepts it
    Then the accepted text is saved
    And the saved record links to the AI output that produced it
```

## Context

Why this is needed now. Link the architecture diagram, for example `../../../docs/architecture/<feature>.md`.

## Acceptance criteria

- [ ] Criterion one, written so it can be checked.
- [ ] Criterion two.

## Human decisions

Every point where a person approves, edits or rejects something. Nothing that affects a candidate happens without one of these.

- Example: the hiring manager accepts, edits or rejects each proposed question.

## AI outputs

Each output the system proposes, and what it records: inputs, model ID, timestamp.

- Example: screening summary. Records the job description version, the CV text used, and the model ID.

## Out of scope

- Item that is deliberately not part of this ticket.

## Open questions

- Question that must be answered before or during the work.

## Notes

Free text.
