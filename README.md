# plonetheme.derico

**„Jahresringe" — the derico.de brand, as a token layer on
[plonetheme.clara](../plonetheme.clara).**

Almost all of the theme is one stylesheet of custom properties:
`src/plonetheme/derico/static/derico.css`. No Sass, no Bootstrap compile, no
template overrides — Clara ships all of that, and derico mostly moves the
values its rules read. Plus one brand mark, which is the single part of the
design that cannot be a token.

The exception is the **brand blocks**: designs that are not a value Clara's
rules already read, so they ship their own component rules and their own
editor-side JavaScript. The Derico Hero is the first. Their source lives in
[`bundle-src/`](bundle-src/README.md) and their built, committed artifacts in
`src/plonetheme/derico/static-blocks/` — installing the theme never requires
Node, but changing a block requires a rebuild.

```
plone.pageletlayout   rendering machinery + markup contract, no CSS
      ↑
plonetheme.clara      the one compiled bundle: @layer, Bootstrap 5.3,
                      primitives, --bs-* bridge, components, token defaults
      ↑
plonetheme.derico     ~60 lines of :root, a logo, and the brand blocks
```

## Install

```bash
uv sync --extra test        # sources/ symlinks Clara and plone.pageletlayout
```

Then install *Plonetheme Derico* from the Add-ons control panel. It pulls in
Clara, which pulls in `plone.pageletlayout`.

## The design

The source of record is `docs/design/derico.de/` — the
„Jahresringe" system document and the bilingual multi-page reference
implementation the theme is built against. Two colours carry it: exact brand
cyan `#039fba` (OKLCH hue 215.55) and a copper complement; Literata over Source
Sans 3; flat and hairlined, no shadows.

## The Derico Hero

The first brand block: the homepage opening from the mockup — photograph,
kicker, headline, lede, two calls to action, and the rings figure with its
four-entry legend. Installing the theme registers it; nothing else is needed.

It is deliberately **inflexible**. It implements one design template, allows
the text and images that template needs, and offers the author **no options** —
no width control, no palette variant, no "hide the rings" toggle. A variant is
added when the design asks for one, never in anticipation. That is the standing
principle for every brand block, not a quirk of this one.

### Inserting it

Only **Manager** and **Site Administrator** see it in the slash menu — the
`plonetheme.derico: Insert Brand Block` permission, granted at the site root in
`profiles/default/rolemap.xml` and changeable through the *Security* control
panel. This is **guidance, not security**: the block stays authorable through
the REST API, and a user without the permission still sees an existing hero
rendered normally rather than as an unknown-block placeholder.

### Authoring one

| field | notes |
|---|---|
| kicker, headline, lede | plain text; edited in the sidebar, previewed live in the canvas |
| primary / secondary link | each renders only when it has **both** a label and a target |
| wide image, portrait image | two Image content items, two crops — see below |
| ring legend | exactly **four** `{title, subtitle}` pairs; the numerals come from position and the last ring is always the "now" one |

Nothing is required. A half-filled hero saves and previews; the editor lists
what is still missing rather than refusing.

**Upload the two crops as WebP.** Plone switches **resolution** but never
**format** — `Img2PictureTag` emits no `type=`, and `plone.scale` preserves
WebP while coercing anything that is not PNG to JPEG. So the format the hero
serves is the format that was uploaded, and WebP-in/WebP-out recovers most of
the mockup's byte saving for free.

**Two crops, not two sizes.** Plone's named scales give variants of one crop,
never art direction, so the wide and the portrait framing stay two uploads. One
crop alone renders at every breakpoint and `object-fit: cover` centre-crops it;
that is a legitimate choice, not a defect, and there is no per-image
`object-position` to tune — the honest fix for a badly framed hero is at the
upload.

**Budget the headline at about 14 characters per line.** The ramp is
`clamp(2.4rem, 1.4rem + 5cqi, 5rem)` over a `14.5ch` measure, and the layout
guarantees the text never clips even at a 320px viewport — but a very long
compound word will shrink the line it sits on rather than break. This is a
budget, not a validator: nothing stops you exceeding it.

### What installing it changes

Beyond the block record itself:

- **one new image scale**, `enormous 2600:65536`, **appended** to
  `plone.allowed_sizes`. Only ever appended: stock templates and other add-ons
  hardcode `large`, `preview`, `mini` and friends by name.
- **two picture variants**, `hero-wide` and `hero-portrait`, added by a
  setuphandler because `plone.picture_variants` is a JSONField and
  GenericSetup has no syntax for one. Both are hidden from the richtext
  editor's variant picker, where they would be meaningless.
- **`plone.blicca.auroraeditor`**, installed as a profile dependency. It is
  the editor the block mounts in and the source of the promised rendering API
  the public view imports, so the theme depends on it hard and with a version
  floor.

Uninstalling removes the block record but **leaves the scale and the variants
in place** — removing a scale that content elsewhere has come to reference is
worse than leaving a harmless extra rung in the ladder.

## What is overridden — and what deliberately is not

Every override is one of two kinds, and nothing else qualifies:

1. the token carries **Clara's own identity** (Plone blue, Klarsicht amber), or
2. the design **names a different value** and the difference is visible.

| inherited untouched | why |
|---|---|
| the entire type scale | Clara's `--clara-text-*` steps are already bit-identical to Jahresringe's, down to the 15px label floor and the flat 1rem body |
| both fonts | Literata + Source Sans 3, self-hosted by Clara; derico ships no font files |
| `--plone-measure` (76rem), all `--plone-radius-*` | already identical |
| `--plone-space-3xs … l` | already identical; only the three section-rhythm steps differ |
| the **entire error/danger family** | the design's red, `oklch(0.45 0.18 28)`, resolves to `#a2080c` — Clara's `--clara-error`, exactly |
| every layout primitive, `--bs-*` bridge line and component hook | that is the point of the base |

What *is* overridden: the cyan ladder, the copper accent (which takes over
Clara's amber role wholesale, so the CTA, mega-menu accents, footer link hover
and published-state marker all follow with no rules restated), the warning
family's hue-dependent steps, the info tint, the success green, a flat footer
ground, three `--plone-*` roles whose *meaning* differs from Clara's mapping,
and the three long space steps. Each one carries its reason in `derico.css`.

`--clara-on-amber` is a good example of an override that is not cosmetic:
Clara's amber is light enough to take an ink label, copper is not — ink on
copper measures 3.63:1, so the near-white label is required, not preferred.

## Verifying the claim

`tests/test_override_minimality.py` is the guard, and it parses Clara's
**compiled bundle**, not its Sass — what has to be overridden is decided by
what lands in the page.

- the sheet declares nothing but custom properties, under `:root` and one dark
  block; no `@layer`, `@import`, `@font-face` or `!important`
- every override targets a token Clara actually defines
- **no override restates a value Clara already resolves to** (both sides
  normalised to sRGB, so an `oklch()` that happens to equal Clara's hex is
  caught)
- every token listed as inherited is *not* overridden — and still matches the
  design; if Clara retunes one, the test says so and names it
- no Klarsicht blue survives anywhere in the resolved token layer
- WCAG ratios measured on the resolved sRGB values, light and dark
  (`tests/test_color_contrast.py`)

```bash
uv run pytest tests -q          # 226 tests
```

Live verification (2026-07-28), a Plone 6.2 instance on port 8088 with the
profile installed, measured through headless Chrome: every token resolves to
the Jahresringe ladder, body renders at 16px / 1.65, h1 in Literata, footer flat
on the page ground, and **zero Plone-blue values anywhere on the rendered page**.

## Findings against the base

All three were found by being the *second* theme on Clara — none is visible from
inside Clara, where the tokens and the compiled values agree. All three were
fixed in `plonetheme.clara` rather than worked around here, because any theme on
Clara hits them identically (its architecture doc, principle 1: an adjustment
that forces a downstream override is a bug in the contract).

1. **Bootstrap's compile-time `$primary` reached seven components.**
   `.pagination`, `.nav-pills`, `.progress-bar`, `.list-group`,
   `.dropdown-item.active`, the outline buttons and the form-control
   checked/indeterminate/range-thumb properties all painted `#0083be` — 13 blue
   spots measured on a live derico page. Four are plain properties with no
   `--bs-*` knob, so no token override could have reached them. Fixed in
   `_clara-bridge.scss` §3; §5 of `tests/test_override_minimality.py` keeps
   derico's stake in it. **Residual, out of reach by design:** `--bs-*-rgb` and
   the `.text-primary` / `.link-primary` / `.table-primary` utilities that read
   them cannot be expressed as a var. Clara's contract markup uses none of them.

2. **Clara's dark mode never went dark.** `[data-bs-theme="dark"]` scores 0,1,0,
   the same as `:root`, so `_clara-brand.scss`'s later `:root` undid the
   defaults' dark background, surface, text, muted, border and on-primary.
   Clara's contrast test modelled the overlay in import order — a cascade the
   browser never runs — so it passed throughout. Fixed by doubling the attribute
   selector; scoped `<div data-bs-theme="dark">` regions still work.

3. **The CTA outline was a value with no token behind it.** `.clara-button`
   hard-coded a 1.5px ink hairline around the pill — a Klarsicht judgement the
   Jahresringe button spec does not share (copper clears 4.60:1 on the page
   ground unaided). Dropping it needed a component rule in a sheet whose whole
   value is having none. Clara now exposes `--clara-button-border-color`,
   defaulting to `var(--clara-ink)` so its own look is unchanged, and derico
   points it at the copper fill. Kept as a *colour*, not `none`: the border box
   has to survive so the pill keeps its metrics and still has an edge in
   forced-colors mode.

## Accepted deviations

- **Dark mode is light-only by design.** Jahresringe sets `color-scheme: light`.
  derico still flips the identity roles so Plone's toolbar switch never renders
  blue chrome, but the dark neutrals stay Clara's.
- **Roboto Slab is not shipped.** It is scoped to the mockup homepage's service
  atlas — page-level content styling, not theme chrome.

## Development

```bash
uv run pytest tests -q                       # full suite
uv run pytest tests/test_override_minimality.py -q   # the minimality guard
```

## License

GPL-2.0-or-later

## Author

Maik Derstappen <md@derico.de>
