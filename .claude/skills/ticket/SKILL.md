---
name: ticket
description: Turn an existing business specification in spec/business/ into feature tickets in spec/features/planned/, following the ticket template. Use when the user asks to create tickets from a spec, split a spec into tickets, or generate tickets from a business specification, even if they just name the spec file or say "make the tickets".
argument-hint: "<spec> [row or BR-ids] [--dry-run]"
---

# Create tickets from a business specification

Read one business specification and create one ticket per row of its ticket breakdown that is marked `not created`. The business specification is the source of the facts. The ticket template in `spec/features/_template/ticket.md` is the source of the structure. Copy the template, never edit it.

## Arguments

Form: `/ticket <spec> [row] [--dry-run]`

- **`<spec>`** (optional): the spec name or path. Accept `candidate-screening`, `spec/business/candidate-screening.md` or `business/candidate-screening.md`. Resolve it to `spec/business/<name>.md`. If it is missing, list the files in `spec/business/` (excluding `_template/`) and ask which one. If no argument is given and only one spec exists, use it. If several exist, ask.
- **`[row]`** (optional): limit the run to one or more rows of the breakdown. Accept the proposed ticket title (or a unique part of it), the row number counted from 1, or a rule range such as `BR-01..BR-04`. A row is selected when its covered rules include every rule named. Only `not created` rows can be selected; if the user names a row that already has a ticket ID, report it and create nothing for it.
- **`--dry-run`** (optional): do everything except write files. Print the IDs, titles, file paths and the rules each ticket would cover, and the spec change, then stop. Use it when the user wants to check the breakdown first.

Without a `[row]`, create a ticket for every `not created` row.

If the arguments are contradictory or unclear, say what you understood and ask before writing anything.

## Steps

1. **Read the sources.** Read the business specification, `spec/features/README.md` and `spec/features/_template/ticket.md`. Follow the template's headings and their order exactly.

2. **Find the rows to create.** In the spec's "Ticket breakdown" table, take each row whose status is `not created`. If a `[row]` argument was given, keep only the rows it selects. A row marked with an existing ticket ID is already done; leave it alone.

3. **Check each row is complete.** Every business rule that the row lists (for example `BR-01 to BR-04`) must exist in the spec's "Business rules" section. If a rule is missing, stop for that row, report it, and continue with the others. Do not invent rules.

4. **Get the next ID.** Look at every status folder (`planned/`, `active/`, `done/`, `dropped/`) under `spec/features/`. Take the highest `F<NNNN>` and add one. Numbers are never reused, so a dropped ticket's number still counts. When you create several tickets in one run, number them in order without gaps.

5. **Create the file.** If `--dry-run` was given, skip steps 5 to 7 and print the plan from step 4 instead. Otherwise copy the template to `spec/features/planned/FNNNN-<slug>.md`. The slug is lowercase and hyphenated from the row's proposed title. Replace the title line with `FNNNN: <title>`.

6. **Fill each section from the business specification:**
   - **Goal:** one or two sentences about what the hiring manager can do once the covered rules hold. Take the wording from the spec's business goal, narrowed to this row.
   - **User stories:** one Gherkin `Feature` matching the ticket title, one `Scenario` per covered business rule. Steps describe what the hiring manager does and sees, not implementation. A rule about the system's internal behaviour, such as where text is extracted, becomes a `Then` step about what the hiring manager sees, or moves to Notes.
   - **Context:** why it is needed now, and links to the business spec (relative path, for example `../../business/candidate-screening.md`) and to the architecture document named in the spec's links.
   - **Acceptance criteria:** one checkable item per covered business rule, and one item per `Human:` decision the row touches. Start every item unchecked.
   - **Human decisions:** copy the human decision points that the covered rules need. Required if any covered rule involves an AI output.
   - **AI outputs:** copy the AI outputs that the covered rules need, with their inputs, model ID, prompt version and timestamp. Required if any covered rule involves an AI output.
   - **Out of scope:** items from the spec's scope that belong to a different row, plus anything the spec excludes for this feature.
   - **Open questions:** the spec's open questions that affect this row. Leave out the rest.
   - **Notes:** a link back to the business specification and the row it came from. Leave the rest empty.

   Remove the template's example bullets. Do not leave placeholder text behind.

7. **Update the breakdown.** In the business specification, change the row's status from `not created` to the new ticket ID, for example `F0010`. Change nothing else in the spec.

8. **Check the boundary.** The system proposes; a person decides. If a covered rule removes the human from a decision about a candidate, do not write that ticket. Report it and ask the user how to proceed.

9. **Do not change status.** New tickets stay in `planned/`. Do not move them to `active/` or `done/`.

10. **Report.** For each ticket created, give the path, the ID, the title and the rules it covers. List any rows you skipped and why, and any open questions, one line each.

## Checks before you finish

- Each file name matches `FNNNN-<slug>.md`, and the IDs are the next free ones in order with no gaps.
- Every template heading is present, in the template's order.
- No template example text or `FNNNN` placeholder remains.
- Every business rule a ticket claims to cover appears in its user stories or acceptance criteria.
- Every acceptance criterion is a single, checkable statement.
- If a ticket involves AI, both "Human decisions" and "AI outputs" are filled in.
- The business specification changed only in the status column of the rows you created.
