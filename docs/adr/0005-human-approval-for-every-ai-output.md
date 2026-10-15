# ADR-0005: Human approval for every AI output

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

The application is semi-autonomous. It prepares work for the hiring manager, but decisions that affect a candidate must stay with a person (`CLAUDE.md`, Vision). Recommendations that cannot be traced to their inputs cannot be reviewed.

## Decision

Every AI output is a proposal until a person approves, edits or rejects it. Only an approved or edited result is stored as final. Every AI output records its inputs, the model ID, the prompt version and a timestamp. Nothing is sent to a candidate automatically.

## Consequences

- Each feature needs a visible decision step in its flow. The architecture documents mark these as "Human decision points".
- The data model needs a proposal table separate from the final result, linked by a decision record.
- Features that remove the human from a candidate decision are out of scope, as `CLAUDE.md` already states.
- Reviewing a proposal takes the hiring manager's time. That cost is accepted.

## Alternatives considered

- Automatic approval above a confidence threshold: rejected, because the application does not produce calibrated confidence, and it would remove the human from a candidate decision.
