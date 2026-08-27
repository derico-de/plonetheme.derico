"""Tests for upgrade step 1002 -> 1003."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.testing import INTEGRATION_TESTING


RECORD = (
    "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.fragments.bundle"
)


class TestUpgrade1003:
    """Test upgrade to version 1003."""

    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_the_profile_is_at_least_at_this_version(self):
        """Not `== 1003`: the newest step's test owns the exact version."""
        setup_tool = self.portal.portal_setup
        (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) >= 1003

    def test_upgrade_handler_importable(self):
        from plonetheme.derico.upgrades.v1003 import upgrade

        assert callable(upgrade)

    def test_upgrade_handler_restores_the_fragments_record(self):
        """The step's whole job: re-import registry.xml.

        Deleting the record and running the handler is the 1002-site case —
        a site that never saw the fragments record at all.
        """
        from plonetheme.derico.upgrades.v1003 import upgrade

        api.portal.set_registry_record(RECORD, "")
        upgrade(self.portal.portal_setup)
        assert api.portal.get_registry_record(RECORD) == (
            "++plone++plonetheme.derico.blocks/fragments.js"
        )
