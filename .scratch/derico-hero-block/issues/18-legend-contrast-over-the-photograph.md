# Decide: how the ring legend keeps WCAG AA over the photograph

Type: grilling
Status: open
Blocked by: —

## Question

The ring legend does not meet AA over the brightest parts of the forest.
Measured by [ticket 10](10-verify-end-to-end.md) against the composited
pixels each glyph actually covers — ground, then photograph, then wash — on
the published page **and on the design source**, which fails the same way:

| element | width | worst | median | share of the glyph area under 4.5 |
| --- | --- | --- | --- | --- |
| `.ring-legend dt` (is-now row) | 1440 | 2.63 | 4.40 | **53 %** (mockup: 44 %) |
| `.ring-legend b` (is-now numeral) | 1440 | 3.21 | 4.16 | **69 %** (mockup: 0 %) |
| `.ring-legend b` 2 / 3 / 4 | 375 | 1.0 – 1.3 | 2.7 – 4.3 | **51 / 64 / 56 %** (mockup: 11 / 44 / 87 %) |

Everything else in the hero passes at every width, most of it comfortably
(medians 8–18). Two distinct causes:

- **The is-now ink is the least contrasty colour in the palette.** The
  highlighted row is the one the design most wants read, and it is the one
  that fails at every width, on both surfaces.
- **At 375 the whole legend crosses the bright part of the photograph.** The
  wash is a gradient tuned for the desktop composition; on a 1166px-tall
  mobile hero the legend has moved out from under it.

What to settle:

1. **What changes** — a scrim or a solid ground behind the legend, a darker
   wash rung at mobile, a different is-now ink, or moving the legend off the
   photograph entirely below the breakpoint. The rings figure is template, so
   this is a design decision, not an author-facing one.
2. **Does the design source change too?** Ticket 15 fixed the mockup's own 320
   defect in the mockup and called it "a trustworthy reference for the next
   brand block". The same argument applies here: if the block is fixed alone,
   the reference is wrong, and ticket 10's parity test compares against a
   source that fails.
3. **What the test then asserts.** `e2e/hero-view.e2e.js` already measures
   this per element (worst ratio, median, share of glyph area) and currently
   *reports* these cases by name rather than asserting them. Deleting those
   named exceptions is the acceptance criterion.
4. Which pixels a glyph lands on shifts with the photograph and with the
   hero's height, so the fix has to be structural (a ground the text is
   guaranteed to sit on), not a colour nudge that passes against this one
   forest. The measured 51–69 % shares are not speckle: they are most of the
   glyph.
