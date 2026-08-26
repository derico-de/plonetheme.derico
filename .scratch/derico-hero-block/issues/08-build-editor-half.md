# Build: the Derico Hero's editor half

Type: task
Status: closed
Assignee: md@derico.de
Blocked by: 14, 02, 04, 06, 11, 13, 15

## Question

With the content model (02), the workspace (04) and the CSS (06) settled, build
the JS half in `plonetheme.derico`.

- The workspace and Vite config from 04, producing committed artifacts under
  `src/plonetheme/derico/static/`.
- `install(config)` adding the `blocksConfig` entry — `id`, `title`, `icon`,
  `edit`, `view`, `blockSchema`, **`defaultBlockWidth: 'full'`** — and returning
  `config`. It must return the config object; the wrapper throws otherwise
  (`main.tsx:96`).
- **`defaultBlockWidth: 'full'` is the whole of the full-bleed wiring** (11).
  Aurora fills it into the node's `blockWidth` at insert, which is what both the
  canvas and the server renderer read. It works only while `blockSchema` has no
  `blockWidth` property — a schema style field wins over it, which is exactly
  what 02 already decided against. Contract §1.4.
- Both `edit` and `view` implemented, per the charting constraint.
- The scope-wrapped stylesheet emitted by the same build.
- Registration happens before `mount()`; the blocksConfig registry is not
  reactive (contract §1.3).

Tests as the code is written, per the repo's standing preference for real tests
over verification scripts.

## Corrections from ticket 07 (measured in the live canvas and view)

- **The component's root element carries its own class, `.derico-hero`, and
  every selector descends from that** — not from `.block-derico-hero`. Aurora's
  anatomy stamps `block-<@type>` on the block **wrapper**, which is the
  full-bleed box on the public view but only the column-width box in the canvas;
  painting the hero on it clips the breakout in the editor. Both halves must
  emit the same root element and the same class.
- **`isolation: isolate` stays in the sheet.** `container-type: inline-size` does
  not supply a stacking context, and without one the `z-index: -2` hero media
  falls behind the hero's own opaque ground and the photograph disappears.
- **The hero sets `white-space: normal`** so the canvas wraps its headline the
  way the public view does; the Plate editable computes `pre-wrap` /
  `break-word` and both inherit in. Safe because ticket 02 edits every text
  field in the sidebar. **`overflow-wrap: normal` is superseded by ticket 15** —
  the hero sets `break-word` deliberately, on both surfaces. 07 blamed
  break-word for the canvas's differing 1440 wrap; re-measured, all five
  configurations give the identical two lines at 1440, so the culprit was the
  co-inherited `pre-wrap` alone. Parity comes from *stating* the value, not
  from which value.
- **No whitespace-only text nodes in the canvas markup.** `white-space: pre-wrap`
  turns each one into a real line box; the mockup's indented HTML inflated the
  rings figure by 76%. JSX drops them, so this is a constraint on any
  `dangerouslySetInnerHTML` or server-rendered fragment, not on ordinary TSX.

See [ticket 07's answer](07-prototype-rings-in-canvas.md) for the measurements.

## Inherited from [ticket 14](14-theme-layer-changes.md)

Two guards land green-but-skipped today and start running the moment this
ticket emits its first `static-blocks/*.css`. Neither is a new decision — both
enforce 06 §3 — but both fail the build if the sheet is written without them
in mind:

- **The block sheet may never name a `--clara-*` token.** It speaks `--derico-*`
  and `--plone-*` only. `derico.css` §3 re-publishes the four Clara type tokens
  that have no `--plone-*` equivalent — `--derico-text-display`,
  `--derico-text-lede`, `--derico-text-label`, `--derico-font-display` — and is
  the theme's one seam onto Clara. Guard:
  `test_block_sheets_never_name_a_clara_token`.
- **All four aliases must actually be read** by a block sheet, or they are dead
  weight and get deleted rather than published. Guard:
  `test_published_aliases_reach_a_block_sheet`.

Also: no hand-written file may live in `static-blocks/` (04 §3, `emptyOutDir`),
and `css_tools.block_stylesheets()` globs `*.css` there — so the guards see
whatever the build emits, nothing else.

## Input from [ticket 15](15-headline-at-320.md) (2026-08-25)

The hero's text never clips, and the guarantee is a **layout** rule, not a type
rule. Four rungs, in the block's own sheet, every selector under `.derico-hero`:

1. `min-width: 0` on the hero's grid and flex items — copy cell, `.action-row`
   children, `.ring-legend` children. **This is the guarantee.** A grid or flex
   item floors at `min-content`, so without it the copy cell grows to the
   longest word (measured 320px inside a 288px shell at a 320 viewport) and the
   hero's `overflow: hidden` clips it.
2. `overflow-wrap: break-word` on headline, kicker, lede, legend `dt`/`dd` and
   both CTA labels. It does **not** feed intrinsic sizing, so it can never
   replace rung 1 — measured, break-word alone still blew the cell out.
3. `font-size: clamp(2.4rem, 1.4rem + 5cqi, 5rem)` on the h1 — **`cqi`, not
   `vw`**: the hero is viewport-minus-toolbar for every logged-in user on both
   surfaces. The block states the clamp itself; it must **not** override
   `--derico-text-display`, which is an alias (derico.css §3) and is read by
   Clara's `.clara-home-copy h1` too.
4. `hyphens: auto` — a labelled enhancement. It is a **no-op in this
   container's Chromium** (no dictionaries; `de` and `en` probes both failed to
   hyphenate), so a test may assert the declaration, never the rendering.
   `lang` is inherited from `main_template`; the block neither stamps it nor
   offers a field.

`max-width: 14.5ch` on the h1 stays as the mockup has it.

Measurements: [`assets/15-wrap-measurements.md`](../assets/15-wrap-measurements.md).
The design source now carries rungs 1, 2 and 4 plus the ramp (in `vw` — it has
no toolbar), so it can be read as the reference again.

## Answer

**Built and green**, in commit `71efe09` — the editor half exists, is served,
and is guarded. The build session ended before it wrote this record; the answer
below was reconstructed from the shipped code and re-verified: `pnpm typecheck`
clean, **27 vitest cases pass**, the theme's Python suite is **116 passed, 1
skipped** (the skip is the `block_api` floor, which has no record to read until
ticket 09), and a fresh `pnpm build` leaves `git diff --exit-code` over
`static-blocks/` clean.

Nothing in the ticket's instructions turned out to be wrong. Four things came
out of writing it that the ticket did not anticipate, and two of them amend
closed tickets.

### 1. The reference trim moved from the edit component into a widget — corrects ticket 02

Ticket 02 fixed the stored shape (`[{"@id": "../resolveuid/<uid>"}]`, bare) and
said the block's **edit component** would trim the enriched brain in its
`onChange` before calling `setBlock`. That is how Aurora's teaser does it — but
the teaser renders its browser **inside the canvas**. The hero edits every field
in the **sidebar**, and the sidebar writes straight onto the Plate node:
`SidebarAfterEditable`'s `onFormDataChange` calls `editor.tf.setNodes(patch)`
itself (`wrapper/src/editor/plone-block-sidebar.tsx`). The edit component is
never consulted and has **no interception point**, so a widget is the only seam
where the trim can happen.

So there are **three** namespaced widgets, not two: `derico_textarea`,
`derico_ring_legend` and a new **`derico_reference`**. The stored shape is
exactly what 02 decided; only the place that produces it moved.
`selectedItemAttrs` will not do the trim — Blicca's widget ignores the list and
always fetches the full contract field set.

A second field-naming rule came out of the same reading: **cmsui resolves a
widget by field id before it looks at `widget`**, so a field called `image`
would silently take the registered image widget. `image_wide` /
`image_portrait` are load-bearing names, not stylistic ones.

### 2. `scope-wrap` had to be `enforce: 'post'`, or the sheet shipped unwrapped

Vendoring the plugin (04 §7) was not enough. In **lib mode** Vite emits the
single `cssFileName` asset from `vite:css-post`, which runs *after* an
unenforced plugin's `generateBundle` — so the stylesheet went out with no scope
wrap at all and every token died against Aurora's scoped preflight. The wrapper
never hit this because its CSS arrives as code-split chunks.

The fix is one `enforce: 'post'` in `vite.config.ts`, spread onto the plugin at
the call site. **The vendored plugin code stays byte-identical to upstream** —
which is what `test_the_vendored_scope_wrap_still_matches_upstream` pins, and
the reason the fix went in the config rather than in the copy.

Three scope roots, as 04 decided: `.aurora-editor`, `.aurora-editor-portal`,
`.aurora-blocks-view`.

### 3. The externals are an allow-list over the whole promised surface

`build-plugins/promised-externals.ts` declares the eight promised specifiers
(`react`, `react/jsx-runtime`, `react-dom`, `react-dom/client`, `jotai`,
`platejs`, `@plone/registry`, `@plone/helpers`) and **fails the build** if a
chunk imports anything that is neither relative nor on that list.

Both halves of that are deliberate. The **whole** list is externalized, not just
what the hero imports today — externalizing an unimported module costs nothing,
a partial list is a landmine for the second brand block. And it is an
**allow**-list, because a deny-list of those eight names would wave through
`platejs/react`, or a transitive dependency that reaches React under some other
specifier — which is precisely the duplicate-instance failure the externals
exist to prevent.

### 4. `--derico-text-display` is retired — amends ticket 14 §3

Ticket 14 published **four** aliases of Clara's private type tokens. Ticket 15
then put the headline ramp on `.derico-hero h1` as a stated
`clamp(2.4rem, 1.4rem + 5cqi, 5rem)` and forbade overriding the alias — Clara's
own `.clara-home-copy h1` reads it. The hero is the only block that sets a
display-sized headline, so the alias was left **published and read by nobody**,
which 14's own guard (`test_published_aliases_reach_a_block_sheet`) calls dead
weight.

`derico.css` §3 now publishes **three**. The alias returns the day a block reads
it — published, not hoarded.

### 5. The canvas is a preview; the only editor-only element is the nag

The block is a Plate **void** node and nothing in it is `contenteditable`:
in-canvas text would mean re-solving focus, undo and selection inside a void, in
a block whose whole premise is that the author gets no choices. That is what
makes 07's `white-space: normal` safe — nothing is lost by normalising what
nobody types into.

`edit` and `view` render from **one** set of components, so both surfaces emit
the same `.derico-hero` root (07's correction). The single difference is a
`Still to fill in: …` hint, `contentEditable={false}` and placed **outside** the
hero's root, so it can neither be typed into nor styled by the block's palette.
Nothing in the schema is required, so a half-authored hero saves and previews
happily — the editor is simply where the author is told what a reader would
notice missing.

### Binding on ticket 09

- **The degradation table is one table implemented twice.** `data.ts` reads the
  stored JSON and `degradation.test.tsx` pins the result in 21 cases (art
  direction with portrait first, no-crop → no `<picture>` and no wash, four
  legend rows whatever is stored, numerals from position, half-filled entry
  keeps its numeral, `aria-hidden` with no alt, secondary link absent → the
  action row itself is gone). The server half must produce the same markup from
  the same data; any change to one is a change to both.
- **The record's `css` field points at `blocks.css`.** Lib mode emits **one**
  stylesheet per *build*, not per entry (04 §5), so every future block record
  names that same asset.
- **`block_api`**: `test_the_declared_block_api_floor_is_one_the_host_provides`
  skips today because no record declares one. Landing the record turns that skip
  into a live assertion — the floor is `1.0` (04 §8).
- **`defaultBlockWidth` is materialised at insert**, so `plate.py` reads an
  explicit `"full"` on the node and the server half needs no per-`@type` default
  of its own (11).

### Shipped

- `bundle-src/` — pnpm/Vite workspace: `vite.config.ts` (N entries → N bundles),
  `build-plugins/scope-wrap.ts` (vendored, byte-identical) and
  `promised-externals.ts`, `src/hero/` (entry, schema, data, `Hero` /
  `HeroView` / `HeroEdit` / `HeroMedia` / `Rings` / `HeroIcon`, three widgets,
  `hero.css`), plus `bundle-src/README.md` — the workspace's prose lives there
  because nothing hand-written may survive in `static-blocks/`.
- `src/plonetheme/derico/static-blocks/` — committed `hero.js` (23.7 kB) +
  `blocks.css` (17.1 kB) + sourcemap, registered in `configure.zcml` as a
  **second** static directory, `++plone++plonetheme.derico.blocks`.
- `src/plonetheme/derico/static/derico.css` — §3 down to three aliases.
- Tests: `install.test.ts` (6, including the
  `defaultBlockWidth`/`blockSchema` interlock that silently returns the width
  control if either half drifts alone), `degradation.test.tsx` (21),
  `tests/test_hero_sheet.py` (9, on the sheet that actually ships),
  `tests/test_block_addon_lockstep.py` (2), one added case in
  `tests/test_setup.py` (the bundles are *reachable*, not merely registered).
  All mutation-checked.
- Tooling: `invoke build-blocks` / `invoke test-blocks`, and a CI `blocks` job
  that typechecks, tests, builds, then runs `git diff --exit-code` over the
  artifacts — the only thing that makes committing build output safe.
- `CHANGELOG.md`, `README.md` (the theme is no longer "one stylesheet").
