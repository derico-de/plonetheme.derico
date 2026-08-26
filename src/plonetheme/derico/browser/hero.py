"""The Derico Hero's public renderer (hero ticket 09).

The server half of the brand block whose editor half lives in
``bundle-src/src/hero/``. Dispatch is Blicca's and entirely generic:
``BlockDispatchMixin.render_block_data`` looks up
``@@aurora-block-<@type>`` on the content object and falls back to
``@@aurora-block-default`` — so registering the view name in
``configure.zcml`` is the whole of the wiring (contract §5.1).

Three things this module deliberately does NOT do:

- **It does not decide the markup.** ``Hero.tsx`` / ``HeroMedia.tsx`` /
  ``Rings.tsx`` are the reference tree and ``hero.pt`` matches them element
  for element and class for class. The stylesheet is shared — one
  scope-wrapped ``blocks.css`` serving the editing canvas AND the public page
  (contract §6.1) — so a class renamed on one side is a rule that silently
  stops matching on the other.
- **It does not decide the degradation.** ``data.ts`` holds the same table,
  pinned there by ``degradation.test.tsx`` in 21 cases and here by
  ``tests/test_hero_view.py``. Two implementations, one table; a change to
  either is a change to both.
- **It does not assume privilege.** The insert gate (ticket 03) is guidance,
  not security: the block stays authorable through the API, so this renderer
  treats whatever it is handed as ordinary untrusted data.

It also emits no breakout of its own. ``defaultBlockWidth: 'full'`` in the
bundle's ``install()`` makes the editor MATERIALISE ``blockWidth: "full"``
onto the node, so Blicca's ``plate.py`` stamps ``has--block-width--full`` on
the wrapper and the viewport bleed is already there (ticket 11).
"""

from plone.blicca.auroraeditor.rendering import BaseBlockView
from plone.blicca.auroraeditor.rendering import image_source
from plone.blicca.auroraeditor.rendering import path_of
from plone.namedfile.picture import get_picture_variants
from plone.namedfile.picture import Img2PictureTag


#: Exactly four legend entries; the numerals are position, never content.
LEGEND_LENGTH = 4

#: The ring the design marks as "now" — the last one, by construction.
LEGEND_NOW_INDEX = LEGEND_LENGTH - 1

#: The picture variants ``setuphandlers.ensure_hero_variants`` installs.
WIDE_VARIANT = "hero-wide"
PORTRAIT_VARIANT = "hero-portrait"

#: Copied verbatim onto the ``<img>`` by ``create_picture_tag``.
#:
#: ``fetchpriority="high"`` plus ``lazy=False`` INSTEAD of a ``<head>``
#: preload (ticket 05 §8): a head viewlet keyed off "the first block is a
#: derico-hero" would couple the theme's head to block content and duplicate
#: the image resolution, to buy the gap between head-parse and the first
#: element of ``<main>``.
#:
#: ``alt=""`` and no alt field anywhere in the schema — the photograph is
#: decorative in this design, and the whole ``<picture>`` is ``aria-hidden``.
IMG_ATTRIBUTES = {"alt": "", "decoding": "async", "fetchpriority": "high"}


def text(value):
    """A text field's value, trimmed; ``""`` for anything that is not text."""
    return value.strip() if isinstance(value, str) else ""


def crop(value):
    """The stored dict for an image reference, or ``None``.

    Reference fields are written by ``derico_reference`` as a one-element list
    of ``{"@id": …}`` (ticket 02), trimmed to the bare ``@id`` so renames
    survive and no stale brain metadata is persisted. restapi then resolves
    that ``@id`` to an absolute URL and injects ``image_scales`` alongside it
    on the way out — the same enrichment on the editor's inlined
    ``ISerializeToJson`` and on this view's transformer loop, which is what
    contract §5.3 is about.

    A value that never went through the widget may be a bare dict or a plain
    string, and neither is worth throwing over.
    """
    first = value[0] if isinstance(value, list) and value else value
    if isinstance(first, str):
        return {"@id": first.strip()} if first.strip() else None
    if isinstance(first, dict) and text(first.get("@id")):
        return first
    return None


def reference(value):
    """The ``@id`` of a reference field, or ``""``."""
    item = crop(value)
    return text(item.get("@id")) if item else ""


def link(label, href):
    """``{"label", "href"}`` for a link, or ``None``.

    Symmetric on purpose: a link renders only with BOTH a label and a target,
    and never falls back to the target's Title. A fallback would make the
    canvas fetch the target just to agree with this view, and the two surfaces
    would still disagree for the moment between picking and reloading.
    """
    label_text = text(label)
    target = reference(href)
    if not (label_text and target):
        return None
    # The resolved `@id` is an absolute API URL; classic UI has to serve it
    # site-relative regardless of the host the serializer stamped in.
    return {"label": label_text, "href": path_of(target)}


def legend(value):
    """Exactly ``LEGEND_LENGTH`` entries — a short or absent list is padded.

    A half-filled entry keeps its numeral and emits only the half that has
    text; an entirely empty entry is a numeral and nothing else. The numerals
    are derived from position and are not editable, and the ``is-now``
    highlight is the last entry by construction.
    """
    stored = value if isinstance(value, list) else []
    entries = []
    for index in range(LEGEND_LENGTH):
        entry = stored[index] if index < len(stored) else None
        if not isinstance(entry, dict):
            entry = {}
        entries.append({
            "number": index + 1,
            "title": text(entry.get("title")),
            "subtitle": text(entry.get("subtitle")),
            "is_now": index == LEGEND_NOW_INDEX,
        })
    return entries


def _plain_image(item):
    """The ``src`` for the no-``<picture>`` fallback, or ``""``.

    ``image_source`` returns ``None`` to mean "do not build a ``<picture>``" —
    no scales, no download URL, no base to hang it off, or an SVG upload,
    where scaling vector art buys nothing. The reference still points at an
    Image, so the original is served directly and ticket 06's
    ``object-fit: cover`` frames it exactly as it frames every other crop.
    """
    base = path_of(text((item or {}).get("@id")))
    return f"{base}/@@images/image" if base else ""


class DericoHeroView(BaseBlockView):
    """Render a ``derico-hero`` block on the published page."""

    @property
    def kicker(self):
        return text((self.data or {}).get("kicker"))

    @property
    def headline(self):
        return text((self.data or {}).get("headline"))

    @property
    def lede(self):
        return text((self.data or {}).get("lede"))

    @property
    def cta(self):
        data = self.data or {}
        return link(data.get("cta_label"), data.get("cta_href"))

    @property
    def quiet_link(self):
        data = self.data or {}
        return link(data.get("link_label"), data.get("link_href"))

    @property
    def legend(self):
        return legend((self.data or {}).get("legend"))

    @property
    def has_media(self):
        """Whether to paint the wash over the hero's token ground.

        Asked of the DATA and not of :attr:`picture`, mirroring ``Hero.tsx``:
        a hero whose only crop is an SVG renders a plain ``<img>`` rather than
        a ``<picture>``, and it still wants its wash. A hero with no
        photograph at all must not get one — a gradient over the flat token
        ground looks like a rendering fault.
        """
        data = self.data or {}
        return bool(reference(data.get("image_wide")) or reference(data.get("image_portrait")))

    @property
    def media(self):
        """What to paint behind the hero: ``{"picture", "src"}``, or ``None``.

        One property and not two, because the fallback is defined by the
        failure of the first: ``image_source`` refusing to build a
        ``<picture>`` IS the condition for the plain ``<img>``, and splitting
        that across two template expressions would run the whole derivation
        twice to ask one question.

        Exactly one of the two keys is ever filled.

        Two uploads, one ``<picture>``, spliced (ticket 05 §6). Plone's named
        scales give variants of ONE crop and never art direction, so the wide
        and portrait framings stay two uploads; two separate ``<picture>``
        elements toggled by CSS would download both. So the portrait's
        ``<source>`` elements are spliced in FRONT of the wide picture's, and
        the portrait's ``<img>`` discarded — a ``<picture>`` takes the first
        source that matches, so portrait-then-wide reproduces the design's
        56rem switch exactly, with the widths and ``sizes`` left declarative
        in the registry.

        This calls ``plone.namedfile``'s public ``Img2PictureTag`` directly,
        not Blicca's ``picture_tag``, which is unpromised and could express
        neither of the two things needed here: art direction across two
        uploads, and ``lazy=False`` on what is the page's LCP image
        (contract §5.2).

        One crop only — either one — renders that crop at every breakpoint
        through the wide sourceset, which carries no ``media``. The portrait
        variant's own query would leave everything above 56rem with no
        matching source and no ladder at all. ``object-fit: cover`` frames
        whichever crop survived; the honest fix for a badly-framed hero is at
        the upload, and a brand block offers the author no options.
        """
        data = self.data or {}
        wide = crop(data.get("image_wide"))
        portrait = crop(data.get("image_portrait"))
        base = wide or portrait
        if base is None:
            return None

        variants = get_picture_variants() or {}
        wide_variant = variants.get(WIDE_VARIANT) or {}
        base_source = image_source(base)
        if not base_source or not wide_variant.get("sourceset"):
            return {"picture": None, "src": _plain_image(base)}

        builder = Img2PictureTag()
        attributes = dict(IMG_ATTRIBUTES, src=base_source["src"])
        tag = builder.create_picture_tag(wide_variant["sourceset"], attributes, lazy=False)

        if wide is not None and portrait is not None:
            self._splice_portrait(builder, variants, portrait, tag)

        img = tag.find("img")
        if img is not None:
            # `create_picture_tag` only sets these on its `resolve_urls` path,
            # and an image without them is a layout shift on the LCP element.
            for attribute in ("width", "height"):
                if base_source.get(attribute) and not img.get(attribute):
                    img[attribute] = base_source[attribute]

        tag["class"] = "hero-media"
        tag["aria-hidden"] = "true"
        return {"picture": str(tag), "src": None}

    @staticmethod
    def _splice_portrait(builder, variants, portrait, tag):
        """Put the portrait's ``<source>`` elements first, in their own order."""
        variant = variants.get(PORTRAIT_VARIANT) or {}
        source = image_source(portrait)
        if not source or not variant.get("sourceset"):
            return
        portrait_tag = builder.create_picture_tag(
            variant["sourceset"], {"src": source["src"], "alt": ""}, lazy=False
        )
        for offset, element in enumerate(portrait_tag.find_all("source")):
            tag.insert(offset, element.extract())
