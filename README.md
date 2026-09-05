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

### Aurora block backgrounds

Clara is not the only upstream the token layer writes to. Blicca's
`backgroundColor` style field lets an author put any Aurora block on a
**named** palette slot — never on a colour — and reads one
`--aurora-block-*` custom property per slot, with a generic slate baked in
as the fallback. `derico.css` §8 fills all three:

| slot | value | measured |
|---|---|---|
| Grey | `--derico-surface` `#ebf6f8` | ink 15.62:1, link 5.44:1 |
| Accent | `--derico-band-soft` `#d2f2fa` | ink 14.60:1, link 5.09:1 |
| Dark | `--derico-brand-deep` `#004553`, foreground `--derico-ground` | 10.33:1 |

Accent is the *soft* cyan, not `--derico-band` — the committed band the
design paints `.section--band` with. That band takes ink text and quiet ink
links by design, and an ordinary link on it measures 4.27:1. A section whose
content the designer chose can honour that convention; a slot in a picker
takes whatever an author drops on it, so it gets the step links already
clear. `tests/test_aurora_block_backgrounds.py` states that as a
measurement, and fails the day the link step darkens enough to revisit it.

## The header

The one part of the theme that is neither a token nor a block. Clara's header
elements carry the design's bar through `static/header.css` and
`static/header.js` — one bundle, `plonetheme-derico-header` — plus a searchbox
template registered on derico's own layer.

It is a separate sheet for the reason `derico.css` is guarded to stay a token
sheet: the design's bar is a **composition**, not a set of values. Clara stacks
a logo row over a full-bleed navigation bar and parks an always-open search
form in the bar's end lane; the design puts logo, navigation and utilities on
one 6rem row, centres the navigation in the viewport, and folds the search into
a single magnifier. The values are still tokens — every colour, step and face
in the sheet is a `--derico-*` or `--plone-*` name — but the rules are
component rules.

| width | header |
|---|---|
| ≤ 48rem | the design's mobile bar: logo, menu pill, magnifier; search opens as a row beneath, the menu as Clara's accordion under that |
| 48–70rem | a two-row header the design never drew — logo and utilities, then the centred navigation bar. What Clara's markup does between the two, made deliberate |
| ≥ 70rem | the design's desktop header: one row, logo at the start, navigation centred in the viewport, search and login at the end |

Clara's mega panel is already the design's three-zone panel and is untouched,
as are the navigation's face, size and weight.

### The search

**Not in the mockup.** A static reference site needs no search; a Plone site
has one, and the design had nowhere to put it. One magnifier at the bar's end,
and the field grows out of it — an overlay sliding out to the left on the wide
layouts, a full row under the bar on the narrow one. The mockup gained the same
control in the same place, so the design source and the theme still describe
one header.

The disclosure is the same pure-CSS `.opener` checkbox Clara's mega menu uses,
so **search works with no JavaScript at all**. `header.js` adds only what a
stylesheet cannot: focus into the field, Escape and outside-click to close, and
one open thing at a time in the bar. The form keeps the base template's ids,
names and classes — `pat-livesearch` and `@@search` read them — so only how it
opens changed.

`browser/templates/searchbox.pt` is registered under the base provider name on
`IPlonethemeDericoLayer`, which extends `IPlonePageletlayoutLayer` (Clara's own
move for its globalnav): that makes the override unambiguously more specific
than the base registration, with no change to the stored layout order and
nothing for an upgrade step to migrate.

## The footer

All three stock footer rows are hidden (profile version 1011), because the
design closes a page with its own band — the wordmark line, the postal
address, phone, email and the Impressum link — authored as footer blocks.

| row | why it goes |
|---|---|
| `siteactions` | Sitemap / Accessibility / Contact, straight from `portal_actions`. Authored content here: the Actions block puts a category of portal actions on a page as designed links, so the stock row renders them twice |
| `copyright` | Plone's own copyright and GPL notice, not derico's signature |
| `colophon` | the „Powered by Plone" badge |

Nothing about Plone's licence obliges either attribution row to be on the
page; the attribution that matters is in the source and the package metadata,
which this does not touch.

**Hidden, not removed from the order** — hiding is what the layout manager
offers for an element it should keep knowing about, so
`@@manage-layout-viewlets` shows each row as hidden and can put it back, and
the base package's parity test still finds the names in the stored sequence.
`profiles/uninstall/viewlets.xml` un-hides all three, so a site that drops the
theme gets its stock footer back.

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
