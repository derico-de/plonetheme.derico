# Build: the hero's body type

Type: task
Status: resolved
Blocked by: 17

## Question

Nothing to decide — [ticket 17](17-hero-body-type.md) settled all of it. This
is the build.

The change: the hero states its own body type from the public `--plone-*`
ladder, so canvas and published view both render the design's font at the
design's leading.

In `bundle-src/src/hero/hero.css`, on `.derico-hero` (the component's own root,
never Aurora's `.block-derico-hero` wrapper — the sheet's rules of the road):

```css
font-family: var(--plone-font-body);
line-height: var(--plone-leading-body);
```

Both tokens are Clara `:root` declarations carrying the mockup's exact values
(`"Source Sans 3", system-ui, sans-serif` and `1.65`), and both are on the side
of the ladder ticket 06 §3 permits a block sheet to speak. So:

- **`derico.css` is not touched.** No fourth `--derico-*` type alias — §3's
  aliases exist for tokens with no `--plone-*` equivalent, and these have one.
  `test_block_sheets_never_name_a_clara_token` (ticket 14 §9) stays satisfied
  without any new seam.
- **`blocks_view.css` is not touched.** Blicca's Tailwind stack keeps its job
  for every other block; the hero simply out-specifies it on its own root.
- **The canvas follows automatically** — the sheet is wrapped in
  `@scope (.aurora-editor, .aurora-editor-portal, .aurora-blocks-view)`, so one
  declaration lands on both surfaces. This is the whole reason the block sheet
  was chosen over the theme layer.

Mirror the same two declarations into
`docs/design/derico.de/site/assets/site.css` only if they are not already
implied there — the mockup sets them on `body`, so the diffability convention
may need no change at all. Check before editing; a gratuitous edit to the
mockup sheet makes the two files *less* diffable, not more.

Three tests, and the third is the point (ticket 17 §Q4):

- **CSS-value test** — parse the built `src/plonetheme/derico/static-blocks/blocks.css`,
  assert `.derico-hero` names `var(--plone-font-body)` and
  `var(--plone-leading-body)`. Catches a hardcoded `"Source Sans 3"` (passes
  every visual check, silently drops the theme seam) and catches the leading
  being dropped on its own.
- **`e2e/hero-view.e2e.js`** — computed `font-family` on a hero body element
  begins `"Source Sans 3"`, computed `line-height` is 1.65em. The assertion
  that would have caught what [ticket 10](10-verify-end-to-end.md) found by
  measurement.
- **The same two assertions in the canvas**, inside `@@aurora-edit`. Parity is
  the entire justification for the chosen seam, so it gets pinned rather than
  assumed.

Interlocks with [ticket 21](21-build-the-contrast-guarantee.md) but is **not
blocked by it, in either direction**: the leading change moves the legend's
height ~39px at 1440 and so moves which pixels every glyph covers. 21's
guarantee is order-independent by construction, and these two landing in either
order without the contrast e2e breaking is the check of that claim. Do not fold
this ticket into 21 — merging them destroys the check.

No profile XML changes, so no upgrade step.

## Answer

**Built and green; the ticket's instructions held in full, and the only thing
that came out of it was a defect somewhere else.**

`.derico-hero` states `font-family: var(--plone-font-body)` and
`line-height: var(--plone-leading-body)`. Both were confirmed present on
Clara's `:root` before being named. `derico.css` untouched, `blocks_view.css`
untouched, no fourth alias.

**The design source needed no edit at all** — checked before editing, as the
ticket asked. `site.css:120,132` already set `font-family: var(--font-body)`
and `line-height: 1.65` on `body`, so the mockup was always rendering what the
block now renders. A gratuitous mirror would have made the two files less
diffable, which is exactly what the ticket warned about.

Three tests, all three the ones the ticket named:

- **CSS-value**, `test_the_hero_takes_its_body_type_from_the_public_ladder` —
  the built sheet must *name* both tokens. Plus a second guard the ticket did
  not ask for, `test_the_hero_never_hardcodes_its_type`: naming the token is
  not enough if a later rule restates `"Source Sans 3"` literally, which passes
  every visual check while silently dropping the seam. Mutation-checked: both
  go red when the family is hardcoded, and the first also goes red when either
  declaration is dropped on its own.
- **`hero-view.e2e.js`** — ticket 17's reported-not-asserted note became three
  assertions: the computed family is `Source Sans 3`, the computed leading is
  1.65, and the hero agrees with the page. Green at 1440/900/375/320.
- **The same pair in the canvas**, in `hero-editor.e2e.js`. This is the
  assertion that justifies the seam rather than merely exercising it.

### What came out of it

**The type change moved a marker numeral across the e2e's speckle threshold.**
`.ring-markers li "1"` at 375 went from 2% of its glyph area under 4.5 to 3%,
against a `SPECKLE` of 2% whose stated basis was that "nothing observed lands
between 2% and 11%". Nothing about the contrast changed — the glyph shape did.
Verified by reverting only these two declarations in the built sheet and
re-running: the worst pixel stays 1.02 either way, only the share moves.

That worst pixel is the point: 1.02 is ground on ground, i.e. the glyph's
antialiased edge overlapping the chip's own 2px ground border. The marker
numerals are the one text in the hero that is never over the photograph, so the
pixel probe was the wrong instrument for them. They moved to the value test
(`test_the_marker_chips_carry_their_own_backdrop`, four pairs, both the 1.4.3
and the 1.4.11 half of ticket 20 §6). Raising `SPECKLE` would have bought this
by blunting the guard for every element that *is* over the photograph.

Interlock with 21 held as predicted: this landed with 21 and 23 in the same
session and the contrast e2e did not break, which was the check.
