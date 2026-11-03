# ADR-0013: Playwright for end-to-end tests

Status: Accepted
Date: 2026-11-03
Supersedes: none
Superseded by: none

## Context

Vitest and React Testing Library (ADR-0007, ADR-0011) test components in jsdom. They do not run the real app in a browser, and they do not exercise the real backend, the SQLite database or the HTTP proxy from `/api` to the backend (ADR-0009).

The hiring manager needs proof that the whole local application works end to end: the positions, the job description chat with draft decisions, the interview questions, and the interview calendar. The proof should be reviewable, so the run must also produce a video of the walkthrough.

## Decision

Add `@playwright/test` as a development dependency of `frontend/`, pinned to the exact version `1.64.1`, and use its bundled Chromium.

- The end-to-end tests live in `frontend/e2e/` and run with `npm run e2e`.
- Playwright starts the backend and the Vite dev server itself (`webServer` in `frontend/playwright.config.ts`).
- The backend runs with a fresh data directory under the Playwright output folder and with a scripted LLM client (`backend/tests/e2e_app.py`). No real Claude call is made, so the tests are deterministic and need no subscription.
- Video recording is on for every test. Videos and the HTML report are written to `frontend/test-results/` and `frontend/playwright-report/`, both ignored by git.
- The Playwright CLI is not a project dependency. It is installed globally only for manual use.

## Consequences

- One new development dependency, locked in `package-lock.json`. Its browser binaries are downloaded into the Playwright cache, not into the repository.
- The version is pinned, so the browser build matches the library. Upgrading Playwright needs a new `playwright install chromium`.
- The e2e suite is slower than the Vitest suite and needs both servers free on ports 5173 and 8001. Vitest tests stay the fast feedback loop.
- The LLM is faked in e2e runs. Real Claude behaviour is not covered by these tests; it is covered by backend tests and by manual checks.

## Alternatives considered

- Cypress: a larger runtime and a different test model. Playwright also records video and handles two servers in one config.
- Only Vitest with jsdom: fast, but it cannot show the real app working or record a walkthrough.
- The Playwright CLI without a test runner: it can take screenshots but cannot assert, so it cannot prove that the tests pass.
