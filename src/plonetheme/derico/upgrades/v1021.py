"""Drop the retired block_api field."""

from plone.registry.interfaces import IRegistry
from zope.component import getUtility


#: The theme's own block add-on records. Deleting the field directly (no
#: profile import): setting it in registry.xml would raise KeyError once
#: block_api has left IAuroraBlockAddon (ADR 0024, plone.blicca.auroraeditor).
RECORDS = (
    "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero.block_api",
    "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.pageheader.block_api",
)


def upgrade(context):
    """Delete the theme's own orphan block_api records, if any are left."""
    registry = getUtility(IRegistry)
    for name in RECORDS:
        if name in registry.records:
            del registry.records[name]
