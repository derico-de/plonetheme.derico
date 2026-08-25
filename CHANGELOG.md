# Changelog

## 1.0.0a1 (unreleased)

- **The token layer gains the two things a brand block cannot reach itself.**
  `derico.css` re-publishes Clara's four private type tokens as
  `--derico-text-display`, `--derico-text-lede`, `--derico-text-label` and
  `--derico-font-display` — aliases, never values, so this file stays the
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
