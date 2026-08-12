# Changelog

## 1.0.0a1 (unreleased)

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
