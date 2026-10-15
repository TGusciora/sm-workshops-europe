# F0003: Talk with the user about interview questions

## Goal

For a position and an interview stage, the assistant proposes interview questions. The hiring manager approves, edits or rejects each one. Only the approved set is stored as final.

## Context

Depends on F0001 and reuses the approval component from F0002.

- Architecture: `../../../docs/architecture/interview-questions.md`
- Decisions: ADR-0005 (human approval for every AI output), ADR-0008 (LLM calls)

## Acceptance criteria

- [x] The hiring manager chooses a position and an interview stage, then requests questions.
- [x] Each proposed question shows its purpose and what a good answer covers.
- [x] The hiring manager can approve, edit or reject each question on its own.
- [x] Rejected questions are never stored as final.
- [x] The approved set for a position and stage is stored and can be read back.
- [x] Every proposal batch and every decision has an AI output record, as in F0002.
- [x] The prompt uses the job description and the already-approved questions for that stage, and no candidate data.

## Human decisions

- Each question is approved, edited or rejected one at a time.
- The approved set is saved only when the hiring manager confirms it.

## AI outputs

- Proposed questions for a position and stage. Records the job description version, stage, approved questions used as context, model ID, prompt version, timestamp.

## Out of scope

- Scoring candidate answers (screening, a later phase).
- Sending questions to candidates.

## Open questions

- Export of the approved set to `hiring/`. Decided: not done in Phase 1. The approved set is read back from SQLite only.
- Questions per batch. Decided: 5, set in `backend/app/prompts.py`.
- Interview stages. Decided: a fixed list in code, `backend/app/stages.py` (screening, technical, leadership, final).
- Limitation: once a stage set is confirmed, it cannot be changed in the app. A later ticket can add revision if needed.
- Each decision is stored with the AI output record of the batch it decides on, so a decision can be traced to its proposal.

## Notes

The stage list is a small reference set. Decide whether it lives in the database or in a file under `hiring/` before implementing.
