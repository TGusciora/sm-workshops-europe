# F0005: App shell and positions sidebar

## Goal

The hiring manager sees a two-column desktop layout, with the positions and the new-position form in a fixed sidebar and the selected position's header and status in the main area, matching `docs/discover/active/design/Main.dc.html`.

## User stories

```gherkin
Feature: App shell and positions sidebar

  Scenario: The hiring manager sees the positions beside the work area
    Given the hiring manager has two positions
    When the application opens on a desktop-width window
    Then the positions are listed in a sidebar on the left
    And the selected position is highlighted and marked "Open"
    And the main area shows the selected position's name and its breadcrumb

  Scenario: The hiring manager sees that the backend is reachable
    Given the backend health check succeeds
    When the hiring manager looks at the page header
    Then a green status pill shows that the backend is running with the subscription login

  Scenario: The hiring manager adds a position from the sidebar
    Given the sidebar shows the positions
    When the hiring manager types a title in "New position" and chooses "Add position"
    Then the new position appears in the list
    And it becomes the selected position
```

## Context

Today `App.tsx` renders the header, the positions panel and the tabs as one stacked column in `main`. The design moves the positions and the new-position form into an `aside`, and the content into a `main` with a page header. The features do not change; only the layout and the components that render them.

- Visual tokens come from F0004 (`index.css`). Build this ticket on those tokens, not on new hard-coded values.
- Components: `App.tsx`, `HealthBadge.tsx`. A sidebar component may be extracted to `frontend/src/components/`.
- Reference: `docs/discover/active/design/Main.dc.html` (desktop, 1280 by 900).
- The frontend talks to the backend only over HTTP. No API change.

## Acceptance criteria

- [x] At 600 pixels and wider, the layout is a fixed 264 pixel sidebar and a fluid main column with 32 pixel top and bottom and 48 pixel side padding.
- [x] The sidebar shows the brand mark, the product name "Onboarding interview" and the list "Positions".
- [x] The selected position has the selected style and the "Open" label. Unselected positions use the plain style.
- [x] The "New position" form sits at the bottom of the sidebar, with its label, input, placeholder "For example, Head of Sales" and "Add position" button.
- [x] The main header shows a breadcrumb "Positions / <title>" and the position title as the page heading (`h1`).
- [x] The backend status pill uses the green style when the health check succeeds and the error style when it fails (see F0004 for the status colors).
- [x] The existing position behavior (select, add, error message) works unchanged. Existing Vitest tests still pass.
- [x] `npm test`, `npm run typecheck` and `npm run build` pass in `frontend/`.

## Human decisions

- The hiring manager chooses which position is open. Nothing is created until they choose "Add position".

## AI outputs

- None. This ticket changes layout only.

## Out of scope

- Phone-width layout (see F0008).
- The section tabs and the screen content (see F0006 and F0007).
- Renaming the product. The name "Onboarding interview" is a working name (`CLAUDE.md`).
- Editing or deleting positions.

## Open questions

- Should the sidebar be a fixed height with its own scroll when many positions exist, or grow with the page?

## Notes

Depends on F0004 for tokens. Can be built before F0006 and F0007, which only need the `main` column.
