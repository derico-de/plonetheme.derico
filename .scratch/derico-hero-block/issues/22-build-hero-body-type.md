# Build: the hero's body type

Type: task
Status: open
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
