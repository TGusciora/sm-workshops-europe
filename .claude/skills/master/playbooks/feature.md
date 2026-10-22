# Playbook: feature

For new or changed behaviour that comes from a ticket, and for deploying it. The ticket is the source of truth: its user stories and acceptance criteria define done.

## Step 1: Find the ticket

1. Take the ticket ID from the request (`F` plus four digits) or the feature's name.
2. Search every status folder under `spec/features/` (`planned/`, `active/`, `done/`, `dropped/`) for it.
3. Also check `spec/business/` for a business spec that covers the feature.

## Step 2: Branch on what exists

**A ticket exists.** Read its status folder and go to step 3.

- In `done/`: the work is built. Go to the deploy step.
- In `active/`: the work is in progress. Ask the user whether to deploy what exists now or finish first.
- In `planned/`: the acceptance criteria are not checked yet. Ask the user to confirm before deploying, and do not move the ticket on your own. Moving it to `done/` needs every criterion checked.
- In `dropped/`: stop. Tell the user the ticket was dropped and ask what to do.

**No ticket exists.** First search the branches and the repo for the feature, so a ticket is not duplicated. Then go through spec and planning:

1. Load `spec` and run spec mode to write the business spec in `spec/business/<slug>.md`, with the Mermaid diagrams.
2. Decide the open points yourself. For each one, choose the option you would recommend, record it as an assumption in the spec, and list it in the final report so the user can redirect. Do not wait for answers in chat. Only ask when the answer depends on a fact or access that only the user has.
3. Run `ticket` on the spec to create the tickets in `planned/`.
4. Take the new ticket through the deploy step without asking which one, when the request named the feature.

## Step 3: Explain and review the behaviour

Before deploying anything that changes behaviour, load `explain_how` to explain the change, and `adversarial-review` with its principles to challenge it. Report what the review found. Fix findings the user agrees with, and list the ones they reject.

## Step 4: Deploy means implement and test

In this repository "deploy" means implement the ticket and test it locally. The app runs on the hiring manager's machine (`CLAUDE.md`), so there is no hosting target.

1. Implement the acceptance criteria, add the backend and frontend tests, and update the matching diagram in `docs/architecture/`.
2. Run the checks from `CLAUDE.md`: `uv run ruff check`, `uv run ruff format --check`, `uv run ty check`, `uv run pytest`, and in `frontend/` `npm run typecheck`, `npm test`, `npm run build`.
3. Report the ticket ID, what was built, the check results, and each assumption made. Do not move the ticket to `done/` unless every acceptance criterion has been checked by a test or by reading the code.
