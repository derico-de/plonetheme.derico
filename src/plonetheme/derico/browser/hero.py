"""The Derico Hero's public renderer; markup must match ``bundle-src/src/hero/``."""

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

#: ``fetchpriority="high"`` instead of a head preload, which would couple the
#: head to block content. The photograph is decorative, hence ``alt=""``.
IMG_ATTRIBUTES = {"alt": "", "decoding": "async", "fetchpriority": "high"}


def text(value):
    """A text field's value, trimmed; ``""`` for anything that is not text."""
    return value.strip() if isinstance(value, str) else ""


def crop(value):
    """The stored dict for an image reference (list, dict or string), or ``None``."""
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
    """``{"label", "href"}`` only when both are set; never falls back to the Title."""
    label_text = text(label)
    target = reference(href)
    if not (label_text and target):
        return None
    # The resolved `@id` is an absolute API URL; classic UI has to serve it
    # site-relative regardless of the host the serializer stamped in.
    return {"label": label_text, "href": path_of(target)}


def legend(value):
    """Exactly ``LEGEND_LENGTH`` entries; the last one is 'now'."""
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
    """The original image URL for when `image_source` refuses a `<picture>`."""
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
        """Asked of the data, not the picture: an SVG-only hero still wants its wash."""
        data = self.data or {}
        return bool(reference(data.get("image_wide")) or reference(data.get("image_portrait")))

    @property
    def media(self):
        """The spliced `<picture>` (portrait sources first), or a plain `src` fallback."""
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
