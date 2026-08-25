# Build: the Derico Hero's editor half

Type: task
Status: in-progress
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
