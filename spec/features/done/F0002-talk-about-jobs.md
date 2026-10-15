# F0002: Talk with the user about jobs

## Goal

The hiring manager discusses a position in a chat with the assistant, reviews the proposed job description text, and saves it to `hiring/<position>/` only after accepting it.

## Context

Depends on F0001.

- Architecture: `../../../docs/architecture/job-talk.md`
- Decisions: ADR-0005 (human approval for every AI output), ADR-0008 (LLM calls)

## Acceptance criteria

- [x] The hiring manager can start a chat for a position and send messages.
- [x] Each assistant reply shows the proposed job description text as a draft, separate from the chat.
- [x] The hiring manager can edit the draft before accepting it.
- [x] Accepting writes `hiring/<position>/<position>.md`. The file contains the edited text, not the proposal.
- [x] Rejecting or leaving a draft writes nothing to `hiring/`.
- [x] Every assistant reply and every accepted draft has an AI output record: chat messages used, job description version used, model ID, prompt version, timestamp.
- [x] The accepted file links back to the AI output record that produced the draft.
- [x] No candidate data is sent in this flow. A test checks the prompt contents.

## Human decisions

- Each draft is accepted, edited or rejected by the hiring manager.
- Accepting is the only action that writes to `hiring/`.

## AI outputs

- Assistant reply and draft job description. Records chat messages used, the job description version it was based on, model ID, prompt version, timestamp.

## Out of scope

- Comparing several positions.
- Interview questions (F0003).
- Editing job descriptions that were not created in the app, unless a later ticket asks for it.

## Open questions

- Chat history is kept per position. Decided: one conversation per position, stored in SQLite.
- Pineapple pizza requirement for text the app writes to `hiring/`. Decided: the drafting prompt asks the model to include the requirement. The save step does not check for it, so a reviewer must still see the line in the draft before accepting. Adding a server-side check is a follow-up.
- Version history for `hiring/`. Decided: no version history in `hiring/`. Each accepted file is written over the previous one, and the SQLite record of the draft and its AI output is the history. Git covers the file once it is committed.
- Limitation: only the latest pending draft can be accepted. A new message marks the older draft as superseded.
- The approval step is not a shared component yet. F0003 has its own review view with the same approve, edit and reject rules.

## Notes

The chat screen and the draft view are the first real use of the approval pattern. Keep the approval component reusable for F0003.
