"""Module where all interfaces, events and exceptions live."""

from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer


class IPlonethemeDericoLayer(IPlonePageletlayoutLayer):
    """Marker interface that defines a browser layer.

    Extends the pagelet-layout layer, as Clara's does, so a chrome pagelet
    derico registers under a base provider name on this layer is
    unambiguously more specific than both the base registration and
    Clara's: the searchbox override in browser/configure.zcml relies on it.
    """
