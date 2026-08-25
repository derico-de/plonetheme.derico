# Decide: what CSS the hero needs, and how it coexists with the theme

Type: grilling
Status: closed
Blocked by: —

## Question

Full-bleed is **settled** — `blockWidth: full`, riding Blicca's existing
viewport breakout on both surfaces (see the map's Notes; the mechanism for
declaring it is ticket 11). What remains is the block's own stylesheet.

- **What CSS to extract.** The mockup's `docs/design/derico.de/site/assets/site.css`
  carries `.home-hero`, `.hero-media`, `.hero-wash`, `.rings-figure`,
  `.rings-stage`, `.ring-markers`, `.ring-legend` and the tokens they read.
  Decide what belongs to the block, what Clara already provides, and what is
  already in derico's token layer — the block should ship the third category
  only.
- **The header overlap.** In the mockup the photograph runs to the top of the
  page, under a transparent site header. In Plone the hero is a block inside
  the content area, below Clara's header and beside the toolbar. Decide what the
  top edge becomes, since the mockup's composition cannot be reproduced exactly.
- **Scope-wrap.** Contract §6: one CSS asset, wrapped at packaging time to
  `(.aurora-editor, .aurora-editor-portal, .aurora-blocks-view)` with a donut
  limit. The breakout itself is Blicca's and stays out of this sheet, which
  removes the `@scope`-versus-negative-margin hazard — but confirm nothing else
  in the extracted CSS depends on escaping the scope.
- **Coexistence with the token bundle.** `derico.css` is deliberately
  **unlayered**, which is how it beats Clara's `@layer tokens`. The block's
  scope-wrapped sheet is also unlayered. Work out the cascade between them and
  fix the load order deliberately rather than discovering it later.
- **The type floor.** Nothing renders below 15px, and the ring legend is HTML
  beneath the SVG precisely because SVG text scales with the graphic. Whatever
  comes out of this ticket keeps that contract.

## Answer

Three of the ticket's premises were wrong, and correcting them is most of the
decision.

**There is no header overlap.** The mockup's `.site-header` is
`background: var(--ground)` with a `border-bottom` hairline (site.css:190), and
`.home-hero` follows it in normal flow. The photograph never runs under the
header. The real top-edge problem is Plone's: `blocks_view.pt` deliberately
leaves the title/description slots unfilled, so Clara renders breadcrumbs,
`.element-contentheader` and the byline *above* the first block.

**Load order needs no fixing — it is structural.** `main_template.pt:28` emits
`plone.htmlhead` (bundles, so `derico.css`); `:35` emits `style_slot`, which is
where `blocks_view.pt` puts `blocks_css_url` and then the add-on sheets. The
block sheet always lands after `derico.css`, both unlayered. It also barely
matters: `derico.css` declares on `:root`, the block sheet declares on elements
inside the block, and custom properties resolve by inheritance proximity, not
by specificity or order. Nothing to configure; record it and move on.

**Reusing Clara's component rules would break surface parity.**
`scope-wrap.ts:47` flattens `@layer` out of the editor bundle, so the editor's
Tailwind preflight ships **unlayered and scoped**, while `.clara-button` lives
in `@layer components`. Unlayered beats layered: inside the canvas preflight's
`button { background-color: transparent }` wins over Clara's fill, while on the
public view Clara wins. Same markup, two appearances — the thing §6.1's
anatomy-class parity exists to prevent.

Two hazards checked and cleared: the editor bundles
(`aurora-remote-*.css`, `index-*.css`) declare **no** `--plone-space-*`,
`--plone-text-*` or `--clara-*` of their own, so derico's `:root` ladder
inherits cleanly into the canvas; and `:scope.aurora-blocks-view …` works as a
deliberate one-surface seam (a bare `.aurora-blocks-view …` would not — inside
`@scope` it looks for a descendant).

### The three categories

The ticket asked what belongs to the block, what Clara provides, and what the
token layer provides. The boundary that came out of it:

- **Clara's *tokens* are inherited** — the type scale, the space steps,
  `--plone-radius-pill`, `--plone-ease-out-quint` (bit-identical to the
  mockup's `--ease-out`), `--plone-measure` (76rem, bit-identical to
  `--site-max`). The block restates none of them.
- **Clara's *component rules* are not reused.** `.clara-button` /
  `.clara-text-link` are `@layer components` and lose to the scoped preflight
  in the canvas. The block owns its CTA and quiet link.
- **The block ships everything else**, including the whole `--hero-*` palette,
  which exists in neither Clara nor `derico.css`.

### Decisions

1. **Page chrome (the top edge).** `derico.css` gains a chrome-suppression rule
   mirroring Clara's own `body:has(.clara-home)` treatment: when the hero is
   the **first** block —
   `body:has(.aurora-blocks-view > .block:first-child.block-derico-hero)` —
   hide `.element-breadcrumbs`, `.element-contentheader` and
   `.element-byline`/`#section-byline`. The hero then sits flush under Clara's
   header hairline, exactly as in the mockup; no gap is added. It has to live
   in `derico.css` because `scope-wrap.ts:41` rewrites `body` to
   `:where(:scope)`, putting `<body>` permanently out of the block sheet's
   reach. **Public view only** — the rule keys on `.aurora-blocks-view`, so
   `@@aurora-edit` keeps its chrome; the edit page is a working surface where
   the title and breadcrumbs orient the author.

2. **The hero palette lives in the block sheet, on `.block-derico-hero`.**
   `--hero-ground`, `--hero-ink`, `--hero-ink-soft`, `--hero-copper`,
   `--hero-ring`, `--hero-ring-now`, `--hero-rule` and the two washes are this
   block's composition, not derico's vocabulary — no other surface uses them.
   Renamed `--derico-hero-*`, and declared on `.block-derico-hero` itself
   rather than on `:where(:scope)`, so they never leak into the scope root every
   other add-on sheet shares. Promote to `derico.css` only if a second brand
   block actually wants the wash.

3. **Clara's private type tokens are reached through `derico.css`.**
   `--clara-text-display`, `--clara-text-lede`, `--clara-text-label` and
   `--clara-font-display` have no `--plone-*` equivalent (only `--plone-text-s`
   / `--plone-text-xs` alias the label). `derico.css` re-publishes them as
   `--derico-text-display`, `--derico-text-lede`, `--derico-text-label`,
   `--derico-font-display`; the block sheet speaks only `--derico-*` and
   `--plone-*`. `derico.css` is already the single seam onto Clara — it writes
   ~30 `--clara-*` tokens — so a Clara rename breaks one file, not two.

4. **Class names stay the mockup's; every selector descends from
   `.block-derico-hero`.** `.kicker`, `.lede`, `.button`, `.quiet-link`,
   `.action-row`, `.rings-figure`, `.rings-stage`, `.rings-disc`,
   `.ring-markers`, `.ring-legend` are generic and the scope root is shared
   territory, so descent — not renaming — removes the collision. Keeping the
   names identical to the mockup is what keeps the two sheets diffable, and the
   mockup is the design's source of record.

5. **The block owns its CTA and quiet link**, using the mockup's `.button` /
   `.quiet-link` rules painted with `--derico-copper*` / `--derico-hero-ink`.
   ~12 declarations buys identical output on both surfaces. Reusing Clara's
   classes was only "ship what Clara doesn't provide" on paper:
   `.clara-text-link` is `color: var(--clara-ink)`, invisible on the dark wash,
   so it needed overriding anyway.

6. **Animations: public view only.** The animation *rules* are written
   `:scope.aurora-blocks-view .block-derico-hero …`, so the copy does not
   re-settle and the rings do not re-grow on every keystroke in the canvas.
   `@keyframes` is hoisted out of the scope wrap by `scope-wrap.ts:32`, i.e.
   name-global across the whole page, so both are renamed `derico-hero-settle`
   and `derico-hero-grow-ring`. The `prefers-reduced-motion: no-preference`
   guard is kept verbatim.

7. **The inner grid re-establishes the container itself.**
   `.block-derico-hero .home-hero__grid` gets
   `width: min(100% - clamp(2rem, 6vw, 6rem), var(--plone-measure))` with
   `margin-inline: auto` — the mockup's `.shell` formula folded in, using
   `--plone-measure` (76rem) rather than a new token. No `.shell` element and
   no `.shell` class, per decision 4.

8. **Container queries, not media queries, for the 56rem switch.**
   `.block-derico-hero` gets `container-type: inline-size`; the two-column grid
   and the wide wash switch at `@container (min-width: 56rem)`. The hero's box
   is `100vw − var(--aurora-full-bleed-offset)`, so at a 900px viewport with the
   toolbar expanded a viewport media query fires at 896px while the hero is only
   ~680px wide and the second column's `minmax(24rem, …)` overflows — a real
   defect for exactly the logged-in site administrator the Destination names.
   `container-type: inline-size` also brings `contain: layout`, which supplies
   the stacking context, so the mockup's `isolation: isolate` drops out of the
   sheet. `sizes="100vw"` on the `<picture>` (ticket 05) stays as it is — that
   one is about bytes, and the toolbar error falls on the right side there.

9. **The wide wash keeps its fixed pixel mask stops** (`0 300px`, `black 420px`).
   They are measured from the hero's left edge, and so is the copy column's
   `.shell` inset — both shift together with the toolbar, so they stay aligned.
   Percentages would make the gradient's softness stretch with the viewport,
   which is the thing the fixed stops exist to prevent. Offsetting them by
   `--aurora-full-bleed-offset` would actively break the alignment.

10. **No print styles.** The mockup's `@media print` block is whole-page and
    derico ships no print CSS at all; one block's fragment would be the only
    print rule on the site. Recorded on the map under **Not yet specified** as a
    theme-wide concern.

### Consequences for other tickets

- **`derico.css` stops being a pure token sheet** (decision 1). Three tests in
  `tests/test_override_minimality.py` encode the old rule and must be widened,
  not deleted, so they still fail on any *other* component rule:
  `test_sheet_declares_only_root_level_selectors` (allow-list the chrome
  selector), `test_sheet_declares_nothing_but_custom_properties` (same),
  and `test_every_derico_token_is_used`, whose corpus must grow to include the
  block sheets — otherwise the four new `--derico-text-*` aliases read as
  declared-but-unused. The intent survives in all three.
- **Ticket 09 (server half) and ticket 08 (editor half): the hero must never
  set its own `width`.** `plate.py:346` stamps `block block-derico-hero
  has--block-width--full` on the *block wrapper*, and `blocks_view.css:733`
  gives that element the breakout — so on the public view `.block-derico-hero`
  **is** the full-bleed box. In the canvas the breakout lands on
  `.has--block-width--full > .block-inner-container`
  (`wrapper/src/styles/index.css:34`) and the component's own
  `<section class="block-derico-hero">` is a 100%-wide child of it. The rules
  are equivalent across surfaces only while the hero leaves `width` alone.
- **Ticket 07 (prototype) inherits the open half of decision 8.** The canvas
  carries a drag-handle gutter the public column only mimics, so the container
  may be narrower than the block on one surface and not the other. 56rem is the
  mockup's threshold, not a measured one; the prototype is what confirms or
  moves it.
