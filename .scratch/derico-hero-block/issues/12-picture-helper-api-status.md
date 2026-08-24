# Decide: does the hero reach into Blicca's unpromised image helpers, or do they get promoted?

Type: grilling
Status: open
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
