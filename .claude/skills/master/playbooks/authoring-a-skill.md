# Playbook: authoring a skill

For creating a new skill, or changing an existing one under `.claude/skills/`.

1. Read the existing skill, if there is one, and the skill-creator route if the user wants evaluation. A skill with a name that already exists is an edit, not a new skill. Keep the directory name and `name` frontmatter unchanged.
2. Decide what the skill does, when it should trigger, and what it produces. Ask the user for any of these that are unclear. One question at a time.
3. Write `SKILL.md` with `name` and `description`. The description is the trigger, so it must say when to use the skill, not only what it does.
4. Keep the body in imperative form. Explain why each step matters instead of writing bare rules. Load `unslop` and its principles to cut filler from the text, then reread the result.
5. Put long reference material in `references/` and link to it from `SKILL.md`. Keep `SKILL.md` under about 500 lines.
6. Add the new skill to the directory listing in `CLAUDE.md` if the change creates a new folder under `.claude/`.
7. Run `/reload-skills` so the session sees the change, and check the skill appears in the list.
8. For a skill that needs evaluation, hand over to the skill-creator. Offer that when the user wants test cases or a description review.
