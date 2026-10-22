# Architecture

Implementation architecture of the hiring manager application. There is one document per main functionality, and each contains a Mermaid sequence diagram of its flow.

All diagrams are drafts derived from `CLAUDE.md`. Review them before implementing the matching ticket.

## Index

| Topic | Document |
| --- | --- |
| Component view of the chosen stack | [system-overview.md](system-overview.md) |
| Login to the internal system | [login.md](login.md) |
| Talk with the user about jobs | [job-talk.md](job-talk.md) |
| Talk with the user about interview questions | [interview-questions.md](interview-questions.md) |
| Candidate screening | [candidate-screening.md](candidate-screening.md) |
| Interview calendar | [interview-calendar.md](interview-calendar.md) |

## Conventions

- Diagrams are Mermaid `sequenceDiagram` blocks inside Markdown. GitHub renders them.
- Participants are named the same way in every diagram: `Hiring manager`, `Frontend`, `Backend`, `SQLite`, `Claude API`, `Internal system`, `Hiring folder`.
- Every call to the LLM provider is drawn as a call to `Claude API`. Nothing else leaves the machine.
- Every human decision is drawn as an explicit step, so no proposal reaches storage or a candidate without one.
- To add a functionality, copy `_template/feature.md` and link the new document in the index above.
