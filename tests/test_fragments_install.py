"""Installing the fragment provider: the record that loads its bundle.

The provider's own registration is a global utility (``test_fragments.py``);
what the profile adds is the record that makes ``@@aurora-edit`` load the
bundle publishing that corpus into the editor's registry. The record is
unusual in one way worth pinning: it declares NO ``types``, because it
registers no block. Nothing in Blicca's discovery gates on ``types``, and
the assertions below are that verdict rather than raw values — a record
that silently stops being loadable costs the picker its entries with no
error anywhere.
"""

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import blockaddons
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.testing import INTEGRATION_TESTING


RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.fragments"
ADDON_NAME = "plonetheme.derico.fragments"
STATIC_BASE = "++plone++plonetheme.derico.blocks"


def record(name, default=None):
    return api.portal.get_registry_record(f"{RECORD}.{name}", default=default)


class TestTheFragmentsRecord:
    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def status(self):
        found = [
            status
            for status in blockaddons.evaluate(self.portal)
            if status.name == ADDON_NAME
        ]
        assert found, "the fragments record is not discovered as a block add-on"
        return found[0]

    def test_the_record_is_loadable(self):
        """Every filter gate passed: enabled, resolvable, compatible."""
        status = self.status()
        assert status.loadable, f"the bundle would be skipped: {status.skip_reason}"

    def test_the_bundle_url_resolves(self):
        assert self.status().bundle_url

    def test_the_bundle_is_served_from_the_block_directory(self):
        assert record("bundle") == f"{STATIC_BASE}/fragments.js"

    def test_the_record_declares_no_block_types(self):
        """The record's whole point: a bundle, no block.

        An @type appearing here would claim a server renderer this package
        does not ship — the fragment block's renderer belongs to
        collective.fragmentsblock — and would be reported as a lockstep gap.
        """
        assert list(record("types") or []) == []

    def test_the_record_declares_no_stylesheet(self):
        # the ornaments are styled by the theme's own snippets.css bundle
        assert not record("css")

    def test_the_record_declares_the_block_api_floor(self):
        assert record("block_api") == "1.0"

    def test_the_record_is_enabled(self):
        assert record("enabled") is True

    def test_the_record_gates_nothing(self):
        """No `permission`, deliberately.

        Withholding this record would not withhold anything insertable; it
        would only empty the picker for the user allowed to insert the
        block. Insert-gating for fragments belongs to the fragment block's
        own record, in collective.fragmentsblock.
        """
        assert not record("permission")
        assert ADDON_NAME not in blockaddons.restricted_block_types(self.portal)

    def test_it_introduces_no_server_renderer_gap(self):
        """Contract §5.5: a typeless record cannot open one."""
        gaps = blockaddons.lockstep_gaps(
            self.portal, self.request, blockaddons.evaluate(self.portal)
        )
        assert [gap for gap in gaps if gap["addon"] == ADDON_NAME] == []
