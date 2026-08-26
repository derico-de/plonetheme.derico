# Build: the Derico Hero's server half

Type: task
Status: resolved
Assignee: md@derico.de
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

## Input from [ticket 08](08-build-editor-half.md) (2026-08-25)

The editor half is built, so the markup, the sheet and the data-reading rules
now exist — the server half **matches** them rather than deciding them again.

- **The markup is written down in TSX.** `bundle-src/src/hero/Hero.tsx`,
  `HeroMedia.tsx` and `Rings.tsx` are the reference tree; the template emits the
  same elements and the same class names under one `.derico-hero` root
  (`home-hero__grid`, `kicker`, `lede`, `action-row` + `button` / `quiet-link`,
  `hero-media` + `hero-wash`, `rings-figure` / `rings-stage` / `rings-disc` /
  `ring-thin` / `ring-markers` / `ring-now` / `ring-future`, `ring-legend`).
  **The stylesheet is shared** — `static-blocks/blocks.css` is scope-wrapped for
  `.aurora-blocks-view` as well as the editor — so a class the template renames
  is a rule that silently stops matching on the public view only.
- **Read the stored data through the same table.** `data.ts` is the editor's
  copy and `degradation.test.tsx` pins it in 21 cases; the server implements the
  same table against the same JSON. The rules, in full: a reference is a
  one-element list of `{"@id": …}` but tolerates a bare object or a plain string
  (a value that never went through the widget); text is trimmed; **a link
  renders only with both label and target** and never falls back to the
  target's Title (a fallback would make the two surfaces disagree between
  picking and reloading); the legend is **always exactly four** rows, padded or
  truncated, numerals from position, the **last** one marked `is-now`; a
  half-filled entry keeps its numeral and emits only the filled half; an
  entirely empty entry is a numeral and nothing else; no wide crop means no
  `<picture>` **and no wash**; the `<picture>` is `aria-hidden` with no alt to
  author. Field ids: `kicker`, `headline`, `lede`, `cta_label`, `cta_href`,
  `link_label`, `link_href`, `image_wide`, `image_portrait`, `legend`.
- **The record's asset fields.** `js` is `hero.js` and `css` is `blocks.css`,
  both under `++plone++plonetheme.derico.blocks/`. Lib mode emits **one**
  stylesheet per build, not per entry, so every future brand block's record
  names that same `blocks.css`.
- **Declaring `block_api` turns a skipped test live.**
  `test_the_declared_block_api_floor_is_one_the_host_provides` is the theme's
  only skip today — it has no record to read. The floor is `1.0` (04 §8);
  landing the record is what makes the lockstep guard real.
- **The canvas preview and the public `<picture>` are deliberately two paths.**
  The editor derives `<@id>/@@images/image/large` from the `@id` alone, because
  the enriched `image_scales` is absent for an image just picked (the widget
  trims the brain). Do not try to unify them — the public view splices two
  `Img2PictureTag` calls (05 §6) and the editor cannot.
- **Whitespace.** The sheet states `white-space: normal` on `.derico-hero`, so
  the template's indentation is safe on the public view; 07's whitespace-only
  text-node warning bites only on markup that lands inside the Plate editable.
- **`--derico-text-display` no longer exists** (08 amends 14 §3 to three
  aliases). The headline's ramp is stated in the block's own sheet, which both
  surfaces load; nothing in the template or `derico.css` may reach for that
  alias.

## Answer (2026-08-26)

**Built and green.** The hero installs, dispatches and renders; 109 new tests,
226 passing, nothing skipped. Six of the ticket's instructions held exactly as
written. Six other things came out of building it, and three of those correct
tickets that fed this one.

### The transformer this ticket asked for does not exist, and now cannot rot

The brief called for "the restapi serialisation transformer and its paired
stripping deserialiser". Ticket 01 had already found that stock restapi does
both — `ResolveUIDSerializerBase` recurses into every dict value, so a nested
`{"@id": …}` gets resolved *and* gets `image_scales` injected beside it
whatever the field is called, and `ResolveUIDDeserializerBase` pops
`image_scales` from every dict it walks on the way back down. 01 said to
"assert it with a test rather than trusting it", and that is the whole of the
work here: **this package registers no transformer at all.**

The assertion is not ceremony. This is a claim about somebody else's code that
this block depends on **silently**: the day restapi stops enriching a nested
`@id`, `image_source` returns `None`, the hero falls through to its plain-`<img>`
branch, and every visitor is served one full-size original with no ladder and
no error anywhere. Both halves of the round trip are pinned — the enrichment
(`@id` absolute, `image_scales` beside it) and the strip (`image_scales` gone,
`@id` back to `../resolveuid/<uid>`), the latter through
`BlocksJSONFieldDeserializer`'s own loop rather than a paraphrase of it.

### The version floor did not exist, and had to be created

The ticket's §12 input said to pin `plone.blicca.auroraeditor>=<the release
carrying news/45.feature>`. There is no such release: Blicca has **no tags, no
CHANGELOG, and news fragments 1–46 all unreleased** — `1.0.0a1` in its
`setup.py` is a development version that was never cut. A floor of `>=1.0.0a1`
would have asserted nothing (that version predates `image_source`), and
`>=1.0.0a2` would have failed to resolve against the checkout.

Settled with md@derico.de: **Blicca bumped to `1.0.0a2`** and the theme pins
`>=1.0.0a2`. Both signals now ship and stay independent — the record still
declares `block_api: 1.0` for the JS facades, and the distribution floor covers
the Python imports, which §2.2 explicitly does not.

### The hard dependency turns CI red, and that is the honest state

`pyproject.toml` now requires a package that is **private and not on PyPI**,
and `browser/hero.py` imports from it at module level. CI's `pip install -e
".[test]"` therefore cannot resolve without the sibling checkout, which needs
`BLICCA_TOKEN`.

Before the hero, a missing token only made two lockstep guards *skip* — the
tolerable half of a bad trade. It is no longer tolerable, because now nothing
at all would be tested. So the test job **fails with a named error** when the
secret is absent, rather than proceeding to a green run over an uninstallable
package. The checkout also moved *above* the install step, and Blicca is
installed from it first so the `>=` floor resolves locally instead of sending
pip to an index that does not carry it. Surfaced as
[ticket 16](16-blicca-token-secret.md) — only the repository owner can set it.

### 05 §7's diagnostics line was premised on a view that has no such dimension

"Surfacing *no portrait crop* belongs on the diagnostics view (ticket 09)."
It does not, and nothing was built for it. Blicca's diagnostics surface is
**per-record**: block-api compatibility, `@type` overrides, skipped bundles,
lockstep gaps — all registry-level facts about an add-on. It has no per-content-item
dimension at all, so "*this* hero has no portrait crop" has nowhere to go on it,
and giving it one would mean walking every page's somersault tree from an admin
view.

More to the point, it should not be reported anywhere: a wide-only hero is a
**legitimate authoring choice**, not a defect. Ticket 08's editor-side
`missing()` nag already lists what a reader would notice was absent — headline,
lede, primary CTA, wide image, ring legend — and deliberately omits the
portrait. That is the right surface and the right omission. **Ruled: nothing to
build**; 05 §7's last sentence is withdrawn.

### One crop renders through the *wide* sourceset — either crop, symmetrically

05 §7 covered "portrait absent" (centre-crop the wide image). The mirror case
was unexamined, and the obvious implementation is wrong: rendering a
portrait-only hero through the `hero-portrait` variant would carry that
variant's `media: (max-width: 55.99rem)` with it, leaving **every viewport
above 56rem with no matching source and therefore no resolution ladder at
all** — the `<img>` fallback would serve whatever scale the target names, at
every desktop width.

So the rule is symmetric and stated once: **whichever crop survives is rendered
through the wide sourceset**, which carries no `media` and is a pure resolution
ladder. The portrait variant is only ever used for the spliced `<source>`, i.e.
only when both crops exist — which is exactly the condition `HeroMedia.tsx`
already writes (`portrait && wide`). Both halves agree by construction rather
than by coincidence.

### The wash is keyed off the data, and the media is one property

Two small shapes that a straightforward implementation gets wrong:

- **`has_media` asks the data, never the rendered media.** A hero whose only
  crop is an SVG renders a plain `<img>` and still wants its gradient; a hero
  with no photograph at all must not get one, because a wash over the flat
  token ground reads as a rendering fault. This mirrors `Hero.tsx`, where the
  same trap is a truthy React element.
- **`media` is one property returning `{picture, src}`, not `picture` plus
  `plain_image`.** `image_source` refusing to build a `<picture>` *is* the
  condition for the plain `<img>`, so two template expressions would run the
  whole derivation twice to ask one question.

### Two things about HTML comments, one of which broke the build

`hero.pt` did not compile: **Chameleon refuses an ASCII `--` inside an HTML
comment**, and the first draft named `--plone-measure` in one. Custom
properties therefore go unnamed in that file, with a note saying why.

The second is not an error and is worse for it: an ordinary `<!-- -->` comment
is **served to every visitor**. This template's commentary is long and cites
internal ticket numbers. All of it moved to Chameleon's hidden-comment form
`<!--! -->`, which is stripped at compile time, and a test asserts no `<!--`
survives into the output.

### What needed nothing built

- **§5.4, the error policy.** Blicca's `render_block_data` already wraps every
  block. Demonstrated by accident: the compile failure above surfaced through
  the published page as an empty `block-render-error` placeholder rather than a
  traceback, which is the production half of the policy working.
- **Full-bleed (ticket 11).** Confirmed in the wild, including its accepted
  limit: a fixture-authored node with no `blockWidth` renders
  `has--block-width--default`, exactly as 11 predicted. The editor's
  materialisation is what makes the breakout work, and the view adds nothing —
  pinned negatively (no inline style, no `block-width` anywhere in the view's
  own output).
- **Ticket 08's prediction.** Landing the record turned the theme's only
  skipped test live: `test_the_declared_block_api_floor_is_one_the_host_provides`
  now runs, and the suite has no skips left.

### What shipped

| | |
|---|---|
| renderer | `browser/hero.py` + `templates/hero.pt`, `for="*"`, `zope2.View`, on the theme's layer |
| photograph | `Img2PictureTag` called once per crop, portrait `<source>`s spliced in front, portrait `<img>` discarded; `fetchpriority="high"`, never `lazy` |
| record | `plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero` — bundle, `block_api: 1.0`, the shared `blocks.css`, `types`, `permission` |
| gate | `plonetheme.derico: Insert Brand Block` in `permissions.zcml`, granted to Manager + Site Administrator in `rolemap.xml`, `acquire="True"` |
| imaging | `enormous 2600:65536` merged into `plone.allowed_sizes` with `purge="false"`; `hero-wide` / `hero-portrait` from an add-only setuphandler |
| uninstall | record removed; scale and variants deliberately left |
| upgrade | **1001**, narrowed to installing the host + `plone.app.registry` + `rolemap` + the variants — not a blanket profile reload |
| docs | README gains an authoring section (WebP, two crops not two sizes, the ~14ch headline budget), CHANGELOG four entries |

`tests/test_hero_view.py` (71) implements ticket 02's degradation table against
the same JSON `degradation.test.tsx` uses, plus markup parity with the TSX
class by class; `tests/test_hero_install.py` (38) asserts Blicca's own verdicts
— `evaluate()`, `may_insert()`, `lockstep_gaps()` — rather than raw record
values, because every packaging mistake here is a **fail-soft skip** whose only
symptom is a block quietly missing from the slash menu. Twelve mutations were
run against the two suites (lazy image, splice order, `is-now` index,
wash-keyed-off-media, root class, `.shell`, a stamped `lang`, shipped comments,
`purge` dropped, `block_api` overshoot, permission cleared, bundle path,
`@type` typo, forgotten variants, uninstall left behind); every one went red and
the baseline back to green.

### Inputs to ticket 10

- **Insert through the editor, not a fixture.** A node authored any other way
  has no `blockWidth` and renders `default` — measuring that box would measure
  the wrong thing.
- **Measure the LCP rather than assume it.** 05 §8 accepted a residual cost for
  declining a `<head>` preload; this is where it gets a number.
- **Upload real WebP crops.** The format story is upload-side only and no test
  can stand in for it.
- **Exercise the gate as a real Site Administrator and as a plain Editor.** The
  integration tests use role switching, not a login.
