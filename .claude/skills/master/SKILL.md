---
name: master
description: Entry point for every request in this repository. Use it first for any request that is not a plain one-line edit, including questions about how the code works, new or changed behaviour from a ticket, deploying a feature, writing or editing a skill, writing docs, ADRs or commit messages, long unattended runs, and anything that does not clearly fit another skill. It classifies the request and routes it to the matching playbook in playbooks/, which then loads the right skills.
---

# Master router

Route each request to exactly one playbook. The playbook says which skills to load and in what order. Do not do the work from this file.

## Step 1: Classify the request

Pick the row whose request kind fits best. Read the request for intent, not for keywords.

| Request kind | Playbook | Skills to load |
| --- | --- | --- |
| A read-only question, or "are we sure?" | `playbooks/investigation.md` | `explain_how`, `investigate` |
| New or changed behaviour from a ticket, including deploying it | `playbooks/feature.md` | `explain_how`, `adversarial-review`, its principles, then `spec` and `ticket` when needed |
| Write or edit a skill | `playbooks/authoring-a-skill.md` | `unslop`, its principles |
| A doc, an ADR, or a commit message | none | `technical-writing` |
| Long or unattended work with a build coordinator | `playbooks/team-run.md` | `show-me-your-work` |
| An app with no scripted user-path proof | none | `create-verification-skill` |
| A request that matches none of the above | `playbooks/workflow.md` | `figure-it-out` |

If two rows fit, choose the one that produces the expected output: a change to the code is a feature, an answer without a change is an investigation.

## Step 2: Check the skill is available

Skills in the table may not all exist in this repository. Before loading one, check the list of available skills. If a skill is missing, do not invent its behaviour. Tell the user which skill is missing and how the playbook falls back. The playbooks say what to do in that case.

## Step 3: Follow the playbook

Open the playbook file and follow it step by step. Load the playbook only once you have classified the request, so the other playbooks stay out of context.

## Rules that apply to every route

- Humans decide anything that affects a candidate. Nothing is sent to a candidate, and no proposal becomes final, without a person's decision (`CLAUDE.md`, Vision).
- If the request is ambiguous, ask one short question before routing. Do not guess between two playbooks that lead to different actions.
- Never deploy without the user's confirmation in this session, unless they have already said to deploy.
