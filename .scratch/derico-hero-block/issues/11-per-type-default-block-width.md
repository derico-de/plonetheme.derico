# Decide and build: how a brand block fixes its own width without offering the author a choice

Type: task
Status: closed
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

## Answer

**Nothing needed building. Aurora already implements this, and Blicca already
composes it — the ticket's premises were wrong on both halves.** The whole
mechanism is one key in the theme's own `install()`, which is ticket 08's line
to write. What landed here is the contract amendment that says so.

### The declaration: `defaultBlockWidth`, upstream's own spelling

The ticket read `block-width-plugin.ts` and found the `element.type` blind spot
correctly — but a **second** plugin covers exactly the case that one skips.
`@plone/plate`'s `style-fields-plugin.ts:67` resolves a ploneBlock's width as:

```ts
blockWidth: styleFields.blockWidth ?? {
  defaultValue: currentBlockConfig?.defaultBlockWidth ?? DEFAULT_BLOCK_WIDTH,
}
```

where `currentBlockConfig` is `config.blocks.blocksConfig[element['@type']]` —
the ploneBlock space, keyed by `@type`, which is where a block add-on's
`install()` already writes. Upstream ships tests named *"uses
`defaultBlockWidth` for ploneBlock nodes without schema style fields"* and
*"adds configured `defaultBlockWidth` when creating ploneBlock nodes…"*.
`@plone/types` declares the field (`Blocks.d.ts:149`) and its CHANGELOG records
it **replacing** a legacy `blockWidth` config field, so it is the current
spelling, not a stub.

So the mirror rule is satisfied by adoption, not invention: **no Blicca-side
field, no `plateBlocksConfig` entry, no new record key.** `StyleFieldsKit` is
already composed in `plugin-kit.tsx:180`, so the machinery is live today.

The ticket's "Lands in `plone.blicca.auroraeditor` alongside ticket 03" is
wrong. Only the docs land here; the behaviour lands in the theme.

### Both halves agree, because the editor writes the value into the data

`setStyleFieldValue` with no `path` sets `data.blockWidth = 'full'` at the
node's top level (`@plone/helpers` `dist/index.js:686`), driven by
`editor.api.create.block` and `insertNodes` at insert time and by
`normalizeInitialValue` on load. That is exactly the key `block_width_for`
reads (`plate.py:115`).

So the server needs **no change at all**: it sees an explicit width, not a
default. Both existing behaviours are already pinned by tests —
`test_plone_block_honors_explicit_width` and
`test_plone_block_defaults_to_default_width` in `test_rendering_plate.py`. No
new test was warranted.

**Chosen over** adding a `default_block_width` field to `IAuroraBlockAddon` so
the server could reach the verdict independently. That buys independence by
declaring the width **twice** — once in JS `install()`, once in the record —
which is the drift the ticket's "two code paths, one answer" was trying to
prevent, and nothing in this map authors heroes outside `@@aurora-edit`.
Also rejected: emitting the breakout from the block's own server view, which
would reimplement the full-bleed the map says the block "inherits and
reimplements none of".

**Accepted limit, written into the contract:** a node created through the REST
API, a migration, or a Python test fixture carries no `blockWidth` and renders
at `default`. Editor-authored content is unaffected.

### Suppressing the control: already done by ticket 02

No toolbar filtering, no fork, nothing to build. Omitting `blockWidth` from
`blockSchema` **is** the "without schema style fields" branch that triggers the
fallback — and ticket 02 already decided the hero has no `blockWidth` key. The
sidebar form is generated from the schema, so the control is absent by
construction. Declaring both would be self-defeating: a schema field marked
`styleField: true` wins over `defaultBlockWidth` and hands the author back the
control the block meant to withhold. That trap is now §1.4 rule 1.

### Default, not override

Aurora fills the declared width in only when the node's `blockWidth` is absent
or not an allowed value, and leaves any other valid value alone. Left as-is.
Forcing it would mean re-implementing `applyStyleFieldDefaultsInData` in Blicca
to win over upstream's — building ahead of Aurora (ADR 0008) for a state no
supported path can reach, since the schema has no width field and the toolbar
picker is inert. A stray value would be a data bug, and an override would hide
it rather than expose it.

### The inert toolbar picker — Aurora's wart, not ours

`BlockWidthToolbarButton` is in the `BlockFloatingToolbarButtons` preset Blicca
installs (`plugin-kit.tsx:52`) and it *renders* for ploneBlocks —
`getBlockWidthConfig` returns `{}` for `PLONE_BLOCK_TYPE`, so it offers all four
widths. But `setBlockWidth`'s `matchesValue` excludes `PLONE_BLOCK_TYPE`, so
`setNodes` matches nothing and **every option is inert**. Pre-existing; affects
the native image, teaser and listing blocks equally.

Not fixed here: it belongs to every ploneBlock, not to the Derico Hero, and
fixing it would smuggle a Blicca-wide UI change into a brand-block ticket. Ruled
[out of scope](../map.md#out-of-scope) as Blicca's to file. Noted in §1.4.

*Unverified:* whether the floating toolbar appears at all for a **void**
selected ploneBlock. If it does not, the wart is invisible and the follow-up is
moot — worth one minute of ticket 10's e2e time to settle.

### Built

- Contract [§1.4 "Fixing a block's width"](../../../plone.blicca.auroraeditor/docs/design/aurora-block-addon-contract.md)
  — the declaration, the two rules that make it work, default-not-override,
  how it reaches the server, the known limit, and the toolbar wart. Generic to
  every brand block, as the ticket asked.
- The `defaultBlockWidth` row in §1's field table, which shipped with an empty
  Notes cell.
- `news/44.feature` in Blicca, per the convention `43.feature` set for a
  docs-only contract amendment.
- Ticket 08 gains `defaultBlockWidth: 'full'` and the schema-field trap;
  ticket 09 gains an explicit "do not touch `DEFAULT_BLOCK_WIDTHS`".

Changes are uncommitted in `plone.blicca.auroraeditor`.
