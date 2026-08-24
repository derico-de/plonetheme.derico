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
- **The block fixes its own width; the author never chooses it.** No per-`@type`
  default width exists today in either half (ticket 11), so this needs building.
- Any GenericSetup profile XML change gets an upgrade step, even at `1.0.0a1` —
  scaffold via `plonecli add upgrade_step`, narrowed to the affected import step.

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

## Not yet specified

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

- **Promoting a generic `textarea` widget into Blicca.** `QuantaTextAreaField`
  ships unregistered (`@plone/components/src/index.ts:77`) and every schema
  field without a widget falls back to a single-line input. Ticket 02 chose to
  namespace the hero's own (`derico_textarea`) rather than claim the generic
  key from a theme; whether Blicca should register one deliberately is Blicca's
  call, not this effort's.
