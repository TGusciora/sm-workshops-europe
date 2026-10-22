# Playbook: team run

For long or unattended work that a build coordinator should run in parallel.

1. Only use a workflow or several subagents if the user asked for multi-agent work in their own words, or said "ultracode". Otherwise ask first and say roughly how many agents it would use.
2. Load `show-me-your-work` so the run reports each step and its result as it goes.
3. Split the work into independent parts, and say which part depends on which.
4. Keep each part small enough that one agent can finish it and report back. Each part must state its inputs, its outputs and what done looks like.
5. Collect the results, check each one against its stated done condition, and report which parts passed and which failed. Do not mark a failed part as done.
