"""Upgrade step 1021 -> 1022: the Reference List block is installed."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.upgrades.v1022 import upgrade


PROFILE = "plonetheme.derico:default"
PRODUCT = "collective.blicca.referencelist"


class TestUpgrade1022:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.installer = api.addon.get_installer(self.portal)
        self.setup_tool.setLastVersionForProfile(PROFILE, "1021")

    def test_installs_the_block_on_a_site_without_it(self):
        self.installer.uninstall_product(PRODUCT)
        self.setup_tool.upgradeProfile(PROFILE, dest="1022")
        assert self.installer.is_product_installed(PRODUCT)

    def test_runs_twice_without_complaint(self):
        upgrade(self.setup_tool)
        upgrade(self.setup_tool)
        assert self.installer.is_product_installed(PRODUCT)

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1022")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1022",)
