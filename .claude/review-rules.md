# Review rules

Specific rules the reviewer agent applies on top of the ticket's acceptance criteria. Loaded at the start of every reviewer run by `.claude/hooks/review.py`. Edit this file to change the rules; no restart is needed for the next reviewer run.

- Every Claude call goes through `backend/app/llm.py`, and it writes an AI output record, including when the call fails.
- Tests never call the real Claude service.
- Candidate data is never logged and never leaves `data/` except in LLM calls the feature needs.
- A new dependency needs an ADR in `docs/adr/`.
- Nothing is sent to a candidate automatically, and no AI proposal becomes final without a person's decision.
- Backend code is Python 3.12 only, with type hints on every parameter and return.
- The matching diagram in `docs/architecture/` is updated when a flow or component changes.
