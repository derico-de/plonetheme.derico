# Build: the hero's contrast guarantee

Type: task
Status: resolved
Blocked by: —

## Question

Nothing to decide — [ticket 18](18-legend-contrast-over-the-photograph.md)
settled all of it. This is the build.

The guarantee: **every text element in the hero meets its WCAG threshold over
any photograph an author uploads** — 4.5:1 for the kicker, lede, CTAs and the
whole legend, 3:1 for the headline (large text, already clears it at 3.05).

In `bundle-src/src/hero/hero.css`, and identically in
`docs/design/derico.de/site/assets/site.css`:

1. **The legend card** — `background: var(--derico-hero-ground)` behind the
   whole `.ring-legend` `<dl>`, with padding and a radius. Opaque, not
   translucent: the is-now cyan needs wash alpha ≥ 0.983 otherwise. The rings
   disc stays on the photograph — the card wraps the `<dl>` only.
2. **The copy scrim** — new token `--derico-hero-copy-scrim` at plateau alpha
   **0.926**, feathered to transparent outside the copy box. The plateau must
   cover the box plus its padding with the fade beginning outside the text; the
   feather is measured, not eyeballed, because the guarantee holds only at or
   above 0.926.
3. **The wash stops being load-bearing.** At wide, cut the copy box out of the
   existing `mask-image` (extending the fixed-pixel-stop technique from ticket
   06 §9). At mobile, suppress the wash across the copy band. The scrim must be
   the only layer over the copy at both breakpoints — stacking 0.72 under 0.926
   composites to 0.98 and silently produces the solid copy area this design
   avoids. The wash keeps its clear window and its composition role.
4. **No colour changes and no image-brightness cap.** Both were costed and
   rejected on 18.

Two tests, different jobs, neither sufficient alone:

- **CSS-value test**: parse the built `blocks.css`, extract
  `--derico-hero-copy-scrim` and `--derico-hero-ground`, composite each ink
  against white, assert the per-element threshold. Read the values from the
  sheet — a test carrying its own copy of 0.926 stays green after someone
  softens the CSS, which is the regression it exists to catch.
- **`e2e/hero-view.e2e.js`**: delete the named contrast exceptions. This is the
  acceptance criterion from ticket 18 §3.

Interlocks with [ticket 17](17-hero-body-type.md) but is **not blocked by it**:
17's leading change moves the legend's height ~39px at 1440 and so moves which
pixels every glyph covers. A structural guarantee is order-independent by
construction — that both tickets can land in either order without the e2e
breaking is itself a check that the fix is structural rather than tuned.

No profile XML changes, so no upgrade step. The canvas inherits automatically —
one scope-wrapped sheet serves both surfaces (ticket 14).

## Answer

**Built and green: the three named contrast exceptions are deleted and every
glyph in the hero passes at 1440/900/375/320.** Four of the ticket's
instructions held; three did not survive measurement.

### What was built

1. **The legend card** — `background: var(--derico-hero-ground)`,
   `padding: var(--plone-space-m)`, `border-radius: var(--plone-radius-l)` on
   `.ring-legend`. Exactly as specified, and it does exactly what 18 §2 said it
   would: the is-now row went from a named exception at every width to 5.94:1.
2. **The copy scrim** — `--derico-hero-copy-scrim` at plateau alpha 0.926.
3. **The wash cut** at both breakpoints.
4. **No colour changes and no brightness cap.**

### Three corrections

**§1. `0.926`'s stated derivation does not reproduce, and the number that does
reproduce belongs to an ink that is no longer on the scrim.** Ticket 18 §3 says
the plateau is "set by the copper kicker at 4.5:1 against a white photograph
with no wash". Composited in sRGB as a browser does it, the copper kicker at
4.5:1 over white needs **α ≥ 0.7379**, and at 0.926 it gets **8.68:1**. The
number that *does* come out at 4.5:1 is the **is-now cyan**: **0.8965** — and
the cyan was moved onto the opaque card by the same ticket, so the plateau is
sized for an ink that no longer sits on it.

White is genuinely the worst photograph here (a dark scrim composites lightest
there, and every copy ink is lighter than the scrim), so this is not a case of
having taken the easy backdrop. The margin was **kept, not spent**: lowering
the plateau lightens the copy area, and that is a look call against pixels, not
an arithmetic one. What changed is the *test* — it asserts the guarantee, never
the literal, and a companion test derives the floor and proves the assertion
can fail. Whoever wants the photograph more visible now has the number: 0.7379.

**§2. The scrim rides the hero, not the copy column — the copy-column anchor
overflowed the hero.** Built the ticket's way first (a `::before` on the copy
column, inset past it by the plateau margin plus the feather), it hangs 72px
outside the hero at 320: **the hero reported 392 against a 320 client width**,
failing ticket 15's guarantee. `overflow: hidden` clips it visually while still
reporting the scrollable overflow the guarantee is *stated in terms of*, and
widening the guarantee to let a decorative box through would blind it to the
headline overflow it exists for.

So the scrim moved to `.derico-hero::before`, `inset: 0`, where there is
nothing to hang over. **The plateau is a band rather than a box** — it darkens
the copy column above and below the text too — which is the ticket's one real
casualty. It is the same band the wash darkened before, so the composition
keeps its shape; it goes from 0.61 effective to 0.926.

**§3. One boundary, used twice, instead of two tunings that have to agree.**
The ticket asked for a feather "measured, not eyeballed" and a wash cut
extending 06 §9's fixed pixel stops. Both were replaced by something stronger:
the wash is cut away *below* a 50% stop and the scrim painted *above the same
stop*, from opposite sides, at both breakpoints. "The scrim is the only layer
over the copy" then holds by construction rather than by two numbers agreeing,
and a guard asserts the pair share it.

The stop is **proportional, not fixed pixels**. Measured on the design source
at 896-1600 and 320-895: two columns, the copy's right edge sits at
**47.94-48.85%** of the hero; single column, the copy occupies the top **4.1%
to at most 45.5%**. A fixed pixel stop cannot serve both a logged-in author and
a visitor, the hero being viewport-minus-toolbar — that is ticket 15's `cqi`
lesson, and 06 §9's fixed stops were about the *feather*, whose softness should
not stretch. So the boundary is proportional and the feather stays in `rem`.

### The tests

- **CSS-value** (`tests/test_hero_contrast.py`, new): the card, the halo, the
  scrim and the marker chips, each read off the **built** sheet.
  `test_the_scrim_would_go_red_if_it_were_softened` derives the floor rather
  than restating the declaration, and asserts non-vacuity — ticket 19's lesson
  that a guard nothing can falsify protects nothing.
- **`hero-view.e2e.js`**: `CONTRAST_EXCEPTIONS` deleted. Every glyph now passes
  at 0% of its area under threshold, including the two cases the design source
  itself failed.
- **Sheet** (`test_hero_sheet.py`): the card is opaque, the scrim cannot
  overflow, and the scrim and wash share their boundary.

Mutation-checked red-then-green: scrim softened to 0.60, ground lightened,
ground made translucent, card removed, wide wash reverted to 06 §9's 0.85
softening, chip fill darkened. All red.

### What came out of it

**`tests/clara_css.py` never descended into `@container`.** The hero's whole
responsive half lives in `@container (min-width: 56rem)` — ticket 06 §8 chose a
container query over a media query deliberately — so every rule at the wide
breakpoint was invisible to the stylesheet tests. They read as covering the
sheet while covering half of it, and the wide wash cut could not be asserted at
all until the parser was taught the at-rule. Found by writing a test that
should have passed and did not.

**The marker numerals left the pixel probe** — see [ticket
22](22-build-hero-body-type.md), which found it. They are the one text in the
hero whose backdrop is entirely element-painted, so the probe was measuring a
glyph against its own border.

No profile XML changes, so no upgrade step. The canvas inherits the sheet.
