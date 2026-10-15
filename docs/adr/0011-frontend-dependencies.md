# ADR-0011: Frontend dependencies

Status: Accepted
Date: 2026-10-15
Supersedes: none
Superseded by: none

## Context

ADR-0007 chose TypeScript, React, Vite, Vitest and React Testing Library for the frontend, and said that each frontend dependency needs an ADR-backed reason when it is added. F0001 is the first ticket that adds them.

## Decision

Runtime dependencies:

- `react`, `react-dom`: the user interface (ADR-0007).

Development dependencies:

- `typescript`, `@types/react`, `@types/react-dom`: type checking and types for React.
- `vite`, `@vitejs/plugin-react`: the dev server, the build and the React transform (ADR-0007).
- `vitest`, `jsdom`: the test runner (ADR-0007) and the browser-like DOM it needs.
- `@testing-library/react`, `@testing-library/dom`: rendering and querying components in tests (ADR-0007).
- `@testing-library/user-event`: simulates typing and clicks in tests, so the tests act the way a user does.

No other frontend library is added. Styling uses plain CSS.

## Consequences

- Each dependency is pinned through `package-lock.json`.
- Adding a UI library, a router or a form library needs a new ADR.

## Alternatives considered

- Jest instead of Vitest: rejected in ADR-0007.
- A component library: not chosen now, because the screens are simple and it would add a large dependency.
