"""Drop the fragments editor bundle record."""

from plone.registry.interfaces import IRegistry
from zope.component import getUtility


#: The block add-on record that loaded derico's `fragments.js` into the
#: editor. Matched with a trailing dot, so a longer name that merely starts
#: the same way is never touched.
PREFIX = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.fragments"


def upgrade(context):
    """collective.fragmentsblock lists the snippets itself now (its ADR 0002)."""
    registry = getUtility(IRegistry)
    for name in [name for name in registry.records if name.startswith(f"{PREFIX}.")]:
        del registry.records[name]
