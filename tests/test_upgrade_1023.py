"""Upgrade step 1022 -> 1023: the theme loads as one stylesheet."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IBundleRegistry
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


PROFILE = "plonetheme.derico:default"
BUNDLE = "plone.bundles/plonetheme-derico"
RETIRED = ("snippets", "header", "footer", "print")


class TestUpgrade1023:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        """The 1022 theme: five bundles, one per sheet."""
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.registry = getUtility(IRegistry)
        api.portal.set_registry_record(
            f"{BUNDLE}.csscompilation", "++resource++plonetheme.derico/derico.css"
        )
        for name in RETIRED:
            self.registry.registerInterface(IBundleRegistry, prefix=f"{BUNDLE}-{name}")
            api.portal.set_registry_record(
                f"{BUNDLE}-{name}.csscompilation", f"++resource++plonetheme.derico/{name}.css"
            )
        self.setup_tool = self.portal.portal_setup
        self.setup_tool.setLastVersionForProfile(PROFILE, "1022")

    def test_points_the_theme_bundle_at_the_built_sheet(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1023")
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/derico.min.css"
        )

    @pytest.mark.parametrize("name", RETIRED)
    def test_removes_the_bundle_of_each_sheet_it_carries(self, name):
        self.setup_tool.upgradeProfile(PROFILE, dest="1023")
        prefix = f"{BUNDLE}-{name}."
        assert not [record for record in self.registry.records if record.startswith(prefix)]

    def test_keeps_the_rest_of_the_theme_bundle(self):
        api.portal.set_registry_record(f"{BUNDLE}.enabled", False)
        self.setup_tool.upgradeProfile(PROFILE, dest="1023")
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is False
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-clara"

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.setup_tool.upgradeProfile(PROFILE, dest="1023")
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1023")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1023",)
