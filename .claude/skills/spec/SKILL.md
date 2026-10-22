---
name: spec
description: Create a business specification with Mermaid diagrams in spec/business/ from the repository's template, or create feature tickets in spec/features/ from a business specification. Use when the user asks to write, draft or create a spec, business specification, process description or feature ticket.
---

# Specification skill

Two modes. The business specification is the entry point. Feature tickets are derived from it.

- **Spec mode (default):** write a business specification in `spec/business/<slug>.md`, following `spec/business/_template/business-spec.md`. It describes the process, the business rules and the diagrams, and ends with a ticket breakdown.
- **Ticket mode:** create tickets in `spec/features/planned/` from the ticket breakdown of an existing business specification. Use it when the user asks for tickets, or names a business spec and a row of its breakdown.

If the user does not say which mode, use spec mode. Do not create tickets unless asked.

The templates are the source of structure. Copy them, never edit them.

## Spec mode

1. **Read the rules.** Read `spec/business/_template/business-spec.md` and `spec/features/README.md` before writing. Follow the template's headings and order.

2. **Understand the process.** Read the matching notes in `docs/architecture/` and `CLAUDE.md` if the feature touches them, so the business view agrees with the architecture. Do not copy sequence details into the business spec; link to the architecture document instead.

3. **Settle the goal.** If the user's description does not say what the hiring manager gets, ask one short question. If it is clear, do not ask. Pick the most likely reading and state it in your final message.

4. **Write the business rules first.** Number them `BR-01`, `BR-02` and so on. Each rule must be checkable: someone reading it can say whether the application follows it. Business rules drive the user stories of the tickets, so write them before the diagrams.

5. **Draw the process.** Write a Mermaid `flowchart TD` for the whole process. Follow these rules:
   - Start and end with a stadium node: `([Start: ...])` and `([End])`.
   - Name every step that a person performs with the prefix `Human:` in its label, for example `{Human: accept, edit or reject?}`.
   - Every proposal from the system goes through a `Human:` decision before it is stored as final.
   - Quote labels that contain parentheses, commas or colons inside `[...]`, `{...}` or `|...|`, for example `A["Store result (final)"]`.
   - Use one diagram per process. Split only when the process is larger than about 15 nodes.

6. **Draw the lifecycle, if there is one.** If a record moves through states, add a Mermaid `stateDiagram-v2`. Name transitions after the human action or system event that causes them. If the feature has no states, delete the section.

7. **Fill every other section.** Replace every example line and every placeholder. Keep the template's headings in order. For each AI output, record the inputs, the model ID, the prompt version and the timestamp. The business spec must state the candidate data boundary.

8. **Write the ticket breakdown.** Group business rules into tickets, one row per ticket. A ticket should be buildable and checkable on its own. Give each row a proposed title and the rule IDs it covers. Keep status as `not created`.

9. **Save the file.** Write it to `spec/business/<slug>.md`, with a lowercase, hyphenated slug. Do not add an ID. Business specs are not numbered like tickets. If the file already exists, update it instead of creating a second one.

10. **Check the boundary.** The system proposes; a person decides. If the process removes the human from a decision about a candidate, do not write it. Say why and ask how to proceed.

11. **Report.** Give the path, the number of business rules, the proposed tickets and the open questions, one line each.

## Ticket mode

1. **Read the source.** Read the business spec and find the ticket breakdown row the user named. If the user did not name one, create tickets for every row marked `not created`.

2. **Get the next ID.** Look at every status folder under `spec/features/` (`planned/`, `active/`, `done/`, `dropped/`). Take the highest `F<NNNN>` number and add one. Numbers are never reused, so a dropped ticket's number still counts. Format it as four digits.

3. **Create the file.** Copy `spec/features/_template/ticket.md` to `spec/features/planned/FNNNN-<slug>.md`. Replace `FNNNN` in the title with the ID.

4. **Fill the ticket:**
   - **Goal:** from the business goal of the row's rules.
   - **User stories:** one Gherkin `Feature`, one `Scenario` per business rule covered. Steps describe what the hiring manager does and sees.
   - **Context:** link the business spec, for example `../../business/<slug>.md`, and the architecture document.
   - **Acceptance criteria:** one checkable item per covered business rule, plus one for each `Human:` decision the row includes.
   - **Human decisions** and **AI outputs:** copy from the business spec for the rows covered. Required if the ticket involves any AI output.
   - **Out of scope, Open questions, Notes:** copy from the business spec, and remove anything that does not apply to this ticket.

   Remove the template's example bullets. Do not leave placeholder text behind.

5. **Update the breakdown.** In the business spec, change the row's status from `not created` to the ticket ID, for example `F0009`.

6. **Do not change ticket status.** New tickets stay in `planned/`.

7. **Report.** Give the path and ID of each new ticket, and the business spec row it came from.

## Checks before you finish

Spec mode:

- The file is in `spec/business/` and has the template's headings in order.
- Every business rule has a number and is checkable.
- Every diagram is a fenced `mermaid` block, starts with the correct diagram type and uses labels with special characters quoted.
- Every decision a person makes is marked `Human:` in the flowchart, and no proposal reaches "final" without one.
- Each proposed ticket covers rules that all exist in the business rules section.
- No placeholder or example text remains.

Ticket mode:

- The file name matches `FNNNN-<slug>.md` and the ID is the next free one.
- The ticket's Context links back to the business spec.
- Every acceptance criterion is a single, checkable statement.
- If the ticket involves AI, both "Human decisions" and "AI outputs" are filled in.
