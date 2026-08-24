# Decide: what CSS the hero needs, and how it coexists with the theme

Type: grilling
Status: open
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
