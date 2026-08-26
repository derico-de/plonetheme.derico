# Decide: where the hero's body type comes from

Type: grilling
Status: resolved
Blocked by: —

## Question

On the published page the hero's body text is set in the browser's generic
sans, not in the theme's font. Measured on the sandbox site by
[ticket 10](10-verify-end-to-end.md), at all four viewports:

| | mockup | published hero |
| --- | --- | --- |
| `font-family` | `"Source Sans 3", system-ui, sans-serif` | `ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", …` |
| `line-height` on the block root | 1.65 (26.4px) | 1.6 (25.6px) |

Both come from **Blicca**, not from this theme and not from the block:
`blocks_view.css` states a Tailwind font stack and
`--aurora-content-line-height` on `.aurora-blocks-view`, deliberately, so that
the published page matches the *editing canvas* — where Aurora's own preflight
sets exactly that stack. The hero declares a `font-family` only for its two
display elements (`--derico-font-display` → Literata, which is correct on both
surfaces and matches the mockup to the pixel); everything else inherits, and
what it inherits is Blicca's parity default rather than `body`'s Source Sans 3.

So the block is *internally* consistent — canvas and view agree with each
other — and both disagree with the design. Everything else about the type
already matches: sizes, the headline ramp and its `-0.02em` tracking, the 15px
label floor, the grid tracks (ticket 10's numbers).

What to settle:

1. **Whose seam is this?** The theme's (state the body font on `.derico-hero`
   from a new `--derico-font-body` alias, the way §3 already publishes
   `--derico-font-display`), or Blicca's (a blocks view should not impose a
   font family on a host theme at all — but changing that moves every block on
   every site, and the canvas/view parity it buys is real)?
2. **The leading with it, or not?** 1.6 vs 1.65 is the whole of the ring
   legend's height difference (291px against the mockup's 330 at 1440). If the
   family moves and the leading does not, the hero stays a mockup-mismatch in
   a less obvious way.
3. **Does the canvas follow?** A block sheet is one scope-wrapped file serving
   both surfaces, so it will. Confirm that is wanted: the canvas would then
   render the hero in brand type while the blocks around it stay in Aurora's.
4. Ticket 14 §9's guard is binding — a block sheet may never name `--clara-*`,
   which is why the alias exists. Whatever is decided goes through
   `derico.css` §3 and gets the same test treatment.

Not in question: the display font, the type sizes, or the ramp. Those are
measured correct.

## Answer

**Neither seam the ticket offered. The hero states its own body type from the
public `--plone-*` ladder — one declaration pair in its own sheet, no theme
change and no Blicca change.** Grilled with md@derico.de, 2026-08-26.

### The fact that removed the choice

The ticket assumed a body font needs a `--derico-font-body` alias, "the way §3
already publishes `--derico-font-display`". But §3's stated reason for those
three aliases is that they *carry no `--plone-*` equivalent* and so cannot be
reached through the public ladder. The body font has one, and so does its
leading — both already carrying the mockup's exact values:

| | Clara `:root` (`clara.min.css`) | mockup (`site.css:74`, `:132`) |
| --- | --- | --- |
| `--plone-font-body` | `"Source Sans 3", system-ui, sans-serif` | `--font-body`, identical |
| `--plone-leading-body` | `1.65` | `body { line-height: 1.65 }`, identical |

Ticket 06 §3 permits a block sheet to speak `--derico-*` and `--plone-*`. Both
tokens are on the permitted side, so §3 gains no fourth alias and `derico.css`
is not touched at all. Clara declares both in `:root` (the `@layer tokens`
defaults beneath them are `system-ui` / `1.55`), so the values inherit to every
surface the theme is loaded on — which includes `@@aurora-edit`, since it
renders through `main_template`.

Incidental property worth keeping: a hero installed without Clara degrades to
the Plone default stack rather than to nothing.

### Q1 — the seam is the block's own sheet

Blicca states the Tailwind stack on `.aurora-blocks-view` **only**
(`blocks_view.css:101`) — the published page. In the canvas the same stack
arrives from Aurora's own `@scope`'d remote preflight. That is deliberate and
it is what buys the canvas/view parity the ticket credits Blicca with.

It also kills the theme-layer option outright. A rule in `derico.css` reaching
`.aurora-blocks-view` fixes the **view only**; the canvas keeps Tailwind sans
and the parity the block currently has — wrong on both surfaces, but equally —
is destroyed. The theme layer cannot reach the canvas the way the ticket
imagined, so option 1's "state it on `.derico-hero` from the theme" was never
the same rule as option 1's premise.

The block sheet has no such problem: packaging wraps it in
`@scope (.aurora-editor, .aurora-editor-portal, .aurora-blocks-view)`, three
roots, so one declaration lands on both surfaces **by construction**. Parity is
not maintained here, it is structural.

Blicca (option 2) remains the correct fix *in principle* — a blocks view should
not impose a family on a host theme — but it moves every block on every Blicca
site to buy one block on one site its design font, and the parity it currently
provides is real. Blicca's call under the mirror rule, not this map's. Noted in
the fog entry below rather than filed here.

### Q2 — the leading moves with the family

`line-height: var(--plone-leading-body)` in the same declaration pair. 1.6 →
1.65 is the whole of the ring legend's 291px-against-330 height gap at 1440;
moving the family without the leading leaves the hero a mockup-mismatch in a
less visible way, which is worse than leaving it alone because it reads as
fixed.

It moves which pixels every glyph covers, which
[ticket 21](21-build-the-contrast-guarantee.md) measures. That is not a
conflict: 21 states its guarantee is order-independent by construction, and
17 landing before or after it is precisely the check of that claim. **Neither
ticket blocks the other, in either direction.**

### Q3 — the rest of the site's blocks are fog, not this map's work

Every other block on derico.de — text, teaser, listing — has the identical
defect, wider. But the Destination is the Derico Hero built and working, and
site-wide block typography is not on the route to it. It goes to the map's
**Not yet specified**, not to a ticket and not out of scope: it is genuinely in
scope for derico.de, and its sharp form (theme rule, Blicca change, or both
surfaces separately) depends on the Blicca conversation above, which has not
happened. That is the fog test exactly — the question is real, its phrasing is
not yet available.

### Q4 — three assertions, and the third is the point

- **CSS-value test** — parse the built `static-blocks/blocks.css`, assert
  `.derico-hero` names `var(--plone-font-body)` and `var(--plone-leading-body)`.
  Catches a hardcoded `"Source Sans 3"`, which would pass every visual check
  while silently dropping the theme seam, and catches the leading being dropped
  on its own.
- **e2e, published view** — computed `font-family` on a hero body element
  resolves to a stack beginning `"Source Sans 3"`, computed `line-height` is
  1.65em. This is the assertion that would have caught what
  [ticket 10](10-verify-end-to-end.md) found by measurement.
- **e2e, canvas** — the same two assertions inside `@@aurora-edit`. Parity is
  the entire justification for choosing the block sheet over the theme layer,
  so it is pinned rather than assumed. This is the one that would otherwise be
  skipped.

No profile XML changes, so no upgrade step.

### Built by

[Ticket 22](22-build-hero-body-type.md) — kept separate from 21 rather than
folded into it, even though both touch `hero.css` and `hero-view.e2e.js`.
Merging them would destroy 21's designed order-independence check.
