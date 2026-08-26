# Changelog

## 1.0.0a1 (unreleased)

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
