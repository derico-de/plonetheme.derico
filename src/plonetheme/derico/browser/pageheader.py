"""The Derico Page Header's public renderer.

The server half of the brand block whose editor half lives in
``bundle-src/src/pageheader/``. Dispatch is Blicca's and generic: registering
``@@aurora-block-derico-page-header`` in ``configure.zcml`` is the whole of
the wiring (contract §5.1).

The block stores ONE thing, the kicker. The title and the description are the
page's own fields: on the canvas the block binds them through the host's form
atom (contract §1.7), here they are read from the context. So a page that
opens with this block needs neither the tree's title node nor its description
node, and ``context.Title`` — head title, listings, breadcrumbs — stays what
the author typed into the header.

``PageHeader.tsx`` is the reference tree and ``pageheader.pt`` matches it
class for class: one scope-wrapped ``blocks.css`` styles both surfaces. No
breakout of its own — ``defaultBlockWidth: 'layout'`` in the bundle makes the
editor materialise ``blockWidth: "layout"`` onto the node, and Blicca's
``plate.py`` stamps the wrapper from that.
"""

from plone.blicca.auroraeditor.rendering import BaseBlockView


def text(value):
    """A text value, trimmed; ``""`` for anything that is not text."""
    return value.strip() if isinstance(value, str) else ""


class DericoPageHeaderView(BaseBlockView):
    """Render a ``derico-page-header`` block on the published page."""

    @property
    def kicker(self):
        return text((self.data or {}).get("kicker"))

    @property
    def title(self):
        return text(self.context.Title())

    @property
    def description(self):
        return text(self.context.Description())
