# ADR-0008: Claude Agent SDK for LLM calls

Status: Accepted
Date: 2026-10-15
Supersedes: ADR-0004
Superseded by: none

## Context

ADR-0004 chose the Claude API through the `anthropic` SDK, billed by API key. The hiring manager wants the LLM calls made through the Claude Agent SDK, using their own Claude subscription, for use on their own machine only.

Anthropic's [legal and compliance page for Claude Code](https://code.claude.com/docs/en/legal-and-compliance) on 2026-10-15 says:

- OAuth sign-in is "intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans".
- Developers building products that use the Agent SDK "should use API key authentication".
- Developers may not "route requests through Free, Pro, or Max plan credentials on behalf of their users", and may not "collect, store, or intermediate Claude.ai credentials or session tokens".
- End users may sign in to the unmodified Claude Code binary with their own Claude subscription.

Reading these together, the subscription route is allowed only when the hiring manager is the sole end user, on their own machine, and the application never touches the credentials. Secondary coverage of the February 2026 change is [here](https://winbuzzer.com/2026/02/19/anthropic-bans-claude-subscription-oauth-in-third-party-apps-xcxwbn/). This ADR relies on the official page above, not on that coverage.

## Decision

LLM calls go through the Claude Agent SDK, which runs the unmodified Claude Code CLI. The CLI is signed in with the hiring manager's own Claude subscription. The application runs only on the hiring manager's machine and is used only by them.

Conditions, all required:

1. **Single user, single machine.** The application is not hosted, shared, or made available to anyone else. If that changes, this ADR is superseded and the API key route applies.
2. **No credential handling.** The application never reads, stores, logs, or forwards OAuth tokens or session data. Sign-in happens only through the CLI's own flow.
3. **Unmodified CLI.** The Claude Code binary is installed as published and is not patched.
4. **Recorded auth method.** Each AI output record stores the authentication method used (subscription login or API key). It never stores a token or key.
5. **No accidental API billing.** If `ANTHROPIC_API_KEY` is set in the environment, the CLI may use it instead of the subscription. The application checks which method is in effect and records it (condition 4). It does not silently continue on the API key when the subscription was intended.
6. **Usage stays individual.** Plan limits assume ordinary individual use. Heavy automated batch use is out of scope for this application.

The Claude calls still go through one backend wrapper, so the authentication method can be changed without touching the features.

## Consequences

- The backend depends on the Claude Agent SDK package and on the Claude Code CLI, which the SDK runs. The CLI must be installed and signed in on the machine. The LLM features do not work without it.
- The `anthropic` dependency is no longer needed. It is removed in F0001, when the wrapper is built on the Agent SDK.
- Each AI output record needs a new field for the auth method used.
- Terms can change. Re-check the legal page before each major change to how the app authenticates.
- If the hiring manager ever wants to share the app, or Anthropic's terms change, switch to an API key by superseding this ADR. ADR-0004 is the route back.

## Alternatives considered

- API key with the `anthropic` SDK (ADR-0004): fully within the terms for any use, but billed separately from the subscription. This remains the fallback if any condition above stops holding.
- Claude Code CLI driven from a script without the SDK: not evaluated in this record.
