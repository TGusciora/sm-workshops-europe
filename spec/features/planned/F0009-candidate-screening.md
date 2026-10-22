# F0009: Screen a candidate's CV against the position criteria

## Goal

For a position, the hiring manager gives a candidate's CV to the application. The assistant proposes a screening summary, a score for each criterion with its reason and evidence, and follow-up suggestions. The hiring manager decides every score and the final screening result. Nothing is sent to the candidate.

## User stories

```gherkin
Feature: Screen a candidate's CV against the position criteria

  Scenario: The hiring manager uploads a CV and receives a proposed screening
    Given a position with its job description and screening criteria exists
    When the hiring manager uploads a candidate's CV for that position
    Then the application shows a proposed screening summary
    And each criterion shows a score, the reason for it and the evidence from the CV

  Scenario: The hiring manager changes a proposed score
    Given a proposed screening is shown
    When the hiring manager edits the score or reason for one criterion
    Then the edited value is kept for that criterion
    And the original proposal is still stored unchanged

  Scenario: The hiring manager rejects a criterion
    Given a proposed screening is shown
    When the hiring manager rejects one criterion
    Then that criterion is left out of the final screening

  Scenario: The hiring manager finalises the screening
    Given every criterion has been accepted, edited or rejected
    When the hiring manager finalises the screening
    Then the final screening is saved with the time and the hiring manager as its decider
    And the saved screening links to the proposal it came from

  Scenario: Nothing reaches the candidate
    Given a final screening is saved
    When the hiring manager looks at the candidate's record
    Then the application offers no way to send the screening or any follow-up to the candidate
```

## Context

CLAUDE.md lists candidate screening as one of the four basic functions. The flow is in `../../../docs/architecture/candidate-screening.md`. It is the first ticket that sends candidate data to the Claude API, so it depends on the approval pattern from F0002 and F0003.

- Architecture: `../../../docs/architecture/candidate-screening.md`
- Decisions: ADR-0005 (human approval for every AI output), ADR-0008 (LLM calls)

## Acceptance criteria

- [ ] The hiring manager can upload a CV file for a chosen position.
- [ ] Text is extracted from the CV on the local machine. Only the extracted text is sent to the Claude API.
- [ ] The prompt contains the job description, the screening criteria and the CV text, and nothing else from the candidate record.
- [ ] A proposal shows a summary, one score per criterion with its reason and evidence, and follow-up suggestions.
- [ ] The hiring manager can accept, edit or reject each criterion on its own.
- [ ] Follow-up suggestions are shown for the hiring manager to use or ignore. None is acted on by the application.
- [ ] A final screening is stored only after the hiring manager finalises it.
- [ ] Each proposal records the CV text used, job description and criteria version, prompt version, model ID and timestamp.
- [ ] Each decision records who decided, what changed from the proposal and the timestamp.
- [ ] The final screening links to the proposal it came from.
- [ ] No feature in the application sends anything to the candidate.

## Human decisions

- Each criterion score and reason is accepted, edited or rejected by the hiring manager.
- The hiring manager chooses which follow-up suggestions to use. The application does not act on them.
- The final screening is saved only when the hiring manager finalises it.

## AI outputs

- Screening proposal for one CV and one position. Records the CV text used, the job description and criteria version, the prompt version, the model ID and the timestamp.

## Out of scope

- Ranking or comparing several candidates.
- Automatic rejection, or any decision made without the hiring manager.
- Sending the screening, the score or any follow-up to the candidate.
- Scheduling interviews from a screening result.
- Extracting text from a CV format that is not PDF, DOCX or plain text. Other formats are a later ticket.

## Open questions

- Is the CV file kept in `data/`, or only the extracted text? (`CLAUDE.md`, Open Questions.)
- Which candidate fields are stored, and how long are they kept?
- What is the score scale, and where do the screening criteria come from? They are read from `hiring/` if the position has a criteria file.
- Which CV formats are accepted in this ticket? The list above is a proposal.

## Notes

The architecture diagram marks this flow as draft. Review it before implementation, and update it in the same change if the flow changes.
