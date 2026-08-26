# Decide: how the rings disc meets WCAG 1.4.11 over the photograph

Type: grilling
Status: open
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
