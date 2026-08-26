# Decide: how the rings disc meets WCAG 1.4.11 over the photograph

Type: grilling
Status: resolved
Blocked by: —

## Question

The rings disc is drawn straight onto the photograph with no ground, and its
strokes miss the 3:1 that WCAG 1.4.11 asks of meaningful non-text graphics.
Worst case — a bright photograph, the backdrop an author can upload at any
time:

| stroke | needs | bare photograph | under the 0.72 wash |
| --- | --- | --- | --- |
| copper (`--derico-hero-ring`) | 3.0 | 1.79 | 1.75 |
| is-now (`--derico-hero-ring-now`, brand cyan) | 3.0 | 3.15 | **1.00** |

The marker chips are unaffected — they are opaque discs with the ground as
their border and text colour, so they carry their own backdrop already.

Surfaced twice while grilling [ticket 18](18-legend-contrast-over-the-photograph.md)
and parked both times, deliberately: the remedy for a stroke is stroke width
and a halo, not a ground, and folding it in would have turned one decision into
two. Ticket 18's decision **not** to cap the image brightness means nothing
there incidentally fixes this — the strokes get no help from the legend card or
the copy scrim, neither of which is anywhere near them.

What to settle:

1. **Whether 1.4.11 binds here at all.** The disc is `role="img"` with an
   `aria-label`, and the legend beneath restates every entry in text. If the
   graphic is decorative-with-a-text-equivalent rather than "required to
   understand the content", the criterion does not apply and this closes as
   out of scope. That is the first question, not the last.
2. **If it binds, what changes** — a halo (a second stroke in the ground
   colour beneath each circle), heavier `stroke-width`, a `filter: drop-shadow`
   on the disc, or a ground behind the whole `.rings-figure`. Ticket 18 §Q5
   rejected the last of these for the legend's sake, on the grounds that it
   spends the hero's best visual idea — the disc floating on the forest — to
   buy contrast. That reasoning still applies.
3. **Whether `vector-effect: non-scaling-stroke` complicates it.** The strokes
   are 2.5 / 1.5 / 4 and do not scale with the viewBox, so a halo has to hold
   at every rendered size, not just at 1440.
4. **What the test asserts.** Ticket 18 established the division: a CSS-value
   test proves the declared treatment is strong enough, an e2e proves the
   geometry puts it where it is needed. A stroke halo needs the second more
   than the first.

Not in question: the disc's geometry, the marker positions, or the ring
colours as brand — ticket 18 kept `#039fba` and there is no reason to reopen it
here.

## Answer

Grilled with md@derico.de, 2026-08-26. Measurements:
[`assets/20-photograph-luminance.md`](../assets/20-photograph-luminance.md).

### What the measurement changed before any of it was decided

The ticket's table listed two hypothetical backdrops. Measuring the photograph
the block actually ships with —
`hero-managed-forest-wide-2400.jpg`, the design source's image and the e2e
fixture's upload — moved the problem into the present tense:

| region | median Y | p99 | max | fails copper 3:1 | fails cyan 3:1 |
| --- | --- | --- | --- | --- | --- |
| whole image | 0.0153 | 0.567 | 0.998 | 7.37% | 16.25% |
| rings band | 0.0116 | 0.340 | 0.815 | 3.28% | **10.27%** |

The forest is dark at the median and its canopy gaps are not. **The disc fails
1.4.11 over the shipped design photograph today**, not only over some future
bright upload — and, against expectation, the existing fixture can therefore
demonstrate the fix, so no synthetic bright image is needed anywhere.

Re-deriving the arithmetic also showed the ticket's own worst case was too kind.
Copper (`Y = 0.5365`) passes only against `Y ≤ 0.1455` — the bright side would
need `Y ≥ 1.7095`, which does not exist, so copper can *only* pass over a dark
backdrop. Cyan (`Y = 0.2836`) passes only against `Y ≤ 0.0612` or `Y ≥ 0.9508`;
ticket 18's `3.15` was measured against pure white, which no photograph is.

### The decision

1. **1.4.11 binds.** The disc is `role="img"` with an `aria-label`, which is the
   block's own declaration that it means something. A decorative graphic is
   `aria-hidden="true"` — as the `<picture>` and the marker `<ol>` already are.
   Claiming the disc is content for screen-reader users and decoration for
   low-vision users is one graphic answering two ways, and that is not a
   conformance argument worth defending. The honest alternative was named and
   rejected: making it genuinely exempt costs the metaphor for AT users.

2. **Legibility is a goal independently of the criterion.** Answered before the
   remedy, so that "exempt" could not have quietly resolved to "ship it
   invisible". On the current CSS the homepage's signature graphic disappears
   into a mid-tone upload for everyone, not only for low-vision users. This
   makes §1 a question about how the answer is written down rather than about
   what gets built.

3. **The rule is hero-wide for non-text, discharged against an inventory** —
   the symmetry with ticket 18, which widened from the legend to every text
   element rather than fixing one. Inventory: the ring strokes (the work), the
   marker chips (§6), the CTA (a filled pill with `border: 0`, inside ticket
   21's copy scrim), and the legend's `border-top` hairline (decorative).

4. **The remedy is a halo, and `stroke-width` is arithmetically dead.** 1.4.11
   is a colour ratio; a 4px stroke and a 10px stroke have identical contrast.
   The ticket's option 2 dies on the same arithmetic that killed the wash on
   ticket 18. A ground behind the whole `.rings-figure` stays rejected on 18 §Q5
   — it spends the composition's best idea to buy contrast.

5. **The halo is opaque `--derico-hero-ground`, and that is forced.** To serve
   both inks it needs `Y ≤ 0.0612` (cyan's dark-side threshold); ground is
   `0.0062`, and ground beats both inks — **10.43** against copper, **5.93**
   against cyan. A *light* halo is dead: copper against `--derico-hero-ink` is
   **1.74**. A translucent one needs `α ≥ 0.7796` over a white photograph, which
   is indistinguishable from opaque while costing a token and compositing math.
   **No new colour token** — the rule names `--derico-hero-ground` directly,
   which is also what ticket 21's card will read.

   The load-bearing observation: **the marker chips already are this treatment.**
   A copper fill inside `border: 2px solid var(--derico-hero-ground)`. The halo
   is not a new idea in this block; it is the chip pattern applied to strokes.

6. **The marker chips need nothing, and that is recorded rather than assumed.**
   The ticket said they "carry their own backdrop already", which is a claim
   about the numerals (1.4.3) standing in for a claim about the silhouette
   (1.4.11). The two happen to agree — copper fill against ground border is
   **10.43** — but on the record, not by luck.

7. **A crisp halo, not a blurred one.** A stacked `filter: drop-shadow()` has no
   plateau to read, and ticket 18's CSS-value test exists precisely because a
   guarantee you cannot read off the sheet survives being softened. There is a
   mechanical objection too: `.rings-disc` carries `overflow: hidden` and needs
   it — the outer circle is `r 315` at `cy 234` in a `470`-tall viewBox, clipped
   on three sides by design — and a CSS filter paints *after* that clip.

8. **Drawn as a second `<g>` of ground-stroked circles**, before the ink group,
   both carrying `transform="translate(105 0)"`, each halo circle
   `vector-effect: non-scaling-stroke`. Chosen over a `feMorphology` outline
   filter, which keeps the geometry stated once but leaves **nothing to
   measure** — and §10 gave the e2e the job of proving the halo is where the
   stroke is. The `<use href>` variant was rejected separately: document CSS
   reaching into a use-element shadow tree is exactly the cross-browser
   fragility this map avoids, and an `id` in a template is a collision waiting
   for a second hero.

   **Correction to this ticket's premise, and to a warning raised while
   grilling it:** duplicating the circles does *not* break the grow animation.
   `:nth-child` counts within a parent and the circles already sit inside a
   `<g>`, so a second group leaves both index runs at 1…8 and
   `circle:nth-child(2)` matches the halo copy and the ink copy, giving them
   the same delay — which is the behaviour wanted. `transform-box: fill-box`
   excludes the stroke, so the paired circles share a transform origin and
   scale in lockstep. The cost of duplication is markup, not motion.

9. **`w = 2px` per side** — halo widths **6.5 / 5.5 / 8** against inks
   2.5 / 1.5 / 4. Two arguments converge: the marker chips' `border: 2px`
   (§5's precedent), and antialiasing — these are curved strokes whose outermost
   fraction of a pixel is always a blend, so at `w = 1px` the effective adjacent
   colour is not the halo at all. Accepted cost: where the halo is visible the
   thin ring reads as a 5.5px band rather than a 1.5px line, about 3.7x the
   apparent weight — but only over the bright 3–10% of the rings band, since
   over the forest proper (`Y = 0.0116` against ground's `0.0062`) the halo is
   indistinguishable from the photograph. `1.5px` is the fallback if the banding
   reads heavy against pixels; it still clears the antialiasing argument.

10. **The dashed `ring-future` is haloed too, uniformly.** Exempting it would
    re-open §1 on weaker grounds than the disc itself had, and a dashed ring
    that vanishes into a bright canopy is the same defect in miniature. It stays
    visually quiet because a wider *stroke* does not touch `stroke-dasharray` —
    the halo follows the dashes rather than filling the gaps. (This is also why
    the `feMorphology` route was worse than it looked: a dilate fattens dashes.)

11. **The design source gets the same change**, per ticket 18 §7. Its geometry
    lives once, in `build.mjs:644`, which generates the committed
    `de/index.html` and `en/index.html`. Parity here is self-enforcing rather
    than a promise: ticket 10's e2e serves `site/` and measures the published
    page against it, so a `build.mjs` change left un-regenerated fails the e2e.

### What the acceptance criterion becomes

An opaque halo makes the adjacency **photograph-independent** — the stroke's
neighbour is the halo, whatever the image — which is what lets the two tests
split as cleanly as they do.

- **CSS-value test**: read `--derico-hero-ground`, `--derico-hero-ring` and
  `--derico-hero-ring-now` off the *built* sheet, compute both ratios, assert
  ≥ 3.0 (currently 10.43 and 5.93). No image and no compositing against white.
  It catches the real regression: someone retunes the brand cyan or the ground
  and the halo silently stops discharging 1.4.11.
- **e2e**: each of the eight circles has a paired halo circle at the same
  `cx/cy/r`; the halo group precedes the ink group in DOM order; `halo
  stroke-width − ink stroke-width ≥ 3` per pair; the halo's computed stroke
  resolves to the ground; `vector-effect: non-scaling-stroke` is declared on the
  halo — the declaration, not the rendering, for ticket 15's reason. At 1440 and
  375, on the view **and** in the canvas.

**`≥ 3` is a floor, not a mirror.** Ticket 18's rule forbids a test carrying its
own copy of the CSS value, because such a test stays green when the sheet is
softened. A floor the sheet must clear is the opposite construction: thin the
halo to `w = 1` and it goes red. The two are easy to confuse and the build
ticket says which is in play.

The `cx/cy/r` pairing is also what pays for §8's duplication: the eight circles
are stated twice per file, but drift between the copies is caught rather than
merely regretted.

No profile XML changes, so no upgrade step. The canvas inherits the sheet
automatically — one scope-wrapped sheet serves both surfaces (ticket 14).

### What came out of it

- [Ticket 23](23-build-the-ring-halo.md) — building the above. Its own ticket
  rather than folded into [ticket 21](21-build-the-contrast-guarantee.md),
  following the 17 → 22 precedent: 21's guarantee is *text over a photograph via
  local grounds*, this one is *a graphic over a photograph via an outline*, and
  they share a file rather than a mechanism. Folding would also merge a markup
  change into a ticket that says it makes none. Unblocked by 21 for the reason
  21 was unblocked by 17 — a structural guarantee is order-independent, and that
  the two can land either way round is itself a check that neither was tuned
  against the other.
- **A glossary collision, fixed in `CONTEXT.md`.** **Hero wash** listed *scrim*
  among the words to avoid, and ticket 18 then named a new layer
  `--derico-hero-copy-scrim`. The avoidance was about not calling the wash a
  scrim, but left standing it reads as forbidding 18's own term. The two are now
  separate entries that point at each other, and **ring halo** was added
  alongside them.
