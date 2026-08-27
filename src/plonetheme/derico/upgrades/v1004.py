"""Retire the Derico Snippet block in favour of the generic fragment block.

The two delivered the same thing — a `snippets/*.html` ornament, injected
verbatim — once derico became a fragment provider in 1003. Keeping both
meant two ways to place one ornament and two registration stacks to
maintain, so the brand block goes and `collective.fragmentsblock`'s
`fragment` stays.

Stored nodes are **converted, not dropped**: `@type` becomes `fragment` and
the `snippet` key becomes `fragment`, which is the whole difference between
the two blocks' data. A converted page renders exactly as it did — same
file, same markup, same stylesheet — so nobody has to rebuild a page
because the machinery underneath it was consolidated.

Two details preserve appearance rather than data:

- an absent or unrecognised `snippet` rendered the Balkenlage on both of
  the old block's surfaces (its schema default, restated at render time),
  so it converts to `balkenlage` rather than to an unresolvable fragment;
- the old block fixed its width through `defaultBlockWidth: 'layout'`,
  which Aurora materialised onto nodes at insert but which never reached
  nodes authored through the API. The generic block declares no default, so
  a node without `blockWidth` would silently narrow to `default`; it is
  filled in here.

The record removal is the paired `1004/registry.xml` — a re-import of the
default profile cannot delete a record that merely stopped being declared.
"""

import logging

from plone import api
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.restapi.behaviors import IBlocks


logger = logging.getLogger(__name__)

OLD_TYPE = "derico-snippet"
NEW_TYPE = "fragment"

#: What the retired block rendered when its key was absent or unknown.
DEFAULT_FRAGMENT = "balkenlage"

#: The width the retired block materialised onto its nodes.
SNIPPET_BLOCK_WIDTH = "layout"


def convert_node(node):
    """Rewrite one node in place. Returns True if it was a snippet node."""
    if node.get("@type") != OLD_TYPE:
        return False
    node["@type"] = NEW_TYPE
    fragment = node.pop("snippet", None)
    node[NEW_TYPE] = fragment if isinstance(fragment, str) and fragment else (
        DEFAULT_FRAGMENT
    )
    node.setdefault("blockWidth", SNIPPET_BLOCK_WIDTH)
    return True


def convert_value(value):
    """Convert every snippet node in a somersault value. Returns the count.

    Walks the whole tree rather than the top level: a snippet can sit inside
    a column, a toggle, or any other node that nests children.
    """
    converted = 0
    if isinstance(value, dict):
        converted += 1 if convert_node(value) else 0
        for child in value.values():
            converted += convert_value(child)
    elif isinstance(value, list):
        for child in value:
            converted += convert_value(child)
    return converted


def convert_object(obj):
    """Convert the snippet nodes stored on one content object."""
    blocks = getattr(obj, "blocks", None)
    if not isinstance(blocks, dict):
        return 0
    somersault = blocks.get(SOMERSAULT_BLOCK_ID)
    if (
        not isinstance(somersault, dict)
        or somersault.get("@type") != SOMERSAULT_BLOCK_TYPE
    ):
        return 0
    converted = convert_value(somersault.get("value"))
    if converted:
        # rebind so the persistent attribute is marked dirty; the value
        # itself is a plain dict/list tree ZODB does not watch
        obj.blocks = dict(blocks)
    return converted


def upgrade(context):
    """Upgrade from profile version 1003 to 1004."""
    logger.info("Running upgrade step: Retire the Derico Snippet block")
    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog(object_provides=IBlocks.__identifier__)
    pages = 0
    nodes = 0
    for brain in brains:
        try:
            obj = brain.getObject()
        except (AttributeError, KeyError):  # stale catalog entry
            continue
        converted = convert_object(obj)
        if converted:
            pages += 1
            nodes += converted
            logger.info(
                "Converted %s snippet block(s) to fragments on %s",
                converted,
                brain.getPath(),
            )
    logger.info(
        "Retired the Derico Snippet: %s block(s) converted on %s page(s)",
        nodes,
        pages,
    )
