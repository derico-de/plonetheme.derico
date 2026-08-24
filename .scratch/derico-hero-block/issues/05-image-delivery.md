# Decide: how the hero's two images are stored, scaled and served

Type: grilling
Status: closed
Assignee: md@derico.de
Blocked by: 01

## Question

The mockup hand-cuts a wide crop (2400×1200) and a portrait crop, switched at
56rem, each in AVIF, WebP and JPEG, with the above-the-fold one preloaded.
Settled at charting: two image fields, each through `plone.picture_variants`.
This ticket decides the rest.

- **The variants.** New `hero-wide` and `hero-portrait` picture variants in the
  theme's `registry.xml` — which widths, which target scales? The mockup's
  wide srcset is 960/1600/2400. `browser/rendering/picture.py` already maps
  Aurora block sizes to variants; check how a brand block declares its own.
- **The upgrade step.** A registry change needs one, even at `1.0.0a1` —
  `plonecli add upgrade_step`, narrowed to the registry import step.
- **Portrait absent.** Confirmed optional with a wide fallback. Decide what the
  fallback actually renders: the wide image with `object-position`, or the
  wide `<source>` simply matching at all widths.
- **Formats.** Plone's picture variants produce what the site is configured to
  produce. Does the sandbox emit AVIF and WebP, or only JPEG — and if the
  answer is "only JPEG", is that acceptable for a brand page or does it need
  fixing first?
- **Preload.** The mockup preloads the hero image with `fetchpriority="high"`.
  A block renders inside the page body and cannot easily reach `<head>`. Decide
  whether to attempt it (a viewlet keyed off the first block?) or accept the
  loss and note the LCP cost.
- **The editor preview.** What the `edit` half shows before an image is chosen,
  and whether it renders the real crops or a cheap placeholder.

## Answer

Grilled with md@derico.de, 2026-08-24. Three facts found while preparing the
round overturned the question's own premises, so they lead.

### The premises that were wrong

- **The mockup's format ladder cannot be reproduced.** `picture_variants`'
  sourceset schema is `additionalProperties: False` over exactly `scale`,
  `media`, `sizes`, `additionalScales` (`plone/base/interfaces/controlpanel.py`,
  `IImagingSchema`), and `Img2PictureTag.create_picture_tag`
  (`plone/namedfile/picture.py`) never emits a `type=` attribute. Plone's
  `<picture>` does **resolution** switching only, never **format**
  negotiation. AVIF/WebP/JPEG is not on the table.
- **The variants cannot go in `registry.xml`.** `picture_variants` is a
  `JSONField`; GS has no syntax for it. Blicca already hit this and adds
  `fullwidth` from a setuphandler (`setuphandlers.py:50`), re-called from
  `upgrades/v1001.py`. `plone.allowed_sizes` is a plain `List` and *can* be
  imported — including merge-not-replace via `purge="false"`
  (`plone/app/registry/exportimport/handler.py:269,285`). The two halves take
  different routes.
- **Blicca's `picture_tag()` cannot render this block.** It builds one
  `<picture>` from one image and hardcodes `lazy=True` (`picture.py:110`) —
  i.e. `loading="lazy"` on the LCP image. Art direction across two uploads
  needs sources from two images in one `<picture>`.

### 1. Format — serve whatever was uploaded, and ask for WebP

The images are references to Image *content items* (ticket 02:
`{"@id": "../resolveuid/<uid>"}`), so the upload happens in Plone's Image type
and the block has no `accept` to constrain. `plone.scale` preserves `WEBP` and
coerces anything that is not PNG to `JPEG` (`scale.py:137`); AVIF is not in
that list at all.

So: **document "upload the hero crops as WebP"** in the block's README and
serve what arrives. WebP-in/WebP-out recovers most of the mockup's byte
saving at zero cost. Rejected: building format negotiation in the hero's view
— generating and storing derived AVIF outside Plone's scale machinery is a lot
of new surface for one block (now an Out-of-scope line on the map).

### 2. Scale ladder — one new rung, appended, never removed

Re-derived from viewport x DPR rather than copied from the mockup:

- **Portrait needs no new scale.** Stock `teaser 600` / `larger 1000` /
  `great 1200` beats the mockup's hand-cut 720/1080 — three rungs, higher
  ceiling. A 430px phone at DPR 3 wants 1290 and gets 1200 (0.93x).
- **Wide needs exactly one.** The mockup's 960 is within 4% of stock
  `larger 1000` (a near-duplicate rung, not coverage) and its 1600 is stock
  `huge`. Only the top end is a genuine gap.

New rung: **`enormous 2600:65536`**. Named for size, continuing the stock
ladder's adjective pattern (`huge`, `great`, `larger`, ...) — *not* `hero`,
which would claim a site-wide name for one block's purpose and put a `hero`
key in every image's `image_scales` payload. Chosen over 2400 (0.94x on a
2560 desktop) and 2880 (+44% bytes on the LCP image): 2600 covers a 2560
desktop exactly and leaves a retina laptop at 0.90x.

**Only ever append.** Stock Plone templates and other add-ons hardcode
`large`, `preview`, `mini`, `thumb`, `icon` by name; removing or resizing an
existing rung breaks things well outside this theme.

### 3. The two variants

```json
"hero-wide": {
  "title": "Hero (wide)",
  "hideInEditor": true,
  "sourceset": [
    {"scale": "huge", "additionalScales": ["larger", "enormous"], "sizes": "100vw"}
  ]
},
"hero-portrait": {
  "title": "Hero (portrait)",
  "hideInEditor": true,
  "sourceset": [
    {"scale": "larger", "additionalScales": ["teaser", "great"],
     "media": "(max-width: 55.99rem)", "sizes": "100vw"}
  ]
}
```

- `additionalScales` is given **explicitly**: omitted, it defaults to *every*
  other allowed scale (`picture.py`, `additional_scales is None` branch).
- `sizes` is given **explicitly**: the default is
  `(min-width: 576px) {target}px, (min-width: 768px) 600px, 98vw`, which is
  wrong for a full-bleed block.
- The `<img>` fallback lands on the target scale, so `huge`/1600 is the `src`
  — the same choice the mockup made.
- `hideInEditor: true` on both: picture variants surface as a picker for
  hand-placed images in the richtext editor, where these two are meaningless.
  (Blicca's `fullwidth` does not set it, but `fullwidth` is plausibly useful
  to a hand-placed image; these are not.)

### 4. Declaration — a forced split, plus one upgrade step covering both

- `plone.allowed_sizes` -> `profiles/default/registry.xml`, referencing the
  existing record by name and merging rather than replacing:

  ```xml
  <record name="plone.allowed_sizes">
    <value purge="false">
      <element>enormous 2600:65536</element>
    </value>
  </record>
  ```

- `picture_variants` -> an idempotent `ensure_hero_variants()` setuphandler on
  Blicca's `ensure_fullwidth_variant` pattern (add key only if absent), called
  from `post_install`.
- **One upgrade step** scaffolded via `plonecli add upgrade_step`, narrowed to
  the `plone.app.registry` import step **and** calling `ensure_hero_variants()`
  — the JSONField half has no import step to narrow to.

### 5. Uninstall leaves both records in place

Matching how Blicca never removes `fullwidth`. Removing a scale that content
elsewhere now references is worse than leaving a harmless extra rung. This is
deliberately **asymmetric** with how the theme's uninstall profile removes its
bundle records — worth a comment in the profile so the next reader does not
"fix" it.

### 6. Art direction — splice two picture tags

Two separate `<picture>` elements toggled by CSS still download both. Instead,
in the hero's view: call `Img2PictureTag().create_picture_tag()` **twice**
(once per variant), splice the portrait `<source>` elements in front of the
wide picture's sources, and discard the portrait `<img>`. First matching
source wins, so portrait-then-wide reproduces the mockup's 56rem switch
exactly. Widths and `sizes` stay declarative in the registry; the splice is a
few lines of BeautifulSoup.

This uses `plone.namedfile`'s `Img2PictureTag` **directly** — public Plone API
— not Blicca's unpromised `picture_tag()`, which can express neither art
direction nor `lazy=False`. See "Inputs to other tickets" below.

### 7. Portrait absent — centre-crop the wide image

Simply omit the portrait sources; the wide 2:1 image under the existing
`object-fit: cover; object-position: 50% 50%` (`site.css:398`) centre-crops on
a tall viewport. Rejected: a narrow-viewport `object-position` bias, which is
a hidden option nobody can tune per image, and brand blocks offer no options.
The honest fix is at the upload — an administrator who cares fills the field.
Surfacing "no portrait crop" belongs on the diagnostics view (ticket 09), not
in the markup.

### 8. Preload — `fetchpriority`, no head viewlet

`fetchpriority="high" decoding="async"` on the `<img>`, and explicitly
`create_picture_tag(..., lazy=False)` so the LCP image never gets
`loading="lazy"`. Both ride in via the `attributes` dict, which
`create_picture_tag` copies onto the `img` verbatim except `src`/`srcset`.

**No** `<head>` preload. A viewlet keyed off "the first block is a
`derico-hero`" would couple the theme's head to block content and duplicate
the image resolution, to buy the gap between head-parse and the first element
of `<main>`. The residual LCP cost is accepted, not zero — measure it at
ticket 10 rather than assuming.

### 9. Editor preview — one scale, no art direction

The canvas is 940-1440px and never full-bleed-on-4K. The `edit` half renders a
**single scale as a plain `<img>`** (from the `image_scales` stock restapi
injects on the nested `@id`, per ticket 01), plus a placeholder for the
genuinely-empty state. The canvas is a live preview, not a proof of the
delivery pipeline; ticket 10 verifies the real markup on the public view.
Rebuilding the splice in TypeScript would duplicate the one piece of logic
most likely to drift.

### Inputs to other tickets

- **Ticket 12** (`picture-helper-api-status`): the hero turns out **not** to
  need Blicca's `picture_tag()` at all — it needs `Img2PictureTag` (public
  `plone.namedfile` API) plus the small `image_scales`-to-download-URL
  derivation that `scales.py:path_of`/`image_model` performs. That narrows 12
  considerably: the open question is whether *that URL derivation* gets
  promoted, not the whole `<picture>` helper.
- **Ticket 09** (server half): owns the registry.xml, the setuphandler, the
  upgrade step, the splice, and the "no portrait crop" diagnostics line.
- **Ticket 06** (CSS): `object-fit`/`object-position` on `.hero-media img`
  stays as the mockup has it; the portrait-absent fallback depends on it.
