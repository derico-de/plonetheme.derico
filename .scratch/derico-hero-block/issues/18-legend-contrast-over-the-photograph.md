# Decide: how the ring legend keeps WCAG AA over the photograph

Type: grilling
Status: resolved
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

## Answer

**Every text element in the hero is guaranteed against any photograph, by two
local grounds. The wash keeps its composition job and loses its legibility
job entirely.** Grilled with md@derico.de, 2026-08-26.

### What the arithmetic settled before any design choice

The ticket framed this as a legend defect with four candidate fixes. Two of the
four are arithmetically dead, and the defect is not the legend's alone. Every
ink composited against the worst backdrop a photograph can present — the wash
over pure white — with WCAG's own thresholds, large text at 3:1:

| element | px @1440 | needs | worst case | on the ground | max image brightness that saves it |
| --- | --- | --- | --- | --- | --- |
| kicker | 21.6 | 4.5 | 1.75 | 10.43 | 0.270 |
| headline | 80 | **3.0** | **3.05** ✓ | 18.16 | none needed |
| lede | 21.6 | 4.5 | 2.57 | 15.27 | 0.486 |
| quiet-link CTA | 16 | 4.5 | 3.05 | 18.16 | 0.615 |
| legend dt/b | 16 | 4.5 | 1.75 | 10.43 | 0.270 |
| legend is-now | 16 | 4.5 | **1.00** | 5.93 | **0.069** |
| legend dd | 15 | 4.5 | 2.57 | 15.27 | 0.486 |

- **The headline is the only element not at risk.** At 80px it is large text,
  needs 3:1, and clears it at 3.05 even against a white photograph. Every other
  element fails worst-case, the legend merely fails first because it lands on
  the brightest pixels.
- **The photograph is author-supplied** (`image_wide` / `image_portrait`,
  object_browser picks, nothing required — ticket 02). There is no "this forest"
  to tune against, so ticket 10's comfortable medians of 8–18 are a property of
  the fixture image, not of the block. Any fix measured against composited
  pixels is measuring an accident.
- **"A darker wash rung at mobile" cannot work.** Guaranteeing even the
  headline needs wash alpha ≥ 0.829; the copper inks need ≥ 0.926 and the is-now
  cyan ≥ 0.983. At those values the photograph is gone and the wash is a panel.
- **"A different is-now ink" cannot work either.** The lightest cyan in the
  palette, `--derico-brand-fill-hover` (`#55bbd3`, 8.36 on the ground), still
  needs ≥ 0.952. No colour reachable from this palette survives a bright
  photograph without a ground.
- **The wide mask cuts the wash AWAY at bottom-left**, it does not strengthen it
  there — `radial-gradient(… at left bottom, transparent 0 55%, black 65%)`
  under `mask-composite: intersect`. The mobile wash has the same hole. That
  clear window is deliberate composition, part of the copy column sits in it,
  and in it the binding cap for the kicker is **0.080**, not 0.270. This is why
  no image-brightness treatment survived the grilling.

### The decision

1. **Scope is hero-wide, not legend-local.** The guarantee is *every text
   element in the hero meets its WCAG threshold over any photograph* — 4.5:1 for
   kicker, lede, CTAs and the whole legend, 3:1 for the headline. Fixing the
   legend alone leaves the headline one bright upload away from failing with no
   ticket behind it.

2. **The legend gets an opaque card** — `background: var(--derico-hero-ground)`
   behind the whole `<dl>`, with padding and a radius. Forced, not chosen: the
   is-now cyan is unreachable by any translucent treatment. On the ground every
   existing colour passes with room (cyan 5.93, copper 10.43, ink-soft 15.27),
   so **no colour changes anywhere**. The card wraps the `<dl>` only — the rings
   disc keeps floating on the photograph, which is the part of the composition
   doing the most work.

3. **The copy column gets a feathered scrim** — new token
   `--derico-hero-copy-scrim`, plateau alpha **0.926**, fading to transparent
   outside the copy box. 0.926 is set by the copper kicker at 4.5:1 against a
   white photograph with no wash. The feather must be *measured*: the plateau
   has to cover the box plus its padding, and the fade begin outside the text,
   because the guarantee holds only where alpha is at or above 0.926.

4. **No image-brightness cap.** Rejected after it was costed properly: it pays
   for legibility with the clear window and the rings side, the two places the
   composition actually spends the photograph, and in the unwashed window it
   would have to reach 0.08 — a black image — to discharge the guarantee.

5. **The wash becomes non-load-bearing at both breakpoints.** At wide the copy
   box is cut out of the existing mask; at mobile the wash is suppressed across
   the copy band. Either way the scrim is the only layer over the copy, which is
   exactly the condition 0.926 was computed for, and the two layers never stack
   (0.72 under 0.926 composites to 0.98 — the solid copy area this avoids).
   The wash keeps its clear window and its composition role untouched.

6. **`#039fba` stays the is-now ink.** It is the exact brand cyan and the row
   the design most wants read as brand; the card makes it pass, so swapping in a
   tint would buy contrast already in hand.

7. **The design source gets the identical CSS**, not a simplified version, so
   ticket 10's parity assertion stays a pixel comparison. The mockup fails the
   same way today and ticket 15's precedent applies: a reference that fails AA
   is not "a trustworthy reference for the next brand block".

### What the acceptance criterion becomes

Two tests with different jobs — **neither is the guarantee alone**:

- **A CSS-value test**: parse the built `blocks.css`, extract
  `--derico-hero-copy-scrim` and `--derico-hero-ground`, composite each ink
  against white and assert the per-element threshold. Proves *the backdrop is
  strong enough where it applies*. Values must be read from the sheet, never
  hardcoded in the test — a test carrying its own copy of 0.926 stays green
  after someone softens the CSS, which is the one regression it exists to catch.
- **`e2e/hero-view.e2e.js`**: delete the named exceptions, per this ticket §3.
  Proves *every glyph sits where it applies*. This is now its real job — it
  catches layout regressions that move text off its promised ground, which is
  exactly what [ticket 17](17-hero-body-type.md)'s leading change will do.

No profile XML changes, so no upgrade step. The canvas inherits all of it
automatically — one scope-wrapped sheet serves both surfaces (ticket 14).

### What came out of it

- [Ticket 20](20-ring-stroke-non-text-contrast.md) — the rings disc misses WCAG
  1.4.11 over a bright photograph (copper 1.79, is-now cyan 1.00, against 3:1),
  and the no-cap decision means nothing here incidentally fixes it. Parked twice
  during the grilling because its remedy is stroke width and a halo, not a
  ground.
- [Ticket 21](21-build-the-contrast-guarantee.md) — building the above.
