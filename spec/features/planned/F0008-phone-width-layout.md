# F0008: Phone-width layout

## Goal

On a phone-width window, the hiring manager can use every screen with one hand: positions are chips at the top, the section control spans the width, and every control is large enough to tap, matching `docs/discover/active/design/Phone.dc.html`.

## User stories

```gherkin
Feature: Phone-width layout

  Scenario: The hiring manager switches positions on a phone
    Given the window is narrower than 600 pixels
    When the hiring manager opens the application
    Then the positions appear as chips under the page title
    And the selected position's chip is highlighted

  Scenario: The hiring manager reads and decides on a draft on a phone
    Given the window is narrower than 600 pixels
    And the assistant has produced a draft
    When the hiring manager reads the draft card
    Then the draft text area and both draft buttons fit the width
    And each button is at least 44 pixels high

  Scenario: The hiring manager reads a screen without scrolling sideways
    Given the window is 320 pixels wide
    When the hiring manager opens any screen
    Then the content fits between 16 pixel side gutters
    And nothing requires horizontal scrolling
```

## Context

F0005, F0006 and F0007 are designed for desktop. This ticket adds the phone-width rules that turn the sidebar into a header and stack the content. It depends on those tickets, and on the touch target and gutter rules in F0004.

- Reference: `docs/discover/active/design/Phone.dc.html` (390 by 844).
- Styling: `frontend/src/index.css`, with one breakpoint at 600 pixels.
- No component behavior changes.

## Acceptance criteria

- [ ] Below 600 pixels, the sidebar stacks above the main content. The brand line and the page title sit at the top, and the positions become a row of chips that wrap.
- [ ] Position chips are pill-shaped, at least 44 pixels high, with the selected chip in the green tint and the others in the outlined style.
- [ ] Below 600 pixels, the section control is a two-column grid that fills the width, with each segment at least 44 pixels high.
- [ ] The conversation panel uses 16 pixel padding and bubbles that take at most 82 percent of the width.
- [ ] The draft text area, "Accept draft", "Reject draft" and "Send" are full width and at least 44 pixels high.
- [ ] The "New position" form is still reachable on a phone, below the position chips.
- [ ] At 320 pixels, the layout has a 16 pixel side gutter and no horizontal page scroll.
- [ ] Touch targets (buttons, links, inputs, selects, and text areas) are at least 44 by 44 pixels below 600 pixels.
- [ ] Layout is checked in a browser at 390 and 320 pixels wide before the ticket is moved to `done/`.
- [ ] `npm test`, `npm run typecheck` and `npm run build` pass in `frontend/`.

## Human decisions

- The hiring manager approves the phone layout from a screenshot at 390 pixels before the ticket is moved to `done/`.

## AI outputs

- None. This ticket changes layout only.

## Out of scope

- A native phone app or a separate phone screen.
- Offline use.
- Changes to the desktop layout beyond what F0005 to F0007 define.

## Open questions

- None.

## Notes

Keep the phone rules in one media query in `index.css` so the desktop layout stays readable in one place.
