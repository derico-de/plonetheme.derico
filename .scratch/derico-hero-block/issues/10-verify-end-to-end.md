# Task: install the block and verify it end to end

Type: task
Status: resolved
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

## Answer

**The block installs, inserts, authors, saves and renders — and the published
page matches the design source everywhere except its type family.** Run on the
sandbox site (`/Plone`, Zope on 8081, the mockup bundle from the webpack dev
server on `powerman:8000`), 2026-08-26. Two defects came out of it and are now
[ticket 17](17-hero-body-type.md) and
[ticket 18](18-legend-contrast-over-the-photograph.md); a third, smaller one
is [ticket 19](19-hide-the-upgrade-profile.md).

The proof is not a session transcript. It is
[`e2e/`](../../../e2e/) — `hero-editor.e2e.js`, `hero-view.e2e.js` and the
fixture and measurement modules they share — written to the Blicca e2e
conventions the ticket pointed at, and re-runnable. What follows is what those
tests establish.

### What holds

- **Install.** The theme was at profile version 1000; upgrade step **1001**
  applied cleanly over restapi. The diagnostics view
  (`@@aurora-block-addons`) reports `plonetheme.derico.hero` as **loaded,
  compatible, enabled**, weight 100, both `++plone++plonetheme.derico.blocks/`
  URLs resolving, `derico-hero` as its only `@type`, and the insert permission
  named. (The fresh-install path is the integration suite's, not this
  ticket's: `tests/test_hero_install.py` runs the profile from empty.)
- **The administrator's round trip.** The hero is in the slash menu, inserts,
  and previews in the canvas. Every field authored through the sidebar — the
  five text fields, four legend rows, two content picks, two image picks —
  survives save *and* reload. `blockWidth` is materialised to `"full"` at
  insert, exactly as ticket 11 said it would be. Each of the four references
  is stored as **one element carrying the bare `@id`**; the two image picks
  additionally carry `image_scales` **on read**, which is stock restapi's
  enrichment (§5.3, ticket 01) and not the widget failing to trim — the first
  version of this test asserted "one key" and was wrong, not the block.
- **The insert gate does what ticket 03 designed.** An ordinary editor
  (Editor on the fixture folder, nothing above it) is offered the same
  19-item slash menu **minus** the Derico Hero, and a page that already holds
  a hero **renders it** for them — no unknown-block placeholder, no page
  errors. This was the claim most likely to be subtly wrong; it is right.
- **One React.** The block's resource directory serves exactly two files,
  `hero.js` and `blocks.css`, and nothing else — a bundled React would appear
  there. The import map aliases `react` onto the editor remote's own facade,
  and the block mounts and runs hooks inside Plate, which a second copy would
  prevent.
- **`<html lang>` matches.** Editor and view both report `de` on a German
  site. Ticket 15's reasoning about METAL discarding `aurora_edit.pt`'s
  `lang="en"` was right, and is now measured rather than assumed.
- **Nothing clips at 320 or 375**, on either surface, with a headline whose
  longest compound cannot fit: hero `scrollWidth === clientWidth` and no
  horizontal document scroll at every tested width. Ticket 15's ladder holds.
- **The published page against the mockup**, measured side by side in one
  browser at 1440 / 900 / 375 / 320 — the hero is full-bleed at every width
  (viewport-wide at x=0, anonymous, no toolbar to subtract), the grid tracks
  are **identical to the pixel** (590.4/567.2 at 1440, 343 at 375, 288 at
  320), the container query flips to one column at exactly the same place, the
  rings stage and disc match to the pixel (544x376 at 1440, 343x237 at 375),
  markers stay 28x28, and nothing is under 15px. The headline carries the
  design's `-0.02em`, not Clara's `-0.015em`.
- **The `<picture>` is what ticket 05 and ticket 09 decided**: two sourcesets,
  portrait first behind `(max-width: 55.99rem)` and wide second, both
  `sizes="100vw"` with width descriptors, no `type=`, and an `<img>` that is
  `alt=""`, `fetchpriority="high"` and NOT lazy, filling the hero.

### What does not

**1. The hero's body type is not the theme's** ([ticket 17](17-hero-body-type.md)).
Everything but the two display elements renders in `ui-sans-serif, system-ui, …`
at leading 1.6, where the mockup has `"Source Sans 3"` at 1.65. Neither the
block nor the theme states it: Blicca's `blocks_view.css` puts a Tailwind
stack and `--aurora-content-line-height` on `.aurora-blocks-view` so that the
published page matches the *canvas*, and the hero inherits that instead of
`body`. The block is internally consistent — both surfaces agree — and both
disagree with the design. It is also the whole of the one remaining geometry
difference: the ring legend is 291px against the mockup's 330 at 1440, which
is four rows of 1.6 leading instead of 1.65.

**2. The ring legend misses AA over the photograph** ([ticket 18](18-legend-contrast-over-the-photograph.md)),
in the design source as much as here. The is-now row fails at every width
(53 % of its glyph area under 4.5 at 1440), and at 375 the numerals go with it
(51–64 %). Everything else in the hero passes at every width with medians of
8–18. The measurement is against the pixels each glyph actually covers, not
against a computed `background-color` — the hero paints ground, then
photograph, then wash, so no ancestor's colour is what the reader sees.

**3. The upgrade profile is offered as an add-on** ([ticket 19](19-hide-the-upgrade-profile.md)).
`plonetheme.derico.upgrades` appears in `@addons` as installable; both sibling
packages hide theirs in `HiddenProfiles`.

### Three notes that changed how this was measured

- **A worst-pixel contrast number cannot tell a defect from a speckle.** The
  first version of the check took the darkest pixel in each text element's
  *box* and failed everything, including the mockup, at ratios of 1.0 — partly
  because `getComputedStyle().color` hands back `oklch(…)` verbatim and
  reading those three numbers as RGB makes every ratio come out at 1. The
  method that works: screenshot the hero twice, once with the glyphs painted
  transparent, and read the difference — a pixel the two shots disagree on is
  a pixel a glyph covered. Report the worst ratio, the median, **and the share
  of the glyph's own area below the threshold**. The genuine failures sit at
  44–87 % of the glyph area; the speckles at 0.1 %; nothing observed lands
  between 2 % and 11 %, which is what makes a threshold defensible.
- **`visibility: hidden` is the wrong way to reveal a background** — it takes
  the element's own background with it, so the call to action and the ring
  markers were being read against the forest behind them rather than against
  their own fill. `color: transparent` keeps the paint and removes the glyph.
- **Scope every query to the hero's root.** `document.querySelector('h1')` on
  the published page returns the *content header's* title, not the block's —
  which produced a confident, entirely false report that the headline's
  tracking and font were wrong. `derico.css` §7 hides that element; it is
  still in the DOM.

### Left behind on the sandbox

Nothing: both tests delete their fixture (`DERICO_E2E_KEEP=1` keeps it). The
theme stays installed at profile version 1001, and the earlier
`/Plone/hero-probe-article` from ticket 07 is untouched.
