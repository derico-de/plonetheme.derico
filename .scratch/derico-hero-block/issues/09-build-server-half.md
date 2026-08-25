# Build: the Derico Hero's server half

Type: task
Status: open
Blocked by: 14, 02, 05, 06, 11, 12, 15

## Question

The public rendering and the Plone packaging, in `plonetheme.derico`.

- `@@aurora-block-<@type>` browser page — `for="*"`, `zope2.View`, on the
  theme's own browser layer, over the contract's public `BaseBlockView`
  (contract §5.1/§5.2). The rings SVG is static markup in its template.
- The restapi serialisation transformer and its paired stripping deserialiser
  for whatever derived image data 01 turns up (contract §5.3).
- `profiles/default/registry.xml`: the `IAuroraBlockAddon` record(s) per 04's
  shape, plus 05's picture variants — with the upgrade step.
- Uninstall profile kept in step, matching how the theme already removes its
  bundle records.
- Fail-soft error placeholder in production, loud in development (§5.4).
- **Nothing to build for full-bleed** (11). The editor materialises
  `blockWidth: "full"` onto the node, so `plate.py`'s existing
  `block_width_for` already emits `has--block-width--full`; do **not** add a
  per-`@type` default to `DEFAULT_BLOCK_WIDTHS`. The view must not emit its own
  breakout either — the wrapper carries it.
- The renderer assumes no privilege — the insert gate is guidance, not security.
- **`permissions.zcml` + `profiles/default/rolemap.xml`: define and grant
  `plonetheme.derico: Insert Brand Block`** (Manager + Site Administrator),
  and set it as the record's `permission` value in `registry.xml`. Surfaced by
  [ticket 03](03-permission-gate.md), which built the gate but deliberately
  left Blicca permission-agnostic. `cmf.ManagePortal` will NOT do: its title
  is held by Manager alone in stock Plone, and the destination says *site
  administrator*. `rolemap.xml` is shipped profile XML, so this gets an
  upgrade step narrowed to `rolemap`.

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

## Input from ticket 12 (2026-08-25)

The image and reference derivations are now **promised API** — import them
from `plone.blicca.auroraeditor.rendering`, never from
`browser.rendering.scales` or `.picture`:

```python
from plone.blicca.auroraeditor.rendering import BaseBlockView
from plone.blicca.auroraeditor.rendering import image_source
from plone.blicca.auroraeditor.rendering import path_of
```

- **`image_source(item)`** → `{src, width, height}` or `None`. Call it once
  per crop on the enriched `{"@id": …}` dict, and hand each `src` to
  `Img2PictureTag().create_picture_tag(sourceset, attributes, lazy=False)` —
  the splice of ticket 05 §6 sits on top of that, unchanged.
- **`None` is the no-`<picture>` signal** — no scales, no download URL, no
  base, or an SVG upload. Render a plain `<img src>` and let ticket 06's
  `object-fit` handle it. This is the same branch as ticket 05 §7's
  "portrait absent", so both fall through one code path.
- **`path_of(url)`** for `cta_href` and `link_href` — the resolved `@id` is
  an absolute API URL and the public view must emit it site-relative.
  Caveat: it strips the scheme from a `mailto:`/`tel:`. Harmless here (both
  are object_browser content picks) but do not reach for it on free-form
  input.
- **Do not use `picture_tag`.** Still unpromised, and §5.2 now records why:
  one image, `lazy=True` fixed, returns a `str`.

**New requirement — a version floor.** `block_api` versions the JS facades
only (§2.2/§2.3), so it says nothing about these Python imports; the Python
distribution version is the only signal. The theme's `install_requires` must
pin `plone.blicca.auroraeditor>=<the release carrying news/45.feature>`.
Ticket 04 made Blicca a hard Python dependency; this makes it a versioned
one. Both signals ship — the record still declares `block_api`, and they are
independent.

## Input from [ticket 15](15-headline-at-320.md) (2026-08-25)

Both halves emit the same markup, so the server template must give the wrap
ladder the same elements to bite on — see
[ticket 08's copy of this note](08-build-editor-half.md) for the four rungs;
the sheet is shared and lives with the editor half.

What is specific here:

- The template's grid and flex items are the ones rung 1 pins: the copy cell,
  `.action-row` and the `.ring-legend` rows. If the server markup nests them
  differently from the TSX, the rule stops matching on one surface only.
- **`lang` is inherited, never stamped.** `hyphens: auto` needs the page
  language, which `main_template` sets from `portal_state.language()`. The view
  must not emit a `lang` of its own, and the block has no `lang` field.
- The headline budget is a README line (see 04 §12's README work), not a field
  caption and not a validator.
