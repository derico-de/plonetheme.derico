"""Upgrade step 1016 -> 1017: Clara's on-demand search."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


PROFILE = "plonetheme.derico:default"
RECORD = "plonetheme.clara.search_on_demand"
BUNDLE = "plone.bundles/plonetheme-derico-header"


class TestUpgrade1017:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        api.portal.set_registry_record(RECORD, False)
        api.portal.set_registry_record(
            f"{BUNDLE}.jscompilation", "++resource++plonetheme.derico/header.js"
        )
        self.setup_tool.setLastVersionForProfile(PROFILE, "1016")

    def test_turns_the_search_on_demand_on(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1017")
        assert api.portal.get_registry_record(RECORD) is True

    def test_drops_header_js_from_the_bundle(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1017")
        assert not api.portal.get_registry_record(f"{BUNDLE}.jscompilation")

    def test_keeps_the_rest_of_the_bundle(self):
        api.portal.set_registry_record(f"{BUNDLE}.enabled", False)
        self.setup_tool.upgradeProfile(PROFILE, dest="1017")
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is False
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/header.css"
        )

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.setup_tool.upgradeProfile(PROFILE, dest="1017")
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1017")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1017",)
