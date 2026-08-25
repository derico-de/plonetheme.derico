# Prototype: does the rings figure survive inside the editing canvas?

Type: prototype
Status: closed
Blocked by: 06
Assignee: md@derico.de

## Question

The rings figure was designed for a full-bleed hero and verified at 1440 / 900 /
375 / 320px as a standalone page. Inside `@@aurora-edit` it renders in a
narrower canvas, with the editor's own chrome around it, at a scale nobody has
looked at.

Build the cheapest thing that shows the truth — the extracted CSS from 06 plus
the mockup's markup, dropped into the editing canvas — and look at:

- Whether the rings disc and its markers stay legible at canvas width, and
  whether the legend stays above the 15px floor.
- Whether the full-bleed breakout really lands identically in the editor and on
  the public view. The two rules are written separately (`blocks_view.css:729`
  and `wrapper/src/styles/index.css:34`) against different boxes — the `.block`
  and the `.block-inner-container` — and the canvas carries a 24px drag-handle
  gutter the public column only mimics. Trust the pixels, not the comment.
- Whether the block needs a distinct **editor rendering** — a reduced or scaled
  hero — and if so, how far it can diverge before editing stops being WYSIWYG.

The output is a judgement to react to, not code to keep. Link what you build
into `../assets/`.

## Prototype

Built ahead of the looking, so the session with the server running is spent on
pixels rather than on extraction:

- [`assets/07-hero-probe.css`](../assets/07-hero-probe.css) — the CSS ticket 06
  decided, extracted from the mockup and transformed by its decisions
  (`--derico-hero-*` palette on the block, `.shell` folded into
  `.home-hero__grid`, container query at 56rem, animations public-view-only,
  prefixed keyframes). Carries a clearly marked **ticket 14 stub** for the four
  `--derico-text-*` aliases that do not exist yet.
- [`assets/07-hero-probe.js`](../assets/07-hero-probe.js) — injects that sheet
  plus the mockup's markup into a live `@@aurora-edit` or blocks-view page,
  building the block anatomy each surface actually emits, and returns the
  measurements. `dericoHeroProbe.measure()` reports the two breakout boxes, the
  grid columns, the disc width and the legend's computed caption size.

**A question the probe was built to settle, surfaced while building it.**
Ticket 06 left open which element the hero paints on, and the two surfaces do
not agree by construction. `plate.py:346` stamps
`block block-derico-hero has--block-width--full` on the block **wrapper** and
`blocks_view.css:733` breaks that same element out — so on the public view the
wrapper is the hero's box. In the canvas the breakout lands one level in, on
`.has--block-width--full > .block-inner-container`
(`wrapper/src/styles/index.css:31`). If the hero paints on the wrapper on both
surfaces, the canvas paints the dark ground and the wash at **column** width
while the image and grid inside break out past it. Hence `heroOn:
'wrapper' | 'section'` — run both and let the pixels choose.


## Answer

Measured in a live `@@aurora-edit` and on the live blocks view of the same
`Article`, same session, same sheet — the probe CSS put through the **real**
`scope-wrap.ts` transform, so it is scoped exactly as packaging would scope it.
(Injected unscoped first, which is wrong: `@scope` proximity outranks
specificity in the cascade, so an unscoped block sheet loses to Aurora's scoped
preflight and every token silently died. That reading was a probe artifact, not
a finding.)

**The rings survive. Nothing about them needs an editor rendering.** At a 1440
viewport with the toolbar expanded the canvas hero is 1220px and the disc is
527px; markers stay 28px with 15px numerals, legend titles 16px, captions
**15px — Clara's `--clara-text-label` floor exactly, never under it**. At 375
the hero is 315px, the disc 314px, markers still 28px, captions still 15px: the
legend is HTML beneath the SVG, so it does not scale with the graphic and the
type floor holds by construction. No reduced or scaled hero is needed, and the
question of how far a distinct editor rendering could diverge does not arise.

**The full-bleed breakout does NOT land identically — because `.block-derico-hero`
is the wrong element to paint on.** Measured at 1440, toolbar expanded:

| | public view | canvas |
|---|---|---|
| `.block.block-derico-hero.has--block-width--full` | **1220 @220** | 1134.9 @262.5 |
| `.block-inner-container` | — | **1220 @220** |

Aurora's anatomy stamps `block-<@type>` on the **wrapper** on both surfaces
(`plate.py:346` mirrors it server-side), but the breakout lands on the wrapper
on the view (`blocks_view.css:733`) and one level in, on the inner container, in
the canvas (`wrapper/src/styles/index.css:31`). So painting the hero on
`.block-derico-hero` gives a canvas hero 1134.9px wide whose `overflow: hidden`
**clips the 1220px inner container inside it** — no breakout at all in the
editor, dark ground stopping at the column edge
([07-canvas-1440-heroOn-wrapper.png](../assets/07-canvas-1440-heroOn-wrapper.png)).
Give the component its own root element instead and both surfaces measure
**1220 @220**, identical to the pixel.

- **Corrects 06 §2 and §4.** The block's hook is its own class on its own
  element — `.derico-hero` on the `<section>` the component and the server view
  both emit — and every selector descends from **that**, not from
  `.block-derico-hero`. The `.block-derico-hero` stamp stays free for
  `derico.css`'s chrome-suppression rule (06 §1), which wants the wrapper anyway.
- The rule "the hero must never set its own `width`" (06 Consequences) survives
  unchanged and is now measured rather than reasoned.

**`isolation: isolate` has to come back — 06 §8 is wrong on the mechanism.**
Chrome computes `contain: none` for `container-type: inline-size`, and
`position: relative; z-index: auto` is no stacking context either. With none,
`.hero-media { z-index: -2 }` escapes to the **root** stacking context and the
hero's own opaque `--derico-hero-ground` paints straight over it: **the
photograph vanishes on both surfaces**, leaving a flat dark panel that looks
deliberate. Isolated by toggling one thing at a time — ground off + wash off →
forest ([07-canvas-image-check.png](../assets/07-canvas-image-check.png)); wash
off, ground on → flat dark
([07-view-wash-off-ground-on.png](../assets/07-view-wash-off-ground-on.png));
`isolation: isolate` restored, wash on → the mockup composition
([07-view-isolate-restored.png](../assets/07-view-isolate-restored.png)).
`contain: layout` never arrived, so the mockup's `isolation: isolate` does not
drop out of the sheet. The container query itself is untouched by this.

**Two editable-inherited text properties leak into the block, and both change
what the author sees.** The Plate editable computes `white-space: pre-wrap` and
`overflow-wrap: break-word`, and both inherit into anything rendered inside it.

- `pre-wrap` turns every newline **between** two elements into a real line box.
  With the mockup's indented markup the rings figure measured **1165px** against
  the view's 690, and the legend **519** against 291 — three quarters of the
  inflation was the probe's own indentation. Stripping whitespace-only text
  nodes brought the canvas to figure **661** / legend **279** / stage **364**,
  against the view's 690 / 291 / 364. JSX drops inter-element whitespace, so the
  editor half is safe by construction — but a `dangerouslySetInnerHTML` preview
  or any server-rendered fragment placed in the canvas is not.
- `break-word` breaks the headline **mid-token**: at 1440 the canvas gives
  "Anwendungen" / ", die bleiben." where the view gives "Anwendungen," / "die
  bleiben." — same width, same 80px Literata, two different wraps. Setting
  `overflow-wrap: normal` on the hero reproduces the view's wrap exactly. Safe
  to set, because ticket 02 put every text field in the **sidebar**: the canvas
  copy is a preview, not a contenteditable region.

**06 §8's container query is vindicated by measurement.** At a 900px viewport
with the toolbar expanded the canvas hero is 680px = **42.5rem**, so the grid
correctly stays single-column; a viewport media query would have fired at 896px
and forced `minmax(24rem, …)` into a 680px box. No horizontal scroll at 1440,
900, 375 or 320 on either surface. **56rem needs no moving** — the threshold is
read off the hero's own box, which is the same box on both surfaces.

**The canvas is narrower than the view by exactly the toolbar, and at mobile
that is proportionally large** — 315px vs 375 (−16%), 260px vs 320 (−19%). At
320 the headline's longest token overflows its column and is clipped by
`overflow: hidden` (h1 line 309px against a 228px column, 65px past the hero's
edge). **This is inherited, not caused by the canvas**: the mockup served
standalone at 320 does the same thing — h1 line 320px against a 288px shell,
16px past the hero's right edge, clipped. A defect in the design source that the
canvas amplifies. Handed to [ticket 15](15-headline-at-320.md) rather than
decided here.

Assets: [`07-hero-probe.css`](../assets/07-hero-probe.css) (carries the
`isolation` correction, marked), [`07-hero-probe.scoped.css`](../assets/07-hero-probe.scoped.css)
(the same sheet through the real transform),
[`07-hero-probe.js`](../assets/07-hero-probe.js),
[canvas at 1440](../assets/07-canvas-1440-final.png),
[canvas at 375](../assets/07-canvas-375.png),
[public view at 1440](../assets/07-view-1440.png).

Fixture left behind on the sandbox site: `plonetheme.derico` installed on
`/Plone`, and `/Plone/hero-probe-article` (an `Article`, so it carries
`volto.blocks` and the blocks view without touching the `Document` FTI).
