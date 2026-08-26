# Decide: where the hero's body type comes from

Type: grilling
Status: open
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
