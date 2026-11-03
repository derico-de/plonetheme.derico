"""Upgrade step 1025 -> 1026: copper moves up to the second block background."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


PROFILE = "plonetheme.derico:default"
RECORD = "plone.blicca.auroraeditor.block_backgrounds"
COPPER_LAST = [("grey", "Grey"), ("accent", "Accent"), ("dark", "Dark"), ("copper", "Copper")]
COPPER_SECOND = [("grey", "Grey"), ("copper", "Copper"), ("accent", "Accent"), ("dark", "Dark")]


class TestUpgrade1026:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """The 1025 site: copper after Blicca's three backgrounds."""
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.portal.set_registry_record(RECORD, COPPER_LAST)
        self.setup_tool = self.portal.portal_setup
        self.setup_tool.setLastVersionForProfile(PROFILE, "1025")

    def test_moves_copper_to_second_place(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1026")
        assert api.portal.get_registry_record(RECORD) == COPPER_SECOND

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.setup_tool.upgradeProfile(PROFILE, dest="1026")
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1026")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1026",)
