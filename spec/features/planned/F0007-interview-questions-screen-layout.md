# F0007: Interview questions screen layout

## Goal

On the interview questions screen, the hiring manager picks a stage, reviews each proposed question as a card, and confirms the approved set, matching `docs/discover/active/design/Questions.dc.html`. The behavior from F0003 does not change.

## User stories

```gherkin
Feature: Interview questions screen layout

  Scenario: The hiring manager picks a stage and asks for questions
    Given a position is open on the interview questions section
    When the hiring manager chooses a stage and then "Propose questions"
    Then the proposed questions appear as cards below the header
    And the stage control and the button sit beside the section title

  Scenario: The hiring manager decides on each question
    Given a question card shows the status "Proposed"
    When the hiring manager reads its purpose and what a good answer covers
    Then the card offers "Approve", "Edit" and "Reject"
    And the status changes to "Approved" once the question is approved

  Scenario: The hiring manager confirms the approved set
    Given one question is approved and one is waiting for a decision
    When the footer is shown
    Then it reads "1 approved · 1 waiting for your decision"
    And the button reads "Confirm approved set (1)"
    And the set is stored only after the hiring manager chooses that button
```

## Context

F0003 built the proposal, the per-question decision and the confirmed set. This ticket changes the markup, classes and layout of `QuestionReview.tsx`. The approval rules and API calls stay as they are.

- Component: `frontend/src/components/QuestionReview.tsx`, tests in `QuestionReview.test.tsx`.
- Reference: `docs/discover/active/design/Questions.dc.html`.
- Shares the status chip and button styles with F0006.
- Architecture: `../../../docs/architecture/interview-questions.md` (no flow change).

## Acceptance criteria

- [ ] The header shows the title "Interview questions" and the note "Each question is decided on its own. Nothing is final until you confirm the set."
- [ ] The stage select has a visible label "Stage" and the options Screening, Technical and Final. It sits beside "Propose questions" and wraps on narrow widths.
- [ ] Each question is a card with the question text as its main text, a status chip, a "Purpose" line and a "A good answer covers" line.
- [ ] The status chip is green for "Approved", neutral for "Proposed", and uses the same tokens as F0004.
- [ ] On a proposed question, "Approve" is the outlined primary button. "Edit" and "Reject" are secondary buttons. An approved question shows "Edit" and "Reject" only.
- [ ] The footer sits above a divider and shows the count sentence on the left and "Confirm approved set (n)" as the filled primary button on the right.
- [ ] "Confirm approved set" is disabled when no question is approved.
- [ ] Existing QuestionReview tests still pass. Add a test that the footer count and the button label match the number of approved questions.
- [ ] `npm test`, `npm run typecheck` and `npm run build` pass in `frontend/`.

## Human decisions

- The hiring manager approves, edits or rejects each question on its own (unchanged from F0003).
- The hiring manager confirms the approved set. Nothing is final before that step.

## AI outputs

- None new. Proposals and decisions keep the AI output records that F0003 already writes.

## Out of scope

- Phone-width layout (see F0008).
- New stages or new question fields.
- Reordering questions by drag and drop.

## Open questions

- Should "Confirm approved set" with zero approved questions be hidden instead of disabled? The design shows it enabled with one approved question only.

## Notes

The design uses the same card pattern for each question. Keep the card markup identical for approved and proposed states so only the chip and buttons change.
