# Decide and build: does the hero reach into Blicca's unpromised image helpers, or do they get promoted?

Type: grilling
Status: closed
Assignee: md@derico.de
Blocked by: —

## Question

Surfaced by [ticket 01's findings](01-research-image-field-and-delivery.md).
Blicca's `picture_tag`, `variant_for_image_block`, `variant_for_block_width`
(`browser/rendering/picture.py:30,61,81`) and `image_model`, `path_of`
(`scales.py:13,20`) do everything the hero's `<picture>` needs — and all three
of Blicca's own renderers use them. But contract §5.2
(`aurora-block-addon-contract.md:307`, echoed at `rendering.py:8`) says they are
**not promised API**, and the promised `BaseBlockView` has no image support at
all (`base.py:77`).

So the first real block add-on to render an image has no sanctioned way to do
it. Decide:

- **Import them anyway**, accepting an unpromised dependency, with a test that
  fails loudly when the signature moves. Cheap, honest about the risk, and
  leaves the contract's promise list telling a lie by omission.
- **Promote them** — a minimal image surface added to §5.2 and to
  `BaseBlockView`, landing in `plone.blicca.auroraeditor` alongside tickets 03
  and 11. Fixes the contract for every future block, costs an API commitment
  made from one example.
- **Reimplement in the theme** over `plone.namedfile.picture.Img2PictureTag`
  directly, skipping Blicca's layer. No unpromised dependency, but the third
  copy of glue that already exists twice.

Whatever wins, say what the *next* brand block does — this is the first of an
expected several, and the answer that only serves the hero is the wrong one.

Note the hero cannot use `variant_for_image_block` / `variant_for_block_width`
regardless: it carries no `size`, and its `blockWidth` is fixed by ticket 11, so
its picture variants are named explicitly (ticket 05). The reuse question is
about `picture_tag` and `image_model`, not the variant chooser.

## Narrowed by ticket 05 (2026-08-24)

[Ticket 05](05-image-delivery.md) removed `picture_tag` from the reuse
question entirely. Two of its findings do that:

- `picture_tag` builds **one** `<picture>` from **one** image, and the hero
  needs sources from two uploads in one `<picture>` (art direction at 56rem).
- It hardcodes `lazy=True` (`picture.py:110`), i.e. `loading="lazy"` on the
  LCP image, with no parameter to turn it off.

So the hero's view calls `Img2PictureTag` — **public `plone.namedfile` API**,
not Blicca's layer — twice and splices the results. The third option above
("reimplement over `Img2PictureTag` directly") is therefore already forced for
the `<picture>` itself, and it is not a "third copy of glue": it is the only
thing that renders this markup.

**What is left of this ticket** is much smaller: the hero still needs the
`image_scales`-to-download-URL derivation that `scales.py:path_of` and
`image_model` (`scales.py:13,20`) perform — resolving the enriched
`image_scales` payload to a site-relative base path and a download URL to hand
`Img2PictureTag` as its `src`. That is ~20 lines, it is still unpromised, and
it is what every future brand block rendering an image will need.

So decide about **that derivation only**: import it unpromised with a
lockstep test, promote it into §5.2 / `BaseBlockView`, or copy it into the
theme. The "say what the next brand block does" requirement stands unchanged.

## Resolution (2026-08-25, grilled with md@derico.de)

**Promoted — but not the function this ticket named.** Two derivations join
the contract's promised API (§5.2), re-exported from
`plone.blicca.auroraeditor.rendering` beside `BaseBlockView`. Built in
Blicca, following tickets 03 and 11; ticket 09 only consumes it.

### 1. `image_model` was the wrong function to argue about

The ticket, and 05's narrowing, both named `scales.py:image_model` as the
derivation the hero needs. Measured against the hero's actual call, it is
not:

| what `image_model` returns | what the hero does with it |
| --- | --- |
| `src` | uses it — this is the whole ask |
| `width`, `height` | uses them (layout stability) |
| `srcset` | **discards it** — `Img2PictureTag` builds the sourceset from the registry variant |
| `alt` | **discards it** — the hero's `<picture>` is `aria-hidden` (charting) |
| *(no `content-type`)* | **misses the SVG guard**, which lives in `picture_tag`, not here |

The derivation the hero needs is `picture_tag`'s *preamble*
(`picture.py:81-99`) — first entry, base path, download URL, intrinsic dims,
SVG bail — not `image_model`'s output shape. Promoting `image_model` would
have promised the wrong thing and still left the hero writing the guard.

### 2. The gap was never image-only

`path_of` (`scales.py:13`) is equally unpromised and the hero needs it
independently of any image: ticket 02 stores `cta_href` and `link_href` as
bare `{"@id": …}`, whose resolved value is an absolute API URL that the
public view must emit site-relative — exactly what `teaser_block.py:65-66`
does. It already has call sites in four of Blicca's five renderers.

So the promotion covers one seam, not one function: **turning the shapes
restapi injects into things a classic template can emit.**

### 3. What was promoted

| Function | Returns | For |
| --- | --- | --- |
| `path_of(url)` | the path of an absolute content URL | any resolved reference — link `href`, download URL |
| `image_source(item, image_field=None)` | `{src, width, height}` or `None` | the base image a `<picture>` is built from |

Free functions, **not** `BaseBlockView` methods: the hero calls
`image_source` twice with different fields so a method needs the parameter
anyway, `path_of` has nothing to do with a view, and free functions test
without constructing one.

`None` from `image_source` means *do not build a `<picture>`* — no scales, no
download URL, no base, or an SVG. **Q1: the guard stays**, matching what all
four existing renderers already do; the hero falls back to a plain `<img>`
and `object-fit` (ticket 05 §7) does the rest.

`image_model` stays **internal**. It serves the plain-`img`/`srcset` case,
which is Blicca's own; the gap §5.2 had was the `<picture>` one.

### 4. `picture_tag` was refactored onto it, and stays unpromised

`picture.py` lost `_first_image` and its base/SVG block; `picture_tag` now
calls `image_source`. A promised copy no first-party caller exercises drifts
from the used one — the same "two code paths, one answer" ticket 11 rejected
a record field to avoid. Pinned by `TestPictureTagRidesOnImageSource`.

It stays unpromised **deliberately**, and §5.2 now says why rather than
leaving it a bare exclusion: one `<picture>` from one image, `lazy=True`
hardcoded, returns a `str`. A block needing art direction or an eager LCP
image calls `Img2PictureTag` itself with an `image_source` `src` — now the
documented path rather than a workaround.

*Correcting ticket 05:* its stated reason for rejecting `picture_tag` — that
it "cannot express art direction" — is not quite right. Two `picture_tag`
calls spliced would express it. The real disqualifier is that
`create_picture_tag` returns a BeautifulSoup tag and `picture_tag` does
`str(tag)` (`picture.py:114`), so splicing over it costs a string → re-parse
round trip, on top of `lazy=True` and no `attributes` passthrough for
`fetchpriority`. **05's conclusion stands; its reasoning did not.**

### 5. `block_api` cannot version this

§2.2 stamps `block_api` over "the facade list plus the majors of the deps
behind it" — the JS surface — and §2.3 is explicit that the declaration is
"Python half only; nothing is required inside the JS bundle". So a record
declaring `block_api: "1.1"` promises **nothing** about
`from plone.blicca.auroraeditor.rendering import …`.

The only signal is the Python distribution version. §5.2 now says so, and an
add-on using the surface MUST declare a minimum
`plone.blicca.auroraeditor` in its own metadata. **Handed to ticket 09**:
the theme's `install_requires` floor (ticket 04 already made Blicca a hard
Python dependency; this makes it a *versioned* one).

This sentence is the most valuable line of the amendment — the two signals
are independent, an add-on may need both, and nothing before said it.

### 6. Found while testing: `path_of` mangles non-http schemes

`urlparse("mailto:md@derico.de").path` is `"md@derico.de"` — truthy — so
`path_of` returns it with the scheme stripped rather than returning the value
whole. Pre-existing, and latent in `teaser_block`/`video_block` today.

**Not fixed here.** The hero is unaffected (its links are object_browser
content picks, always http(s)), and changing the behaviour of a function
with four existing call sites — including `video_block`'s external-URL path
— is a regression risk in a ticket that is not about links. Documented as a
limit in §5.2, pinned by `test_non_http_scheme_is_stripped_not_preserved`,
and left on the map as Blicca's to decide.

### 7. What the next brand block does

Imports `path_of` and `image_source` from
`plone.blicca.auroraeditor.rendering`, declares its Blicca version floor, and
calls `Img2PictureTag` directly for anything `picture_tag` cannot express.
No copying, no unpromised imports. That was the ticket's standing
requirement and it is met by construction — the surface was extracted from
five call sites (image, teaser, listing, video, hero), not designed from the
hero alone, which is what disarms the usual "an API commitment made from one
example" objection.

### Built

All in `plone.blicca.auroraeditor`, uncommitted:

- `browser/rendering/scales.py` — new `image_source`; module docstring marks
  which functions are promised and which are not.
- `browser/rendering/picture.py` — `_first_image` removed, `picture_tag`
  rebuilt on `image_source`, `urlparse` import dropped.
- `rendering.py` — `__all__` is now `["BaseBlockView", "image_source",
  "path_of"]`, with the `picture_tag` exclusion and the `block_api` caveat in
  the docstring.
- `docs/design/aurora-block-addon-contract.md` §5.2 — the two-function table,
  the `None` contract, the `picture_tag` exclusion *with its reason*, the
  `path_of` scheme limit, and the distribution-versioning paragraph.
- `tests/test_rendering_api.py` — 20 pure unit tests standing in for the
  add-ons that import the surface: export list, stable path, both functions'
  behaviour and every refusal, plus the `picture_tag`-rides-on-`image_source`
  lockstep.
- `news/45.feature`.

Full Blicca suite: **202 passed**. No renderer test changed.
