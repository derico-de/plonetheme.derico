# Wayfinder map: Derico Hero — the first brand block

Labels: wayfinder:map
Status: needs-triage

## Destination

The **Derico Hero brand block, built and working**: a site administrator inserts
it in `@@aurora-edit`, fills in its text and images, and the public view renders
the homepage opening from the mockup — image, kicker, headline, lede, two calls
to action, and the rings figure with its four-entry legend. Reaching it includes
the admin-only insert gate this block depends on, which lands in
`plone.blicca.auroraeditor`.

Done means the block is installed and usable on the sandbox site, not that a
spec exists for it.

## Notes

- **This map carries execution.** Wayfinder plans by default; here the
  architecture is already decided (see below), so the remaining decisions are
  small and the tickets run through to the built block.
- **Two repos.** The block lives in `plonetheme.derico`; the permission gate and
  the contract amendments land in `plone.blicca.auroraeditor` (map ticket 03).
- Skills to consult per ticket type: `/grilling`, `/domain-modeling`,
  `/prototype`, `/research`, `/plonecli` (upgrade steps), `/tdd`.
- Vocabulary: [`CONTEXT.md`](../../CONTEXT.md) — **brand block**, **rings
  figure**, **ring legend**, **Derico Hero**.
- The mechanism this block rides on is already decided **and implemented**:
  [the block add-on contract](../../../plone.blicca.auroraeditor/docs/design/aurora-block-addon-contract.md)
  + ADR 0013, from the
  [aurora-block-addons map](../../../plone.blicca.auroraeditor/.scratch/aurora-block-addons/MAP.md).
  Host `block_api` is **1.1** (`wrapper/vite.config.ts:18`). Read the contract
  before touching packaging; this map decides only what it leaves open.

### Fixed constraints from the charting session (2026-08-22, grilled with md@derico.de)

- **Brand blocks are deliberately inflexible.** Implement the design template,
  allow the text and images it needs, offer **zero** author-facing options — no
  block width control, no palette variant, no "hide the rings" toggle. A variant
  is added when the design asks for one, never in anticipation. This is the
  standing principle for every project block, not a one-off for the hero.
- **Home: `plonetheme.derico`.** `package.json` + Vite build in the repo,
  artifacts committed under `src/plonetheme/derico/static/`, picked up by a
  registry record — the `plone.staticresources` workflow.
- **Registered as an `IAuroraBlockAddon` record, not a `plone.bundles` record.**
  `@@aurora-edit` emits an import map aliasing `react`, `platejs`, `jotai`,
  `@plone/registry` to facades re-exported from the editor remote
  (`aurora_edit.pt:38`), and the wrapper `import()`s each block bundle by URL
  (`main.tsx:169`). A `plone.bundles` record emits `<script src defer>`, not
  `type="module"`, so bare imports miss the map and a **second React** loads —
  the block then fails inside Plate. Same build workflow, different record.
- **Single-ecosystem exemption.** Contract §1.1 requires the JS half to be a
  publishable Aurora npm package. A brand block serves one brand; it is built
  locally and **never published**. Both `edit` and `view` are still implemented.
  The exemption is written into the spec by ticket 03.
- **No relationship to `plone.blicca.heroblock`.** The generic hero decided on
  [aurora-block-addons ticket 08](../../../plone.blicca.auroraeditor/.scratch/aurora-block-addons/issues/08-reference-block-and-scaffold.md)
  stays unbuilt. The Derico Hero is a concrete brand example, not a
  generalisation of one, and does not wait for it.
- **The rings are template, the words are content.** Ring geometry and the
  `is-now` highlight are static markup. Exactly **four** legend entries, each
  `{title, subtitle}`; the numerals are derived from position and not editable.
- **Editable inventory**: kicker, headline, lede, primary CTA (text + link),
  secondary link (text + link), wide image, portrait image, and the four legend
  pairs. **No image alt** — the mockup's `<picture>` is `aria-hidden="true"`,
  the photograph is decorative.
- **Two image fields**, wide and portrait, each rendered through
  `plone.picture_variants` for widths and formats. Plone's named scales give
  variants of one crop, not art direction, so the two crops stay two uploads.
- **Admin-only insert, via the menu, not via the bundle.** A `permission` field
  on the record; `@@aurora-edit` passes the verdict to the client but loads the
  bundle for **everyone**, so an ordinary editor opening a page with a hero sees
  the rendered hero rather than an unknown-block placeholder. The wrapper's
  existing `extendGroups` (`plugin-kit.tsx:73`, an Aurora-provided seam —
  `SlashMenuConfig`, `slash-menu.tsx:53`) filters the block out of the slash
  menu for users without the permission. Aurora's own `restricted` field is a
  static boolean and cannot do this.
- **Insert-gating is guidance, not security.** The block can still be authored
  through the API, so `@@aurora-block-*` must never assume the caller was
  privileged.
- **The hero is full-bleed via `blockWidth: full`.** Verified while charting:
  Blicca already implements the viewport breakout on both surfaces —
  `blocks_view.css:729` for the public view, `wrapper/src/styles/index.css:34`
  for the editing canvas, both toolbar-aware through `--aurora-full-bleed-offset`
  declared on `<body>`, with `html:has(...) { overflow-x: clip }` guarding
  against a phantom scrollbar. The class is stamped server-side by
  `plate.py:346`. The block inherits all of it and reimplements none of it, so
  the breakout never enters the add-on's scope-wrapped sheet.
  Note Aurora's own `full` means `--block-width: 100%` (`block-width-plugin.ts:54`),
  i.e. the container — the viewport bleed is Blicca's addition and Blicca's to
  maintain.
- **The block fixes its own width; the author never chooses it.** Settled by
  ticket 11 — Aurora's `defaultBlockWidth` on the `blocksConfig` entry already
  does this, and the charting note that "no per-`@type` default width exists
  today in either half" was wrong. One key in the theme's `install()`; nothing
  to build in either half.
- Any GenericSetup profile XML change gets an upgrade step, even at `1.0.0a1` —
  scaffold via `plonecli add upgrade_step`, narrowed to the affected import step.
- **Blicca is a hard, versioned dependency of the theme** (ticket 09): Python
  `>=1.0.0a2` *and* a GS profile dependency, which are different promises about
  different surfaces. `block_api` covers neither — it versions the JS facades
  alone. Consequence: the theme cannot be installed, tested or built without
  the private `plone.blicca.auroraeditor` checkout, on CI as much as locally.
- **The public template's commentary must be `<!--! … -->`.** Chameleon refuses
  an ASCII `--` inside an HTML comment at all, and an ordinary comment is
  served to every visitor. Applies to every brand block's template.

## Decisions so far

<!-- one line per closed ticket: gist + link -->

- [Research: how an Aurora block schema takes an image, and how it reaches the renderer](issues/01-research-image-field-and-delivery.md)
  — no image *field type* exists; behaviour comes from a `widget` key, and only
  `object_browser` (`mode: 'image'`) survives the sidebar's one-argument
  `onChange`, so the hero uses the Teaser's `preview_image` idiom, not the Image
  block's. Stored as a one-element list of `{"@id": "../resolveuid/<uid>"}` per
  image; `image_scales` is injected by **stock restapi** on any nested `@id` and
  stripped on save, so contract §5.3 looks already satisfied — assert it with a
  test rather than trusting it. Blicca's `picture_tag` / `image_model` do the
  `<picture>` work but are **unpromised API** (§5.2), which is now
  [ticket 12](issues/12-picture-helper-api-status.md).
  Findings: [`assets/01-image-field-and-delivery-findings.md`](assets/01-image-field-and-delivery-findings.md).

- [Decide: the shape of plonetheme.derico's JS workspace](issues/04-theme-js-workspace.md)
  — one `bundle-src/` pnpm+Vite workspace, **N entry points → N bundles → N
  records** (the shared-bundle shape kills the per-block `enabled` switch).
  Artifacts committed to a **new, build-output-only** `static-blocks/` served as
  `++plone++plonetheme.derico.blocks/`, with `emptyOutDir: true` — so no
  hand-written file may live there. `scope-wrap.ts` is **vendored** (three scope
  roots, not the wrapper's two) and `block_api` declares the floor `1.0`, both
  backed by skip-when-absent lockstep tests on CI's *pytest* job. CI builds and
  runs `git diff --exit-code` over the artifacts. Blicca becomes a hard Python
  **and** GS-profile dependency (upgrade step required), and the theme stops
  calling itself tokens-only.

- [Decide: the Derico Hero's content model](issues/02-content-model.md)
  — `@type` **`derico-hero`** (it lands verbatim in `.block-derico-hero` and in
  the view name `aurora-block-derico-hero`), record `plonetheme.derico.hero`.
  All text **plain** — no rich-text widget exists anywhere in the stack — edited
  in the **sidebar**, with the canvas a live preview; the lede gets a
  block-registered `derico_textarea`. All four references (`cta_href`,
  `link_href`, `image_wide`, `image_portrait`) are **object_browser picks
  trimmed to bare `{"@id": …}`**, so renames survive and no stale brain metadata
  is persisted. `legend` is an **array of exactly four** `{title, subtitle}`,
  seeded empty at insert. **No `blockWidth` key** — the width is template, so
  full-bleed rides entirely on ticket 11. Nothing `required`; a link renders only
  when label *and* target are present, one crop renders at every breakpoint, a
  half-filled legend entry keeps its numeral. Widgets are namespaced
  (`derico_textarea`, `derico_ring_legend`) because `registerWidget` is global
  and last-wins. Surfaced [ticket 13](issues/13-object-browser-forward-props.md).

- [Decide and build: the admin-only insert gate in plone.blicca.auroraeditor](issues/03-permission-gate.md)
  — **built in Blicca**, which stays permission-agnostic. Optional
  `permission` on `IAuroraBlockAddon` (a permission *title*, empty =
  unrestricted); the verdict ships as **`restrictedBlockTypes`**, a derived
  list of `@type`s rather than a per-record flag, evaluated against **the
  object being edited** (permissions acquire). The wrapper filters
  `block_<@type>` items via a module-level setter, mirroring the
  `setFloatingToolbarButtons` precedent. The blocker the ticket didn't
  anticipate: contract §7 forbade this outright ("never ahead" of Aurora) —
  resolved as **subtractive curation on Aurora's own `extendGroups` seam**,
  which ADR 0008 sanctions, so **ADR 0008 is unamended** and only §7 changed.
  Bundle loads for everyone (no unknown-block placeholder for ordinary
  editors) and the gate **fails open** when a record omits `types`. **Not a
  block-api bump** — host stays 1.1. §1.1 gained the **brand block**
  single-ecosystem exemption as a general category; **brand block** and
  **insert gate** are now Blicca glossary terms. The hero's own permission
  (`plonetheme.derico: Insert Brand Block`, Manager + Site Administrator) was
  handed to ticket 09 — `cmf.ManagePortal` is Manager-only in stock Plone and
  would have locked out the very role the Destination names.

- [Decide: how the hero's two images are stored, scaled and served](issues/05-image-delivery.md)
  — three of the ticket's premises were wrong. **No format ladder**: the
  `picture_variants` sourceset schema is closed over `scale`/`media`/`sizes`/
  `additionalScales` and `Img2PictureTag` emits no `type=`, so Plone switches
  resolution only — the block serves whatever was uploaded (`plone.scale`
  keeps WebP, coerces the rest to JPEG), and "upload WebP" becomes a README
  line. **Not registry.xml**: `picture_variants` is a JSONField, so the two
  variants land via an idempotent setuphandler on Blicca's
  `ensure_fullwidth_variant` pattern, while `plone.allowed_sizes` merges in
  through `registry.xml` with `purge="false"` — **one** upgrade step covers
  both. **Not Blicca's `picture_tag()`**: it renders one image and hardcodes
  `lazy=True`, so the view calls public `Img2PictureTag` **twice** and splices
  the portrait `<source>`s ahead of the wide ones, giving art direction across
  two uploads in one `<picture>`. Ladder re-derived from viewport x DPR rather
  than copied: portrait needs **no** new scale, wide needs exactly one —
  **`enormous 2600:65536`**, appended and never removed on uninstall. Both
  variants `hideInEditor`, `sizes: "100vw"`, `additionalScales` explicit.
  `fetchpriority="high"` with `lazy=False` instead of a `<head>` preload;
  missing portrait centre-crops the wide; the canvas previews one plain scale.
  Narrowed [ticket 12](issues/12-picture-helper-api-status.md).

- [Decide: what CSS the hero needs, and how it coexists with the theme](issues/06-css-and-full-bleed.md)
  — three premises wrong again. **No header overlap**: the mockup's header is
  opaque with a hairline and the hero follows it in flow; the real top-edge
  problem is Plone's own breadcrumbs/contentheader/byline above the first block,
  fixed by a chrome-suppression rule in **`derico.css`** (the scope wrap rewrites
  `body`, so the block sheet can never reach it) — public view only, gated on the
  hero being first. **Load order needs no fixing**: `main_template.pt` puts
  `style_slot` after `plone.htmlhead`, so the block sheet always follows
  `derico.css`, and inheritance proximity settles the tokens regardless.
  **Clara's component rules are unusable**: `scope-wrap.ts` flattens `@layer`, so
  the editor's preflight is unlayered and beats `@layer components` in the canvas
  but not on the view — so Clara's *tokens* are inherited and its *rules* never
  reused; the block owns its CTA. The `--hero-*` palette is the block's, renamed
  `--derico-hero-*` and declared on `.block-derico-hero` (not the shared scope
  root); Clara's private type tokens are re-published as `--derico-text-*` by
  `derico.css`, keeping one seam. Mockup class names kept, every selector
  descending from `.block-derico-hero`. **Container queries, not media queries**
  — the hero is `100vw − toolbar`, so a viewport query overflows the two-column
  grid for the very administrator the Destination names; `contain: layout` comes
  free and retires `isolation: isolate`. Animations and `@keyframes` are
  public-view-only and prefixed. `derico.css` stops being a pure token sheet:
  three tests in `test_override_minimality.py` widen rather than go.

- [Prototype: does the rings figure survive inside the editing canvas?](issues/07-prototype-rings-in-canvas.md)
  — **the rings survive; the box around them did not.** Disc 527px at 1440 and
  314px at 375, markers 28px throughout, legend captions **15px — Clara's label
  floor exactly**, never under. No editor rendering needed. Three corrections
  came out of the pixels. **`.block-derico-hero` is the wrong hook**: Aurora
  stamps `block-<@type>` on the wrapper, which is the full-bleed box on the view
  (1220 @220) but the column box in the canvas (1134.9 @262.5), so painting the
  hero on it makes its own `overflow: hidden` clip the breakout — the component
  needs its own `.derico-hero` root, after which both surfaces measure 1220 @220
  identically (corrects 06 §2/§4). **`isolation: isolate` comes back**:
  `container-type: inline-size` computes `contain: none`, supplies no stacking
  context, and the `z-index: -2` media falls behind the hero's opaque ground —
  the photograph vanishes on both surfaces (corrects 06 §8's mechanism, not its
  container query, which measurement vindicated: at a 900px viewport the hero is
  42.5rem and correctly stays single-column). **The Plate editable's
  `white-space: pre-wrap` and `overflow-wrap: break-word` inherit into the
  block** — indentation alone inflated the rings figure 76%, and the headline
  breaks mid-token in the canvas where the view keeps it whole. Surfaced
  [ticket 15](issues/15-headline-at-320.md): the mockup itself clips its
  headline at 320, inherited rather than caused by the canvas.

- [Decide and build: how a brand block fixes its own width without offering the author a choice](issues/11-per-type-default-block-width.md)
  — **nothing needed building; the ticket's premises were wrong on both halves.**
  Aurora already resolves a ploneBlock's width as `styleFields.blockWidth ??
  {defaultValue: blocksConfig[@type].defaultBlockWidth}`
  (`style-fields-plugin.ts:67`, upstream-tested), and Blicca already composes
  `StyleFieldsKit`. So the mirror rule is met by **adoption**: one key,
  `defaultBlockWidth: 'full'`, in the theme's own `install()` (ticket 08) — no
  Blicca field, no record key, no `plateBlocksConfig` entry, and it does **not**
  land in Blicca as the ticket claimed. The editor **materialises**
  `blockWidth` onto the node at insert, so `plate.py` reads an explicit width
  and the server needs **zero change** — both behaviours already pinned by
  existing tests. Rejected a `default_block_width` record field: it would
  declare the width twice, which is the drift "two code paths, one answer" was
  meant to prevent. **Suppressing the control was already done by ticket 02** —
  omitting `blockWidth` from the schema *is* the branch that triggers the
  fallback, and declaring both hands the control back. Left as a **default, not
  an override**. Accepted limit: an API/migration/fixture-authored node renders
  `default`. Built: contract **§1.4** + the empty `defaultBlockWidth` table
  cell + `news/44.feature`.

- [Decide and build: does the hero reach into Blicca's unpromised image helpers, or do they get promoted?](issues/12-picture-helper-api-status.md)
  — **promoted, but not the function the ticket named.** `image_model` is the
  wrong shape: the hero discards its `srcset` (`Img2PictureTag` builds the
  sourceset) and its `alt` (the `<picture>` is `aria-hidden`), and it lacks the
  SVG guard, which lives in `picture_tag`. And the gap was never image-only —
  `path_of` is equally unpromised and the hero needs it for `cta_href` /
  `link_href` regardless. So §5.2 gains **one seam, two functions**: `path_of`
  and a new **`image_source(item, image_field=None)` → `{src, width, height}`
  or `None`** — `picture_tag`'s preamble lifted whole, `None` meaning "do not
  build a `<picture>`". Free functions, not `BaseBlockView` methods.
  `picture_tag` is **refactored onto it** (a promised copy nobody exercises
  drifts) and stays unpromised *with its reason now written down*: one image,
  `lazy=True` fixed, returns a `str` — so art direction goes through
  `Img2PictureTag` directly, which is now the documented path, not a
  workaround. Corrects ticket 05: `picture_tag` *could* express art direction
  by splicing two calls; the real disqualifier is the `str` → re-parse round
  trip. The load-bearing new sentence: **`block_api` cannot version this** —
  §2.2 covers the JS facades alone, so the Python surface is versioned by the
  distribution, and ticket 09 gains an `install_requires` floor. Extracted
  from five call sites, not designed from the hero, which is what answers "an
  API commitment made from one example". Built in Blicca: 20 unit tests
  standing in for the add-ons that import it; 202 pass.

- [Build: Blicca's object browser forwards selectableTypes and upload](issues/13-object-browser-forward-props.md)
  — **built, but not through the props the ticket named.** Aurora already
  spells this: its object browser reads `selectableTypes` from
  `widgetOptions.pattern_options` (`isSelectable`, cmsui
  `ObjectBrowserWidget/utils.ts`), and **`plone.restapi` already serializes
  relation fields with that same envelope**, carrying pat-contentbrowser
  option names verbatim. So Blicca reads Aurora's envelope rather than
  claiming top-level keys of its own — a hero schema written the ticket's way
  would have lost its restriction the day the substitution is dropped for
  Aurora's widget. `upload` has no Aurora counterpart (Aurora's ImageWidget
  owns upload itself) and rides the same open bag, degrading to browse-only
  upstream. **Only these two keys** — `maximumSelectionSize` is deliberately
  left to `mode`, since two ways to say one width is the drift ticket 11
  rejected. Corrects ticket 02's snippet in place. Also: `mode: 'image'` /
  `mode: 'link'` are dead **everywhere** — `ObjectBrowserWidgetMode` is
  `'multiple' | 'single'`, yet Aurora's own teaser and image schemas ship
  them, so upstream's teaser image override is unrestricted too. **Not a
  block-api bump** — §2.2 covers the JS facades alone, so like §5.2's Python
  surface this is versioned by the distribution; host stays 1.1. Shipped:
  contract **§1.5**, `news/46.feature`, and an e2e that records the options
  pat-contentbrowser is *constructed* with (patternslib adopts a pre-created
  registry Proxy). Its fixture-free case — the shipped widget pulled from the
  registry through URL-imported facades, because the import map only exists
  when an add-on survived filtering — was confirmed RED then GREEN in the
  sandbox, along with the negative case; the full sidebar path needs the
  helloaddon ZCML this instance does not load.

- [Build: the token-layer changes the hero needs](issues/14-theme-layer-changes.md)
  — **built; nothing was re-decided, but three confirmations turned into
  mechanisms.** `derico.css` gains §3 (four `--derico-text-*`/`--derico-font-`
  `display` aliases of Clara's private type tokens) and §7 (the
  chrome-suppression rule, 06 §1 verbatim; 07's correction holds — the
  `.block-derico-hero` wrapper stamp was free for it). **"No gap is added" is
  now measured**: all the space above the first block sits on the three hidden
  elements themselves and Clara zeroes `.plone-layout`'s row-gap, so the three
  `display: none` declarations *are* the whole of "flush" — and Clara's
  companion `.element-body { padding-block-end: 0 }` is deliberately not
  mirrored, since the hero opens the page rather than closing it. `:first-child`
  verified against the markup: `plate.py` **skips** the title node rather than
  emitting an empty wrapper. **"No upgrade step" confirmed with a mechanism**,
  not an absence — Plone builds the bundle URL with `unique=True` and
  `webresource` derives that key from a **hash of the file's bytes**, so editing
  `derico.css` busts its own cache; no `last_compilation`, no registry value
  changed. The tests were **pinned, not allow-listed**: the exception is matched
  structurally, its body must be exactly `display: none`, exactly one such rule
  may exist, and the narrowness assertions are on the guard constant rather than
  on the matched selector (which would be circular). The four aliases are
  **exempt** from the usage test rather than skipping it wholesale — 04 §9's
  "a guard that always skips protects nothing" applies to the other ~25 tokens,
  which are checkable today. One guard goes past the ticket on purpose and is
  **binding on ticket 08**: a block sheet may never name `--clara-*`, which is
  the whole reason the aliases exist. Two now-false self-descriptions
  (`derico.css`'s header, `registry.xml`'s comment) fixed here; the wider README
  rewrite stays with **04 §12**. 103 passed, 2 skipped; every guard
  mutation-checked red-then-green.

- [Decide: what the hero's headline does when its longest word will not fit](issues/15-headline-at-320.md)
  — **the ticket asked the wrong question: the box overflows, not the words.**
  The copy cell is a grid item, so it floors at `min-content` and grew to
  **320px inside a 288px shell** (383 with a longer compound); the hero's
  `overflow: hidden` then cut it. The answer is a **ladder** whose guarantee is
  a layout rule: `min-width: 0` on the hero's grid/flex items (holds for a
  headline nobody has written yet), then `overflow-wrap: break-word` — which
  measured **cannot** substitute for it, since it does not feed intrinsic
  sizing — then the ramp, then `hyphens: auto` as a labelled enhancement that
  is a **no-op in this Chromium** (no dictionaries), so tests assert the
  declaration and never the rendering. Two of the ticket's four options were
  premised on the wrong mechanism. **Lowering the clamp's floor does nothing
  at 320**: the clamp returns its middle term there, so the slope had to
  change — `clamp(2.4rem, 1.4rem + 5cqi, 5rem)`, chosen over a flatter
  candidate that bought the fit by shrinking the whole mid-range 9%. **`cqi`,
  not `vw`**, because 07's table shows the hero is 1220 @220 on the *public
  view* too: the box is viewport-minus-toolbar for every logged-in user, so a
  `vw` ramp is the 320 defect in miniature. Stated on `.derico-hero h1`, never
  as a token override (§3 is aliases, and Clara reads them). Scope is one rule
  over every grid/flex item in the block, `14.5ch` stays, `lang` is inherited
  and never stamped or offered as a field, and the budget is a README line, not
  a caption. Corrects 07: break-word does **not** change the desktop wrap —
  `white-space: pre-wrap` alone did — which amends the `overflow-wrap: normal`
  instruction 07 wrote into 08 and 09. **The design source is fixed in this
  ticket** (verified: cell 288, zero hero and document overflow at 320, 1440
  unchanged), so the mockup is a trustworthy reference for the next brand
  block. Measurements:
  [`assets/15-wrap-measurements.md`](assets/15-wrap-measurements.md).

- [Build: the Derico Hero's editor half](issues/08-build-editor-half.md)
  — **built and green**; the ticket's instructions all held, and four things
  came out of writing it. **The reference trim moved from the edit component
  into a widget** (corrects 02): the sidebar writes straight onto the Plate node
  via `onFormDataChange` → `setNodes`, so the edit component is never consulted
  and has no interception point — hence a third namespaced widget,
  `derico_reference`, producing exactly the bare `@id` shape 02 fixed. Same
  reading: **cmsui resolves a widget by field id before `widget`**, so
  `image_wide`/`image_portrait` are load-bearing names — a field called `image`
  silently takes the registered image widget. **Vendoring `scope-wrap.ts` was
  not enough**: in lib mode `vite:css-post` emits the single `cssFileName`
  asset *after* an unenforced plugin's `generateBundle`, so the sheet shipped
  unwrapped and every token died against Aurora's scoped preflight — fixed with
  `enforce: 'post'` at the call site, leaving the vendored copy byte-identical
  to upstream, which is what the lockstep test pins. The externals are an
  **allow-list over all eight promised specifiers**, not just what the hero
  imports: a deny-list would wave through `platejs/react` or a transitive route
  to React, which is the duplicate-instance bug itself. And
  **`--derico-text-display` is retired** (amends 14 §3 to three aliases): 15
  put the ramp on `.derico-hero h1` and forbade overriding the alias, leaving it
  published and read by nobody — dead weight by 14's own guard. The canvas is a
  preview of a **void** node — one set of components for both surfaces, the only
  editor-only element a `contentEditable={false}` nag outside `.derico-hero`.
  Binding on 09: the degradation table is one table implemented twice (21 vitest
  cases), the record's `css` names the single `blocks.css`, and landing the
  record turns the skipped `block_api` floor test live. 27 vitest, 116 passed /
  1 skipped, artifacts reproducible under `git diff --exit-code`.

- [Build: the Derico Hero's server half](issues/09-build-server-half.md)
  — **built and green; the block installs, dispatches and renders.** The
  transformer the ticket asked for **does not exist**: 01 was right that stock
  restapi enriches a nested `{"@id": …}` and strips it again, so this package
  registers none — and both halves of that round trip are now *pinned*, because
  the failure is silent (no ladder, no error, one full-size original to every
  visitor). The **version floor had to be created**: Blicca was never released —
  no tags, no CHANGELOG, `1.0.0a1` a dev version — so it was bumped to
  **`1.0.0a2`** and the theme pins `>=1.0.0a2`. That hard dependency **turns CI
  red** until `BLICCA_TOKEN` is set, and the job now says so instead of running
  green over an uninstallable package ([ticket 16](issues/16-blicca-token-secret.md)).
  Three corrections: **05 §7's diagnostics line is withdrawn** — Blicca's
  diagnostics is per-*record* and has no per-content dimension, and a wide-only
  hero is a legitimate choice, which is why 08's nag already omits the portrait;
  **one crop renders through the *wide* sourceset whichever crop it is**, since
  the portrait variant's own `media` would strand every viewport above 56rem
  with no ladder (05 §7 had only considered the mirror case); and the
  **`<picture>` is one property, not two**, because `image_source` refusing to
  build one *is* the condition for the plain `<img>`. Two facts about HTML
  comments: Chameleon **refuses `--` inside one** (the template would not
  compile), and an ordinary comment is **served to every visitor** — all of the
  template's commentary is now `<!--! -->`. Nothing needed building for §5.4 or
  for full-bleed, and 11's accepted limit was seen in the wild: a
  fixture-authored node renders `default`. Upgrade step **1001** is narrowed to
  installing the host plus `plone.app.registry`, `rolemap` and the variants.
  109 new tests (226 total, **no skips left** — landing the record turned 08's
  predicted skip live), 12 mutations red-then-green.

- [Task: install the block and verify it end to end](issues/10-verify-end-to-end.md)
  — **the block installs, inserts, authors, saves and renders on the sandbox
  site, and the published page matches the design source everywhere except its
  type family.** Measured side by side against `docs/design/derico.de/site` in
  one browser at 1440/900/375/320: grid tracks identical to the pixel, the
  container query flipping to one column at the same place, rings stage and
  disc to the pixel, markers 28x28, nothing under 15px, the headline carrying
  the design's `-0.02em` and not Clara's. The gate does what 03 designed — an
  ordinary editor gets the same 19-item menu minus the hero, and a page that
  already holds one still RENDERS it. One React (the block's resource
  directory serves exactly `hero.js` and `blocks.css`). 15's two unverified
  assumptions both hold: `<html lang>` agrees on `de`, and nothing clips at
  320 or 375 on either surface. The proof is [`e2e/`](../../e2e/) — two
  re-runnable browser tests, not a transcript. Three defects came out of it:
  the hero's body type is **Blicca's blocks-view default, not the theme's**
  ([ticket 17](issues/17-hero-body-type.md), and the whole of the one
  remaining geometry difference), the ring legend **misses AA over the
  photograph** in the design source as much as here
  ([ticket 18](issues/18-legend-contrast-over-the-photograph.md)), and the
  upgrade profile is offered as an installable add-on
  ([ticket 19](issues/19-hide-the-upgrade-profile.md)). Method notes worth
  keeping: a worst-pixel contrast number cannot tell a defect from a speckle
  (report the share of the glyph area too), `visibility: hidden` removes the
  background you were trying to reveal, and an unscoped `h1` query on the
  published page returns the content header's title, not the block's.

- [Decide: how the ring legend keeps WCAG AA over the photograph](issues/18-legend-contrast-over-the-photograph.md)
  — **not a legend defect: every text element in the hero except the headline
  fails over a bright photograph, and the photograph is author-supplied.** The
  headline is large text and clears 3:1 at 3.05 worst-case; everything else
  needs 4.5 and gets 1.00–3.05, so ticket 10's medians of 8–18 measured the
  fixture forest, not the block. Two of this ticket's own four candidate fixes
  are arithmetically dead — no wash alpha below 0.983 saves the is-now cyan,
  and no cyan in the palette survives a bright image without a ground. The
  guarantee is **hero-wide and structural, from two local grounds, with the
  wash no longer load-bearing at either breakpoint**: an **opaque card** behind
  the legend `<dl>` (forced — cyan is unreachable translucent; on the ground
  every existing colour passes, so **no colour changes**), and a **feathered
  scrim at plateau alpha 0.926** over the copy box, set by the copper kicker
  against a white photograph with no wash. The copy box is cut out of the wide
  mask and the wash suppressed across the mobile copy band, so the scrim is the
  only layer over the copy and the two never stack to 0.98. **No image
  brightness cap** — costed and rejected: the wide mask *cuts the wash away* at
  bottom-left where part of the copy sits, making the real cap 0.08, a black
  image. `#039fba` stays. The design source gets identical CSS. Acceptance is
  two tests with different jobs: a CSS-value test reading the tokens from the
  built sheet proves *the backdrop is strong enough where it applies*; the e2e
  with its named exceptions deleted proves *every glyph sits where it applies*.
  Built by [ticket 21](issues/21-build-the-contrast-guarantee.md); the rings
  disc's own 1.4.11 gap became
  [ticket 20](issues/20-ring-stroke-non-text-contrast.md).

- [Decide: where the hero's body type comes from](issues/17-hero-body-type.md)
  — neither seam the ticket offered. `--plone-font-body` and
  `--plone-leading-body` already carry the mockup's exact values
  (`"Source Sans 3", system-ui, sans-serif` and 1.65) on Clara's `:root`, and
  06 §3 permits a block sheet to speak them — so the hero states both on
  `.derico-hero` and **neither `derico.css` nor `blocks_view.css` is touched**;
  §3 gains no fourth alias. The theme-layer option was ruled out on a fact, not
  a preference: Blicca states the Tailwind stack on `.aurora-blocks-view` only,
  the canvas getting it from Aurora's `@scope`'d preflight, so a theme rule
  fixes the view and **breaks** canvas/view parity — while the block sheet's
  three scope roots hold parity by construction. The leading moves with the
  family (1.6 → 1.65 is the legend's whole 291-against-330 height gap).
  Acceptance is three assertions: a CSS-value test that the tokens are *named*
  rather than hardcoded, an e2e on the published view, and the same e2e in the
  canvas — the last pins the parity that justified the seam. Built by
  [ticket 22](issues/22-build-hero-body-type.md), which is deliberately not
  folded into 21.

## Not yet specified

- **Brand body type for every other block on derico.de.** The text, teaser and
  listing blocks have the hero's defect unfixed and wider: Blicca's
  `blocks_view.css` states a Tailwind sans stack on `.aurora-blocks-view`, so
  the published page renders them in the browser's generic sans rather than the
  theme's Source Sans 3. Ruled off [ticket 17](issues/17-hero-body-type.md) as
  in scope for the *site* but not on the route to this map's Destination. Not
  yet sharp because the seam is genuinely undecided: a blocks view arguably
  should not impose a family on a host theme at all (Blicca's call under the
  mirror rule, and it would move every Blicca site), while a theme-layer rule
  can only reach the published view and would break the canvas/view parity
  Blicca's current stack buys. Its phrasing waits on that Blicca conversation.

- **A print stylesheet for the theme.** The mockup ships a whole-page
  `@media print` block; derico ships none. Ruled off ticket 06 as theme-wide
  rather than block-local — the site will want one, but not from this effort's
  tickets.

- **The rest of the mockup as brand blocks.** The manifesto grid, the service
  atlas / Balkenlage, and the field-guide definition list are all "beyond
  tokens" too. Whether they become brand blocks, and in what order, is unknown.
  (The workspace no longer waits on this: ticket 04 chose the N-entry layout
  that accommodates any number of them.)
- **Editor-side i18n for brand blocks.** The site is bilingual DE/EN; block
  *content* is per content item, but the block's own editor labels (title,
  field labels, placeholders) are not. Inherited from the contract's open items.
- **Contributing the insert gate upstream.** Ticket 03 has now built it in
  Blicca (contract §7); whether per-permission block availability should become
  an Aurora feature — and this filter then give way to it under the mirror rule
  — is still a later conversation with upstream. Unchanged in sharpness: it
  depends on someone else's roadmap, not on anything this map can settle.
- **Orphan policy.** What a page does when the theme is uninstalled but its
  hero blocks remain. Inherited from the contract's open items.

## Out of scope

- **Format negotiation for Plone images.** Serving AVIF/WebP/JPEG from one
  `<picture>` needs derived formats generated and stored outside Plone's scale
  machinery, plus `type=` support in `Img2PictureTag` that does not exist.
  Ruled out on [ticket 05](issues/05-image-delivery.md) — a lot of new surface
  for one block, and properly an upstream concern.
- **Building `plone.blicca.heroblock`**, the generic hero reference block — it
  stays unbuilt until a second site actually wants a hero.
- **Extracting `@plone-collective/blicca-block-tools` and the
  `blicca_block_addon` scaffold.** Both were decided on aurora-block-addons
  ticket 08 and neither exists. This effort imports
  `wrapper/build-plugins/scope-wrap.ts` directly instead; packaging the tooling
  is its own effort, best driven by the second brand block.
- **Publishing the block to npm** — the single-ecosystem exemption above.
- **Authoring the derico.de homepage content**, or migrating the mockup's copy
  into Plone. The destination is the block, not the page.

- **Fixing the inert block-width picker in the floating toolbar.**
  `BlockWidthToolbarButton` renders for every ploneBlock and offers all four
  widths, but `setBlockWidth` excludes `PLONE_BLOCK_TYPE`, so no option does
  anything. Found on [ticket 11](issues/11-per-type-default-block-width.md).
  Pre-existing and Blicca-wide — it hits the native image, teaser and listing
  blocks identically — so fixing it is not this hero's work and not this map's
  destination. Blicca's to file. (Whether the toolbar even appears for a *void*
  selected ploneBlock is unconfirmed; if it does not, there is nothing to fix.)

- **Promoting a generic `textarea` widget into Blicca.** `QuantaTextAreaField`
  ships unregistered (`@plone/components/src/index.ts:77`) and every schema
  field without a widget falls back to a single-line input. Ticket 02 chose to
  namespace the hero's own (`derico_textarea`) rather than claim the generic
  key from a theme; whether Blicca should register one deliberately is Blicca's
  call, not this effort's.

- **Aurora's own object_browser schemas carry dead keys.** `mode: 'image'`
  (teaser `preview_image`), `mode: 'link'` (image `href`) and `allowExternals`
  have no consumer in Aurora or Blicca — so upstream's teaser image override
  accepts any content type, and no field anywhere can offer an external URL.
  Found on [ticket 13](issues/13-object-browser-forward-props.md) while
  choosing the envelope. The hero is unaffected: it declares `single` plus
  `selectableTypes`, and its links are content picks by design. Whether Blicca
  should restrict the teaser's image override, or implement an external-URL
  affordance, is Blicca's call under the mirror rule — not this map's
  destination.

- **`path_of` mangles non-http schemes.** `urlparse("mailto:…").path` is
  truthy, so the scheme is stripped rather than the value returned whole.
  Pre-existing and latent in `teaser_block` / `video_block`; found on
  [ticket 12](issues/12-picture-helper-api-status.md) while testing the
  promotion. The hero is unaffected — its links are object_browser content
  picks, always http(s) — and changing a function with four existing call
  sites, one of them an external-video URL path, is a regression risk in a
  ticket about images. Documented as a limit in §5.2 and pinned by a test;
  fixing it is Blicca's call, not this map's destination.

- **Blicca's diagnostics lists a role twice.** "Who may insert" renders
  `Manager, Manager, Site Administrator` for the hero's permission:
  `permission_roles` sorts what `rolesForPermissionOn` returns but does not
  deduplicate it, and the grant is both declared and acquired. Found on
  [ticket 10](issues/10-verify-end-to-end.md). Cosmetic, one word to fix, and
  in another package's diagnostics view — Blicca's call, not this map's
  destination.
