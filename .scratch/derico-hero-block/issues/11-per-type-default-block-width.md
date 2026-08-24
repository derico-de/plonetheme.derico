# Decide and build: how a brand block fixes its own width without offering the author a choice

Type: task
Status: open
Blocked by: —

## Question

Settled at charting: the Derico Hero is full-bleed, via `blockWidth: full`, whose
breakout Blicca already implements on both surfaces (`blocks_view.css:729`,
`wrapper/src/styles/index.css:34`). What does not exist is any way for a block to
*declare* that width, so a freshly inserted hero comes out at `default` (940px)
and an administrator has to pick Full Width from the block toolbar by hand —
precisely the author-facing option brand blocks are not supposed to have.

Neither half can express a per-`@type` default today:

- Server: `block_width_for` (`plate.py:113`) falls back on
  `DEFAULT_BLOCK_WIDTHS.get(node_type, ...)`, and `node_type` is `ploneBlock` for
  every Aurora block — the `@type` never reaches the lookup.
- Editor: `getBlockWidthConfig` (`block-width-plugin.ts:94`) reads
  `plateBlocksConfig?.[element.type]?.blockWidth` — same `element.type`, same
  blind spot.

Decide:

- **Where the declaration lives.** A field on the `blocksConfig` entry the block
  already writes in `install()` is the natural home, and costs the author
  nothing. Check first whether Aurora reads such a field already before adding a
  Blicca-side one — the mirror rule says adopt upstream's spelling if it exists.
- **Both halves agreeing.** Whatever the editor honours at insert time, the
  server renderer must reach the same verdict for a node that carries no explicit
  `blockWidth`. Two code paths, one answer, or published pages drift from the
  canvas.
- **Explicit versus default.** Does the declared width become a hard override, or
  only the value used when the node carries none? A node saved before the
  declaration existed, or one whose width an admin changed on purpose, must have
  a predictable outcome.
- **Suppressing the control.** A fixed-width block should not show a width picker
  at all. Find out whether the toolbar can be filtered per `@type` — and if it
  cannot without forking editor behaviour, say so and accept the picker as a
  cosmetic wart rather than build ahead of Aurora (ADR 0008).
- **Generality.** This is a brand-block need, not a hero need. Whatever lands
  serves every future brand block, and gets a line in the contract spec.

Lands in `plone.blicca.auroraeditor` alongside ticket 03.
