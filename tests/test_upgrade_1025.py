"""Upgrade step 1024 -> 1025: copper joins the block backgrounds."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


PROFILE = "plonetheme.derico:default"
BLICCA_PROFILE = "plone.blicca.auroraeditor:default"
RECORD = "plone.blicca.auroraeditor.block_backgrounds"
BUILT_IN = [("grey", "Grey"), ("accent", "Accent"), ("dark", "Dark")]


class TestUpgrade1025:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """The 1024 site: Blicca's three backgrounds."""
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.portal.set_registry_record(RECORD, BUILT_IN)
        self.setup_tool = self.portal.portal_setup
        self.setup_tool.setLastVersionForProfile(PROFILE, "1024")

    def test_adds_copper_after_the_built_in_backgrounds(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1025")
        assert api.portal.get_registry_record(RECORD) == [*BUILT_IN, ("copper", "Copper")]

    def test_creates_the_record_on_a_site_before_blicca_1006(self):
        del getUtility(IRegistry).records[RECORD]
        self.setup_tool.setLastVersionForProfile(BLICCA_PROFILE, "1005")
        self.setup_tool.upgradeProfile(PROFILE, dest="1025")
        assert ("copper", "Copper") in api.portal.get_registry_record(RECORD)
        (blicca_version,) = self.setup_tool.getLastVersionForProfile(BLICCA_PROFILE)
        assert int(blicca_version) >= 1006

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.setup_tool.upgradeProfile(PROFILE, dest="1025")
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1025")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1025",)
