# Build: the hero's contrast guarantee

Type: task
Status: open
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
