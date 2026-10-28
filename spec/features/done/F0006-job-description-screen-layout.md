# F0006: Job description screen layout

## Goal

On the job description screen, the hiring manager talks with the assistant in a clear conversation, reads the draft in its own card, and accepts or rejects it, matching `docs/discover/active/design/Main.dc.html`. The behavior from F0002 does not change.

## User stories

```gherkin
Feature: Job description screen layout

  Scenario: The hiring manager switches between job description and interview questions
    Given a position is open
    When the hiring manager chooses "Interview questions" in the section control
    Then that section is shown as selected
    And the other section is shown as not selected

  Scenario: The hiring manager reads the conversation
    Given the conversation has messages from the hiring manager and the assistant
    When the hiring manager reads the conversation panel
    Then the hiring manager's messages are on the right in dark bubbles
    And the assistant's messages are on the left in light bubbles

  Scenario: The hiring manager reviews a draft before deciding
    Given the assistant has produced a draft job description
    When the hiring manager reads the draft card
    Then the draft card says "Draft · not saved" and "Needs your decision"
    And the draft text can be edited in place before it is accepted
    And "Accept draft" is the only primary button in the panel

  Scenario: The hiring manager asks for a change
    Given the hiring manager has typed a message
    When they choose "Send"
    Then the message appears in the conversation
    And nothing is saved until the hiring manager accepts a draft
```

## Context

F0002 built the conversation, the draft and the approval. The current `JobTalk.tsx` works, but its layout and styling do not match the design. This ticket restructures the markup and classes of that component. It does not change its behavior or API calls.

- Component: `frontend/src/components/JobTalk.tsx`, tests in `JobTalk.test.tsx`.
- Reference: `docs/discover/active/design/Main.dc.html`.
- Reuses the status and state pattern from F0004 and `StateMessage.tsx`.
- Architecture: `../../../docs/architecture/job-talk.md` (no flow change).

## Acceptance criteria

- [x] The section control is a segmented control with the tab style from the design: a light track, the selected segment white with a subtle shadow, and `aria-pressed` set on each button.
- [x] The "Current job description" block is a collapsed `details` element. When open, the text is shown in a monospace block.
- [x] The conversation is an ordered list. Hiring manager messages align right, the assistant's align left with an "A" avatar. Bubbles take at most 70 percent of the width on desktop.
- [x] The draft card has a tinted background and border, the title "Draft · not saved" and a "Needs your decision" chip.
- [x] The draft text area has a visible label, and its contents are editable before acceptance.
- [x] "Accept draft" is the primary (filled) button. "Reject draft" is the secondary (outlined) button. No other button in the panel is filled.
- [x] The panel header shows "Conversation" and the note "Nothing is saved until you accept a draft".
- [x] The message form has a visible label "Message", a text area with the placeholder "Ask for a change to the job description", and a "Send" button aligned right.
- [x] Existing JobTalk tests still pass. Add a test that the section control and the draft card render the expected labels.
- [x] `npm test`, `npm run typecheck` and `npm run build` pass in `frontend/`.

## Human decisions

- The hiring manager accepts, edits or rejects each draft. Accepting is the only way the job description is saved (unchanged from F0002).
- The hiring manager sends each change request. Nothing is sent automatically.

## AI outputs

- None new. The conversation and drafts are the outputs already recorded by F0002.

## Out of scope

- Phone-width layout (see F0008).
- Any change to what the assistant proposes or how drafts are saved.
- Syntax highlighting or rich text in the draft.

## Open questions

- None.

## Notes

The design's "Current job description" block uses a monospace font. Keep it plain text, since the stored job description is plain text.
