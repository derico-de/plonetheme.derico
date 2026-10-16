"""Upgrade step 1023 -> 1024: the Clara bundle loads derico's compile of Clara."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


PROFILE = "plonetheme.derico:default"
BUNDLE = "plone.bundles/plonetheme-clara"


class TestUpgrade1024:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """The 1023 site: Clara's bundle loads Clara's own sheet."""
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.portal.set_registry_record(
            f"{BUNDLE}.csscompilation", "++resource++plonetheme.clara/clara.min.css"
        )
        self.setup_tool = self.portal.portal_setup
        self.setup_tool.setLastVersionForProfile(PROFILE, "1023")

    def test_points_the_clara_bundle_at_derico_compile(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1024")
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/clara.min.css"
        )

    def test_keeps_the_rest_of_the_clara_bundle(self):
        api.portal.set_registry_record(f"{BUNDLE}.enabled", False)
        self.setup_tool.upgradeProfile(PROFILE, dest="1024")
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is False

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.setup_tool.upgradeProfile(PROFILE, dest="1024")
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1024")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1024",)
