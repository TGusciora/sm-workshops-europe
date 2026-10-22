# Playbook: workflow

For a request that does not match any other row in the router. Use it only when no other playbook fits.

1. Load `figure-it-out` if it is available. If not, say so and continue with the steps below.
2. Restate the request in one sentence and say what the output should be: an answer, a change to code, a new document, or a new skill.
3. If the output is a change to code, check whether a ticket covers it. If yes, route to the feature playbook. If no, ask the user whether it should become a ticket.
4. If the output is a question, route to the investigation playbook.
5. If you still cannot place the request after these checks, ask the user one question that would settle it.
