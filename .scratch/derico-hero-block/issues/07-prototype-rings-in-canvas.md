# Prototype: does the rings figure survive inside the editing canvas?

Type: prototype
Status: open
Blocked by: 06

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
