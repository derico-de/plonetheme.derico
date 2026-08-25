# Task: install the block and verify it end to end

Type: task
Status: open
Blocked by: 03, 07, 08, 09, 11

## Question

Prove the destination is reached, on the running sandbox site.

- Install the theme; the record appears on the blockaddon diagnostics view as
  enabled, resolvable and compatible.
- As a site administrator: the Derico Hero appears in the slash menu, inserts,
  takes text and both images, and survives a save/reload round-trip.
- As an ordinary editor: the block is **absent** from the slash menu, and a page
  that already contains a hero still renders it in the editor — not an
  unknown-block placeholder. This is the specific claim ticket 03's design
  makes; it is the thing most likely to be subtly wrong.
- The public view matches the mockup at 1440 / 900 / 375 / 320px: no text below
  15px, no horizontal overflow, contrast at WCAG AA over the photograph.
- One React on the page — check for the duplicate-React failure mode the import
  map exists to prevent.

The e2e conventions and the sandbox's port and bundle quirks are already known;
follow them rather than inventing a setup.

## Input from [ticket 15](15-headline-at-320.md) (2026-08-25)

Two additions to the checks above, both cheap and both currently *unverified
assumptions* rather than known facts:

- **`<html lang>` on `@@aurora-edit` matches the content language.**
  `aurora_edit.pt` declares `lang="en"` on the element carrying
  `metal:use-macro`, which METAL should discard in favour of
  `main_template`'s `lang python:portal_state.language()`. Ticket 15 reasoned
  this out with no instance running and deliberately did not trust it. Assert
  it on a German page: the canvas and the view must agree, or `hyphens: auto`
  hyphenates the canvas with English rules.
- **Nothing clips at 320 on either surface**, with a headline long enough to
  force the break rung — check `scrollWidth === clientWidth` on the hero and
  no horizontal document scroll, at 320 and 375, editor and view. The
  pre-existing 320 defect was measured in the design source and fixed there;
  this proves it did not come back through the block.
