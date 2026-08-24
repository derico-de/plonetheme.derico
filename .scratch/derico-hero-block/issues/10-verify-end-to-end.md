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
