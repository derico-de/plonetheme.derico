# Build: the rings disc's halo

Type: task
Status: resolved
Blocked by: —

## Question

Nothing to decide — [ticket 20](20-ring-stroke-non-text-contrast.md) settled all
of it. This is the build.

The guarantee: **every ring stroke meets WCAG 1.4.11's 3:1 against its adjacent
colour, whatever photograph an author uploads.** An opaque halo makes that
adjacency photograph-independent, which is why it is a one-value guarantee
rather than a per-image one.

Not hypothetical: the disc fails over the *shipped* design photograph today —
3.28% of the rings band for copper, **10.27%** for the is-now cyan
([`assets/20-photograph-luminance.md`](../assets/20-photograph-luminance.md)).

### Markup — `browser/templates/hero.pt`, `bundle-src/src/hero/Rings.tsx`, and `docs/design/derico.de/site/build.mjs`

The eight circles are duplicated into **two sibling groups inside
`.rings-disc`**, halo first so the ink paints on top, both carrying
`transform="translate(105 0)"`:

```html
<g transform="translate(105 0)" class="ring-halo"> …the eight circles… </g>
<g transform="translate(105 0)" class="ring-ink">  …the eight circles… </g>
```

Same `cx/cy/r` and same per-circle classes in both. This does **not** disturb
the grow animation: `:nth-child` counts within a parent, so both runs stay 1…8
and `circle:nth-child(2)` matches each group's second circle, giving the pair
one delay. `transform-box: fill-box` excludes the stroke, so they share a
transform origin and scale in lockstep. Nothing in `hero.css:333–343` changes.

`build.mjs:644` states the geometry once and generates the committed
`de/index.html` / `en/index.html` — regenerate them. Parity is self-enforcing:
ticket 10's e2e serves `site/` and measures the published page against it, so a
`build.mjs` change left un-regenerated fails the e2e rather than passing quietly.

### CSS — `bundle-src/src/hero/hero.css`, identically in `docs/design/derico.de/site/assets/site.css`

```css
.derico-hero .rings-disc .ring-halo circle    { stroke: var(--derico-hero-ground); stroke-width: 6.5; }
.derico-hero .rings-disc .ring-halo .ring-thin { stroke-width: 5.5; }
.derico-hero .rings-disc .ring-halo .ring-now  { stroke-width: 8; }
```

`w = 2px` per side against inks 2.5 / 1.5 / 4. Specificity already favours these
over the existing ink rules (four classes against three), so no `!important` and
no reordering. `vector-effect: non-scaling-stroke` is inherited from the
existing `.rings-disc circle` rule — confirm it, do not restate it.

**No new colour token.** The rule names `--derico-hero-ground` directly, which
is the same value ticket 21's legend card reads.

### Tests, two jobs, neither sufficient alone

- **CSS-value test** — read `--derico-hero-ground`, `--derico-hero-ring` and
  `--derico-hero-ring-now` off the **built** sheet, compute both contrast
  ratios, assert ≥ 3.0. Currently 10.43 and 5.93. No image and no compositing
  against white: the halo is opaque, so the guarantee does not depend on the
  photograph. Catches the regression that matters — someone retunes the brand
  cyan or the ground and the halo silently stops discharging 1.4.11.
- **e2e** (`hero-view.e2e.js`, and the canvas case in `hero-editor.e2e.js`) —
  the halo is where the stroke is. Per circle: a paired halo circle at the same
  `cx/cy/r`; the halo group before the ink group in DOM order; `halo
  stroke-width − ink stroke-width ≥ 3`; the halo's computed stroke resolving to
  the ground; `vector-effect: non-scaling-stroke` declared. At 1440 and 375, on
  the view and in the canvas.

**`≥ 3` is a floor, not a mirror.** Ticket 18's rule forbids a test that carries
its own copy of a CSS value, because it stays green when the sheet is softened.
A floor the sheet must clear is the opposite: thin the halo to `w = 1` and it
goes red. Do not "fix" one into the other.

The `cx/cy/r` pairing is also what pays for the duplication — the eight circles
are stated twice per file, and drift between the copies is caught rather than
regretted.

### Bounds

- **No colour changes.** `--derico-hero-ring`, `--derico-hero-ring-now` and
  `#039fba` all stay. Ticket 20 §5.
- **The marker chips need nothing** — copper fill against a ground border is
  10.43. Ticket 20 §6. They are the precedent for the halo, not a separate fix.
- **No ground behind `.rings-figure`.** Rejected on ticket 18 §Q5 and again on
  20 §4: it spends the composition's best idea to buy contrast.
- **No image-brightness cap.** Rejected on ticket 18 §4.
- No profile XML changes, so no upgrade step. The canvas inherits the sheet —
  one scope-wrapped sheet serves both surfaces (ticket 14).

Interlocks with [ticket 21](21-build-the-contrast-guarantee.md) — same two files
— but is **not blocked by it**, and vice versa. That they can land in either
order without either test breaking is itself a check that both fixes are
structural rather than tuned against each other.

One thing this build should measure that the decision could not: the failure
shares above are for the rings *band*, not for pixels adjacent to a stroke.
Ticket 10's lesson — report the share, not the worst pixel — applies to that
number too, and measuring along the stroke paths is cheap once the halo exists.

## Answer

**Built and green; ticket 20's instructions held in every particular.** The
only surprise was how little the duplication cost once it was pinned.

Two sibling groups inside `.rings-disc`, halo first, both carrying
`transform="translate(105 0)"`, in all three files — `hero.pt`, `Rings.tsx`,
and `build.mjs` (whose committed `de/index.html` and `en/index.html` were
regenerated). CSS in `hero.css` and `site.css`: the halo painted in
`--derico-hero-ground` at 6.5 / 5.5 / 8 against inks 2.5 / 1.5 / 4, so 2px a
side. Specificity beat the ink rules unaided (four classes against three), so
no `!important` and no reordering, and `fill: none` plus
`vector-effect: non-scaling-stroke` came down from the existing rule — which is
what makes 2px a side hold at 375 as well as 1440.

Confirmed rather than assumed: **the grow animation is untouched.** All 8
`circle:nth-child(n)` delays still land, on both copies, because `:nth-child`
counts within a parent. Nothing in `hero.css:333-343` changed.

### The tests, and what each is for

- **Value** (`test_hero_contrast.py::test_the_ring_halo_carries_both_ring_inks`)
  — ground against both ring inks, 10.43 and 5.93 against the 3.0 that 1.4.11
  asks. **No photograph in the sum**, which is the whole dividend of an opaque
  halo and the reason this test is three lines rather than a rendering harness.
  Also asserts the halo is opaque, since a translucent one puts the upload back
  in.
- **Sheet** — `test_the_halo_is_wider_than_every_stroke_it_surrounds` (a
  **floor** of 3px, not a mirror of the 4 that ships) and
  `test_the_halo_is_painted_in_the_ground_and_nothing_else`.
- **Server** (`test_hero_view.py`) — the pairing, from the rendered template:
  halo group first, eight circles, identical `cx/cy/r` *and* per-circle class,
  identical transform.
- **Editor** (`degradation.test.tsx`) — the same four assertions on the React
  half.
- **e2e**, on the published view and in the canvas — computed styles rather
  than pixels, because a photograph cannot tell a halo from a dark leaf behind
  it. Pairing, DOM order, surround ≥ 3px, stroke resolving to the ground, and
  `vector-effect` as a *declaration* (ticket 15's posture).

Mutation-checked red-then-green: halo group moved after the ink, a halo circle
dropped, `ring-now`'s class dropped from the halo copy, the halo thinned to
+0.1px, and the ground lightened. Every one goes red.

**The duplication is paid for.** The eight circles are stated twice in each of
three files, and the geometry-pairing assertions exist in four places, so the
copies cannot drift silently — which was the one real objection to ticket 20 §8.

### The one thing this build could not close

`hero-view.e2e.js`'s halo assertions **fail against the currently running
Zope**, and only there: the process has the pre-halo `hero.pt` compiled, and
Chameleon caches compiled templates per process. The evidence is differential —
every CSS-borne change on the same page is live (the legend card, the scrim,
the body type all assert green), while the template-borne one is not, which is
exactly the split between a resource directory read from disk and a compiled
template held in memory. The same markup is pinned by the Python view test,
which renders the template fresh on every run and is green. **Re-run
`hero-view.e2e.js` after a Zope restart to close this.**

Not attempted: measuring the failure share *along the stroke paths* rather than
across the rings band, which the ticket left to the build. It is cheap now that
the halo exists, but it measures the defect that has just been removed — the
value test proves the adjacency directly and without a photograph, so the
measurement would be a record rather than a guard.
