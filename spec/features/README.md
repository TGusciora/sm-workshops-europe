# Features

Tickets for the application. One Markdown file per ticket. The folder a ticket sits in is its status.

## Folders

- `planned/`: accepted, not started.
- `active/`: being built now. Keep this short.
- `done/`: built and every acceptance criterion checked.
- `dropped/`: decided not to build. Keep the file and write down why.
- `_template/`: the ticket template. Copy it, do not edit it per ticket.

## Rules

1. Create a ticket by copying `_template/ticket.md` into `planned/` as `FNNNN-<slug>.md`, for example `F0001-foundation.md`. The ID is mandatory: `F` followed by a four-digit number. Numbers start at `0001` and are never reused. Take the next free number across all status folders.
2. Change status by moving the file between folders. There is no status field to keep in sync.
3. A ticket that involves an AI output must fill in both "Human decisions" and "AI outputs". This is the boundary from `CLAUDE.md`: the system proposes, a person decides.
4. If a ticket changes a flow, link the matching diagram in `docs/architecture/` and update that diagram in the same change.
5. Move a ticket to `done/` only when every acceptance criterion is checked.
