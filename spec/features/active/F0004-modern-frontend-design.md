# F0004: Modern frontend design

## Goal

The hiring manager uses an interface that looks current, reads clearly on a laptop and a phone, and works in light and dark mode, without changing what the screens do.

## User stories

```gherkin
Feature: Modern frontend design

  Scenario: The hiring manager reads a screen comfortably on a laptop
    Given the hiring manager opens the application in a desktop browser
    When they move between the talk-about-jobs and interview-questions screens
    Then the layout, spacing and typography are consistent on every screen
    And the main action on each screen is the most visible control

  Scenario: The hiring manager uses the application on a phone-width window
    Given the window is narrower than 600 pixels
    When the hiring manager opens any screen
    Then the content fits the width with a 16 pixel side gutter
    And nothing requires horizontal scrolling

  Scenario: The hiring manager switches between light and dark mode
    Given the operating system is set to dark mode
    When the hiring manager opens the application
    Then every text, panel, border and control remains readable
    And the status colors (ok and error) keep enough contrast on both backgrounds

  Scenario: The hiring manager uses the keyboard only
    Given the hiring manager navigates with the Tab key
    When focus moves across controls
    Then every control shows a visible focus indicator
    And every control can be reached and activated without a mouse
```

## Context

The current styling in `frontend/src/index.css` defines color tokens on `:root`, a single `main` column and a `.panel` class. It works, but it has no shared spacing scale, no focus styles, no responsive rules and no defined type scale. Phase 1 screens (F0002, F0003) are built on it, so this ticket changes the styling layer and the shared components, not the features.

- Frontend stack: ADR-0011 (React, TypeScript, Vite, Vitest).
- Components live in `frontend/src/components/`.
- The frontend talks to the backend only over HTTP. This ticket does not change any API.

## Acceptance criteria

- [x] Color, spacing, radius and type values are defined once as tokens and used everywhere. No screen uses a hard-coded color or size that bypasses the tokens.
- [x] Light and dark themes follow `prefers-color-scheme` and the `data-theme` override already in `index.css`. Both themes meet WCAG 2.2 AA contrast for body text (4.5:1) and for controls (3:1).
- [x] Every interactive element (button, link, input, select, textarea) shows a visible `:focus-visible` style in both themes.
- [ ] Layout works at 320 pixel width with a 16 pixel side gutter and no horizontal page scroll.
- [x] Touch targets are at least 44 by 44 pixels on phone-width screens.
- [x] Buttons have a clear primary and secondary style. A screen has at most one primary action.
- [x] Loading, empty and error states use the same component pattern on every screen.
- [x] Motion respects `prefers-reduced-motion`.
- [x] No new runtime dependency is added. If a styling library is considered, an ADR is written first (`CLAUDE.md`).
- [x] Existing Vitest tests still pass. Add tests for any new shared component.
- [x] `npm test`, `npm run typecheck` and `npm run build` pass in `frontend/`.
- [ ] Before and after screenshots of the talk-about-jobs and interview-questions screens, in light and dark mode, are attached to the pull request.

## Human decisions

- The hiring manager approves the visual direction (palette, type, density) from the before and after screenshots before the ticket is moved to `done/`.
- The hiring manager decides whether to adopt a component library. Until then, the ticket uses plain CSS.

## AI outputs

- None. This ticket changes presentation only and produces no AI output.

## Out of scope

- Changes to backend routes, data models or the Claude wrapper.
- New screens or features. Those belong in their own tickets.
- A brand identity or logo. The product name is still open (`CLAUDE.md`).
- Internationalization.

## Open questions

- Should the palette stay close to the current green and neutral tokens, or move to a new brand direction?
- Is a component library (for example Radix or Tailwind) acceptable? It would need an ADR, so the answer decides whether this ticket starts with one.
- Which screen is the reference for the layout pattern: talk-about-jobs or interview-questions?

## Notes

Start with the token and focus work, which is low risk and fixes accessibility gaps. Layout and component changes can follow in a second pass if the ticket grows.
