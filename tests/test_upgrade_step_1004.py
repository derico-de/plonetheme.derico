"""Tests for upgrade step 1003 -> 1004: retiring the Derico Snippet.

The record removal is a profile import and fails loudly. The content
conversion does not: a node the walk misses renders as an unknown-block
placeholder in the editor and an invisible `block-unrendered` div on the
page, which is exactly the silent damage this step exists to prevent. So
the conversion gets the cases the walk could plausibly get wrong — nested
nodes, a missing key, an unknown key, a node already converted — and the
appearance-preserving details are pinned as their own assertions.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.testing import INTEGRATION_TESTING
from plonetheme.derico.upgrades.v1004 import convert_value
from plonetheme.derico.upgrades.v1004 import upgrade


RETIRED_RECORD = (
    "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.snippet.bundle"
)


def snippet_node(**extra):
    node = {
        "type": "ploneBlock",
        "@type": "derico-snippet",
        "children": [{"text": ""}],
    }
    node.update(extra)
    return node


class TestTheRecordRemoval:
    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_the_profile_is_at_least_at_this_version(self):
        """Not `== 1004`: the newest step's test owns the exact version."""
        setup_tool = self.portal.portal_setup
        (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) >= 1004

    def test_the_retired_record_is_gone(self):
        assert api.portal.get_registry_record(RETIRED_RECORD, default=None) is None

    def test_upgrade_handler_importable(self):
        assert callable(upgrade)


class TestNodeConversion:
    """The walk itself, on plain data — no site needed."""

    layer = INTEGRATION_TESTING

    def test_a_top_level_node_is_converted(self):
        value = [snippet_node(snippet="service-frame", blockWidth="layout")]
        assert convert_value(value) == 1
        assert value[0]["@type"] == "fragment"
        assert value[0]["fragment"] == "service-frame"
        assert "snippet" not in value[0]

    def test_a_nested_node_is_converted(self):
        """A snippet inside a column is still a snippet."""
        value = [
            {
                "type": "columns",
                "children": [
                    {
                        "type": "column",
                        "children": [snippet_node(snippet="balkenlage")],
                    }
                ],
            }
        ]
        assert convert_value(value) == 1
        column = value[0]["children"][0]
        assert column["children"][0]["@type"] == "fragment"

    def test_a_missing_key_becomes_the_default_ornament(self):
        """What the retired block rendered when its key was absent."""
        value = [snippet_node()]
        convert_value(value)
        assert value[0]["fragment"] == "balkenlage"

    def test_an_unknown_key_becomes_the_default_ornament(self):
        # the retired block fell back to the Balkenlage on both surfaces
        value = [snippet_node(snippet="")]
        convert_value(value)
        assert value[0]["fragment"] == "balkenlage"

    def test_the_fixed_width_is_preserved_when_it_was_materialised(self):
        value = [snippet_node(snippet="balkenlage", blockWidth="full")]
        convert_value(value)
        assert value[0]["blockWidth"] == "full"

    def test_the_fixed_width_is_filled_in_when_it_was_not(self):
        """The retired block's `defaultBlockWidth` has no successor.

        An API-authored node carries no `blockWidth`; the generic fragment
        block declares no default, so without this the ornament would
        silently narrow from the shell width to `default`.
        """
        value = [snippet_node(snippet="balkenlage")]
        convert_value(value)
        assert value[0]["blockWidth"] == "layout"

    def test_other_blocks_are_untouched(self):
        value = [{"type": "p", "children": [{"text": "text"}]}]
        assert convert_value(value) == 0
        assert value == [{"type": "p", "children": [{"text": "text"}]}]

    def test_running_twice_converts_nothing_the_second_time(self):
        value = [snippet_node(snippet="balkenlage")]
        assert convert_value(value) == 1
        assert convert_value(value) == 0


class TestContentMigration:
    """End to end: a page with a snippet block, before and after."""

    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        alsoProvides(self.request, IPlonethemeDericoLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.page = api.content.create(
            container=self.portal, type="Document", id="page", title="A page"
        )
        alsoProvides(self.page, IBlocks)
        self.page.blocks = {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [
                    {"type": "p", "children": [{"text": "Kept"}]},
                    snippet_node(snippet="balkenlage", blockWidth="layout"),
                ],
            }
        }
        self.page.blocks_layout = {"items": [SOMERSAULT_BLOCK_ID]}
        self.page.reindexObject()

    def value(self):
        return self.page.blocks[SOMERSAULT_BLOCK_ID]["value"]

    def render(self):
        view = getMultiAdapter(
            (self.page, self.request), name="aurora-blocks-view"
        )
        return view.render()

    def test_the_stored_node_becomes_a_fragment(self):
        upgrade(self.portal.portal_setup)
        node = self.value()[1]
        assert node["@type"] == "fragment"
        assert node["fragment"] == "balkenlage"

    def test_the_rest_of_the_page_survives(self):
        upgrade(self.portal.portal_setup)
        assert self.value()[0] == {"type": "p", "children": [{"text": "Kept"}]}

    def test_the_page_renders_the_same_ornament_afterwards(self):
        """The point of converting rather than deleting."""
        upgrade(self.portal.portal_setup)
        html = self.render()
        assert 'class="block-fragment"' in html
        assert "balkenlage" in html

    def test_the_page_has_no_unrendered_block_afterwards(self):
        upgrade(self.portal.portal_setup)
        html = self.render()
        assert "block-unrendered" not in html
        assert "block-fragment-unresolved" not in html
