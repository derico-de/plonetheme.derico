# Changelog

## 1.0.0a1 (unreleased)

- **The Promo block is a declared dependency** (profile version 1008).
  Installing derico now installs `derico.blicca.promoblock`, and the upgrade
  step installs it on sites that predate the declaration. The list the steps
  install from moved to `upgrades/base.py` alongside the guard, and
  `test_setup` holds it to `metadata.xml`'s `<dependencies>`, so a dependency
  added to one and not the other stops being a site that installs clean and
  upgrades incomplete.

- **Every declared dependency is installed on upgrade** (profile version
  1007). `metadata.xml` names three add-on profiles as dependencies, and
  GenericSetup applies dependency profiles on install only, so a site carried
  whichever ones were declared the day derico was installed there and silently
  missed the rest: the editor the brand blocks mount in, the base theme, the
  fragment block. 1005 closed that for `collective.fragmentsblock` alone; this
  step generalises it, so whether a site is missing an add-on derico needs no
  longer depends on which version it was installed at. Guarded per product, so
  re-running it is a no-op rather than a log full of install errors.

- **The contact band closes every page** (profile version 1006). The design's
  „Erstgespräch vereinbaren" section — heading, one sentence, a call to action
  and a mail link — is now a chrome pagelet in Clara's whole-body layout,
  placed after the content and Clara's sub-navigation and before the footer
  rows, exactly where all 22 mockup pages put it. A pagelet and not a brand
  block because there is nothing to author: an author who had to place it on
  every page would eventually forget one.

  Its ground is the Aurora palette's **accent slot**, not the design's
  committed `--derico-band`, and it opens with no margin and no rule. That is
  the whole point: a page whose last block sits on the accent slot flows into
  the band with no seam, so a designed page can close on one continuous
  surface. The second half of that is a `:has()` rule dropping
  `.element-body`'s closing padding under such a block — the strip of page
  ground between two identical accents would read as a rendering fault. Only
  under `accent`; `grey` and `dark` keep the separation the strip gives them.

  Nothing about the two links is written into the markup. The call to action
  resolves `plonetheme.derico.contact_page`, a path relative to the navigation
  root (default `contact`, the id Plone's own starter contact page ships
  with), and it is dropped on the page it points at. The mail address is
  Plone's `plone.email_from_address`, because a theme that shipped its
  author's address would mail derico from every site that installed it. Copy
  is translatable, with the design's German in `locales/de`.

  Styling is a third theme bundle (`static/contact.css`), on the same footing
  as the snippets' sheet: derico.css is guarded to stay a token layer. It
  carries one rule that is a repair rather than a design — Clara's
  `a:not(.btn)` outranks its own `.clara-button`, which put the call to
  action's label at 1.4:1 on its copper fill; remove it when Clara stops
  overriding itself. `--derico-text-heading` joins the published aliases, and
  the token-usage guards now read the theme's own sheets as well as the
  blocks'.

- **Aurora block backgrounds are brand colours** (`derico.css` §8). Blicca's
  `backgroundColor` style field lets an author put a block on a named palette
  slot and reads one `--aurora-block-*` custom property per slot; unset, all
  three painted Blicca's generic slate. The token layer now fills them from
  the Jahresringe ladder — Grey on `--derico-surface`, Accent on
  `--derico-band-soft`, Dark on `--derico-brand-deep` with the page ground as
  its foreground. Accent is deliberately the soft cyan rather than the
  committed `--derico-band`: that band takes ink text and quiet ink links by
  design and an ordinary link on it measures 4.27:1, which a designed section
  can honour but a picker slot cannot. No profile change — a value-only edit
  to the token sheet. `tests/test_aurora_block_backgrounds.py` holds the slot
  names against Blicca's own table and every pairing against AA.

- **The Derico Snippet block is retired** (profile version 1004). It and the
  generic fragment block delivered the same thing once 1003 made derico a
  fragment provider — one ornament, one file, injected verbatim — so the brand
  block goes and `collective.fragmentsblock`'s `fragment` stays: the block
  registration, its bundle entry, its server view and its record are gone.
  Stored nodes are **converted, not dropped**: `@type` becomes `fragment` and
  the `snippet` key becomes `fragment`, which is the whole difference between
  the two blocks' data, so a converted page renders exactly as it did. Two
  details preserve appearance rather than data — an absent or unrecognised
  choice becomes the Balkenlage the old block fell back to, and the width its
  `defaultBlockWidth` used to materialise is filled in where a node lacked it.
  The corpus, its stylesheet and its bundle are untouched; only the machinery
  that injected them changed.

- **derico is the first fragment provider** (profile version 1003). The same
  `snippets/*.html` corpus is now published for `collective.fragmentsblock`'s
  generic **fragment** block as well: `fragments.py` registers the directory as
  a named `IFragmentsProvider` utility for classic rendering, and a second
  bundle entry (`bundle-src/src/fragments/`) publishes id, title and markup
  into `@plone/registry` so the editor renders it client-side. One corpus,
  three readers, still no copies — the editor entry restates the map only
  because a module shared between two bundles becomes a chunk no record can
  declare, and `tests/test_fragments.py` holds the restatement in lockstep with
  the files on disk. Its record carries no `types`: it registers no block, it
  fills the fragment block's picker. The Derico Snippet block is untouched;
  which of the two an ornament should be placed with is a question for the day
  the fragment block has run in production.

- **The Derico Snippet: one brand block for the design's static ornaments**
  (profile version 1002). The Balkenlage divider and the Ständerwerk frame are
  finished markup with nothing to author, so they share a single generic block
  — a `derico-snippet` node whose one sidebar choice picks the fragment —
  rather than each cloning the hero's whole registration stack. The fragments
  live once, as `snippets/*.html` in the Python package: the server view
  injects the file, the editor bundle imports the very same file `?raw`, and
  the two surfaces cannot drift because neither owns a copy. Adding the next
  ornament is one HTML file, one import, one schema choice. The styling is the
  theme's, not the block's: `static/snippets.css`, shipped as its own bundle
  and hand-wrapped in the same `@scope` the block pipeline would have emitted,
  so it survives the editor's scoped preflight without a build step. The
  mockup's scroll-in animations are deliberately not ported — the design
  defines the JS-less state as the finished one. Same insert gate as the hero;
  `defaultBlockWidth: 'layout'` fixes both ornaments at the shell width the
  mockup places them at, with the schema offering no way to countermand it.

- **A freshly inserted Derico Hero already carries the mockup's words.** Kicker,
  headline, lede, both link labels and all four ring-legend pairs arrive filled
  in with the German homepage copy from `docs/design/derico.de/site/de/`, so an
  author edits eight fields instead of inventing them and can see which field
  is which the moment the block lands. Every word is stored on the block and
  every word is editable — a starting draft, not a fallback: the seed is
  written exactly once, keyed on whether the node carries any hero key at all,
  so clearing a field leaves it cleared. Ticket 02 put this default on the
  slash-menu entry; nothing writes it there (Aurora inserts a node carrying
  `@type` and nothing else, and `blocksConfig` has no initial-data hook), so it
  happens in the block's own `edit` component instead. The site-specific fields
  — both link targets and both crops — are deliberately left empty, and the
  canvas nag goes on naming them until they are picked.

- **The hero's contrast guarantee is structural, not tuned against one
  photograph** (hero tickets 18/20/21/23). Every text element and the rings
  disc now meet their WCAG threshold over *any* upload, because each one's
  adjacent colour is a value this package declares rather than a pixel the
  author supplies: an opaque card under the ring legend, a feathered scrim over
  the copy, and a ground-coloured halo beneath every ring stroke. No colour
  changed and no brightness cap was imposed — both were costed and rejected.
  The wash keeps its composition role and stops being load-bearing: it is cut
  away at the same 50% boundary the scrim is painted from, one number used
  twice from opposite sides, so the two can never drift into stacking (0.72
  under 0.926 composites to 0.98, a solid copy panel). The disc had been
  failing over the *shipped* design photograph, not merely a hypothetical one —
  3.28% of the rings band for the copper strokes and 10.27% for the is-now
  cyan. `hero-view.e2e.js` loses its three named contrast exceptions, which is
  the acceptance criterion for the whole change.

- **The hero states its own body type** (hero tickets 17/22): `font-family` and
  `line-height` from `--plone-font-body` / `--plone-leading-body`, which
  already carry the design's exact values. Blicca states its Tailwind stack on
  `.aurora-blocks-view` only, so a theme-layer rule would have fixed the
  published view and broken canvas/view parity; the block's scope-wrapped sheet
  reaches both from one declaration, and the canvas assertion in
  `hero-editor.e2e.js` is what pins that. Neither `derico.css` nor
  `blocks_view.css` is touched.

- **The marker numerals moved from the pixel probe to the value test.** They
  are the one text in the hero whose backdrop is entirely element-painted — a
  ground glyph on an opaque copper chip — so what the probe was reporting was
  the glyph's antialiased edge overlapping its own 2px border, not a
  photograph. Raising the speckle threshold would have blunted the guard for
  every element that really is over the photograph.

- **`tests/clara_css.py` now descends into `@container`.** Every rule at the
  hero's wide breakpoint — where ticket 06 §8 deliberately put a container
  query rather than a media query — had been invisible to the stylesheet tests,
  which read as covering the sheet while covering half of it.

- **The upgrade profile is no longer offered as an installable add-on.**
  `plonetheme.derico.upgrades:1001` has to be an EXTENSION profile for
  `genericsetup:upgradeDepends` to import it, and the add-ons control panel
  offers every EXTENSION profile it is not told to hide — so it stood next to
  the theme itself, inviting an administrator to apply a migration out of
  order. `HiddenProfiles` now names it. The guard is the *enumeration* in
  `test_every_upgrade_profile_is_hidden`, which reads the registered profiles
  out of `portal_setup` rather than carrying a hardcoded version list, so the
  next `plonecli add upgrade_step` cannot reintroduce the gap silently. A
  `getNonInstallableProducts` blanket would have hidden future profiles too
  and was deliberately not taken: it states the same answer a second way, and
  it is the second way that would let the enumeration pass over a
  `HiddenProfiles` that had stopped naming them.

- **Browser tests for the hero, in `e2e/`.** Two playwright-core scripts and
  the fixture and measurement modules they share: `hero-editor.e2e.js` drives
  a real `@@aurora-edit` — insert, author every field, save, reload, the
  insert gate as an ordinary editor sees it, one React, `<html lang>`, no
  clipping at 320/375 — and `hero-view.e2e.js` measures the published page
  against `docs/design/derico.de/site`, served from this repository, in the
  same browser at 1440/900/375/320. Contrast is read from the pixels each
  glyph actually covers (the hero paints ground, then photograph, then wash,
  so no ancestor's `background-color` is what the reader sees), reported as
  worst ratio, median and the share of the glyph area below the threshold.
  Two known gaps are printed rather than asserted, each named element by
  element so a new failure still fails the run.

- **The Derico Hero's server half — the block is now installable and rendered.**
  `@@aurora-block-derico-hero` draws the published page from the same markup
  tree and the same degradation table as the editor half, over the contract's
  promised `BaseBlockView` / `image_source` / `path_of`. The photograph is one
  `<picture>` art-directed across two uploads: `Img2PictureTag` is called once
  per crop and the portrait's `<source>` elements are spliced in front of the
  wide ones, because Plone's named scales give variants of one crop and two
  toggled `<picture>` elements would download both. It is the page's LCP image,
  so it ships `fetchpriority="high"` and explicitly not `loading="lazy"` —
  instead of a `<head>` preload, which would couple the theme's head to block
  content. A crop that cannot become a `<picture>` (an SVG, or a reference that
  never went through the widget) falls through one code path to a plain `<img>`
  in the same element, so `object-fit` frames it identically.

- **Packaging: a block record, a permission, a scale rung and two variants.**
  The `IAuroraBlockAddon` record declares the `block_api` **floor** the block
  needs rather than the host's current version, and names the shared
  `blocks.css` every future brand block's record will also name. Insert is
  gated on a new `plonetheme.derico: Insert Brand Block`, held by Manager and
  Site Administrator — `cmf.ManagePortal` is Manager-only in stock Plone and
  would have locked out the very role the block is for. Imaging is split by
  what GenericSetup can carry: `enormous 2600:65536` merges into
  `plone.allowed_sizes` through `registry.xml` with `purge="false"`, while the
  two `hero-*` picture variants come from an add-only setuphandler, because
  `plone.picture_variants` is a JSONField. Uninstall removes the record and
  deliberately leaves the imaging alone.

- **`plone.blicca.auroraeditor` is a hard, versioned dependency.** Both a
  Python requirement (`>=1.0.0a2`, the release carrying the promised rendering
  API) and a GenericSetup profile dependency — a Python dependency installs no
  profile, and a GS dependency reaches fresh installs only, so upgrade step
  **1001** installs the host, re-runs the `plone.app.registry` and `rolemap`
  import steps and adds the picture variants. Narrowed to those, not a blanket
  profile reload.

- **Contract §5.3 is satisfied by stock restapi, and now asserted rather than
  assumed.** No serialization transformer ships with this theme: restapi
  already resolves a nested `{"@id": …}` and injects `image_scales` beside it
  whatever the field is called, and strips it again on save. That is a claim
  about somebody else's code, and the day it stops being true the hero silently
  loses its resolution ladder and serves one full-size original to every
  visitor — so `tests/test_hero_view.py` pins both halves of the round trip.

- **The Derico Hero's editor half.** `bundle-src/` is a small pnpm/Vite
  workspace whose build emits committed artifacts into `static-blocks/`
  (`hero.js` + a scope-wrapped `blocks.css`), served as
  `++plone++plonetheme.derico.blocks`. Its entry point registers ONE block per
  bundle and returns the config object the loader requires, with
  `defaultBlockWidth: 'full'` — the whole of the full-bleed wiring, which works
  only because the block's schema deliberately declares no `blockWidth`. The
  sidebar widgets are namespaced (`derico_textarea`, `derico_ring_legend`,
  `derico_reference`) rather than claiming the generic keys in a global,
  last-wins registry. Both `edit` and `view` are implemented from one set of
  components, so the canvas and the published page render the same markup under
  the same `.derico-hero` root — never Aurora's `.block-derico-hero` wrapper
  stamp, which is only column-width in the canvas and would clip the breakout.
  27 vitest cases cover the seven-case degradation table and the registration
  contract; `tests/test_hero_sheet.py` adds nine that pin the shipped sheet's
  wrap ladder, stacking context and namespace containment.

- **The blocks are served, built and guarded.** `static-blocks/` is registered
  as `++plone++plonetheme.derico.blocks` — a second static directory, and
  `++plone++` rather than `++resource++`, because one directory under both
  directives would give every file two public URLs. `invoke build-blocks` and
  `invoke test-blocks` wrap the pnpm workspace, and a new CI job typechecks,
  tests and builds it, then runs `git diff --exit-code` over the artifacts:
  committed build output rots the moment someone edits source and forgets to
  rebuild, and that check is the only thing that makes committing it safe.
  `tests/test_block_addon_lockstep.py` pins the vendored `scope-wrap.ts` to
  upstream and will pin the declared `block_api` floor once the record lands.
  `bundle-src/README.md` carries the workspace's prose, because nothing
  hand-written may live in `static-blocks/` — the build wipes it.

- **`--derico-text-display` is no longer published.** The hero states its own
  `clamp(2.4rem, 1.4rem + 5cqi, 5rem)` — container-relative, because the hero
  is viewport-minus-toolbar for every logged-in user — instead of reading the
  alias, and it is the only block that sets a display-sized headline. That left
  the alias published and read by nobody, which the token layer's own guard
  calls dead weight: published, not hoarded. `derico.css` §3 now re-publishes
  three of Clara's private type tokens, and the alias returns the day a block
  reads it.

- **The token layer gains the two things a brand block cannot reach itself.**
  `derico.css` re-publishes Clara's private type tokens as
  `--derico-text-lede`, `--derico-text-label` and `--derico-font-display` —
  aliases, never values, so this file stays the
  theme's one seam onto Clara and a block sheet speaks only `--derico-*` and
  `--plone-*`. And it gains §7, the first rule in the sheet that is not a token
  declaration: when the Derico Hero is the *first* block on a blocks-view page,
  the breadcrumbs, contentheader and byline above it are hidden, so the hero
  sits flush under Clara's header hairline. It has to live here because a
  block's own stylesheet is scope-wrapped and `body` is rewritten out of its
  reach. Public view only — `@@aurora-edit` keeps its chrome. This narrows the
  "any selector beyond `:root`/dark" claim below: the minimality tests were
  widened, not dropped, and now also pin the rule to `display: none`, admit
  exactly one of it, and check that the published aliases really alias Clara
  and are really read by a block sheet.

- Remove the `plone.bundles/plonetheme-derico` registry records on uninstall
  (`profiles/uninstall/registry.xml`), so derico.css stops loading once the
  add-on is removed.

- **Re-base on `plonetheme.clara` and ship the „Jahresringe" identity as a pure
  token layer.** The package was an empty `backend_addon` scaffold; it is now a
  theme. `static/derico.css` is the entire stylesheet: one `:root` block plus a
  dark block, no Sass, no Bootstrap compile, no template or component overrides.
  The profile depends on `profile-plonetheme.clara:default`, the bundle depends
  on `plonetheme-clara`, and the brand mark is set as `plone.site_logo` by a
  post-install handler (an existing logo is never clobbered).

- **Minimality is enforced, not asserted.** `tests/test_override_minimality.py`
  parses Clara's compiled bundle and fails on a redundant override (both sides
  normalised to sRGB), an override targeting a token Clara does not define, any
  selector beyond `:root`/dark, any `@layer`/`@import`/`@font-face`/`!important`,
  a surviving Klarsicht blue in the resolved token layer, and drift in any of
  the 13 values derico deliberately inherits. `tests/test_color_contrast.py`
  measures WCAG on the resolved values in both modes. 98 tests.

  Inherited untouched because Clara already matches the design: the whole type
  scale, both fonts, `--plone-measure`, the radii, the short space steps, and
  the entire error family — the design's `oklch(0.45 0.18 28)` resolves to
  `#a2080c`, Clara's red exactly.

- Three gaps in the base, found by being the second theme on Clara and fixed
  there rather than worked around here — Bootstrap's compile-time `$primary`
  reaching seven components (13 blue spots on a live page, 0 after); a dark-mode
  cascade bug that meant `[data-bs-theme=dark]` never actually went dark; and
  the CTA's ink hairline, which had no token behind it and is now the
  `--clara-button-border-color` hook that derico points at its copper fill. See
  README, "Findings against the base", and Clara's changelog.
