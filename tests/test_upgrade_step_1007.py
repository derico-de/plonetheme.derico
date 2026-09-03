"""Tests for upgrade step 1006 -> 1007."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.upgrades.v1007 import PRODUCTS
from plonetheme.derico.upgrades.v1007 import upgrade


class TestUpgrade1007:
    """Test upgrade to version 1007."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = api.addon.get_installer(self.portal)

    def test_the_profile_is_at_this_version(self):
        """The newest step's test owns the exact version."""
        setup_tool = self.portal.portal_setup
        (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) == 1007

    @pytest.mark.parametrize("product", PRODUCTS)
    def test_installing_derico_installs_the_dependency(self, product):
        """The fresh-install half: the profile dependencies in metadata.xml.

        The layer applies `plonetheme.derico:default` and nothing else, so
        each add-on is only here because derico's profile asked for it. This
        also pins PRODUCTS to the profile: a name that drifts out of
        metadata.xml's <dependencies> fails here.
        """
        assert self.installer.is_product_installed(product)

    @pytest.mark.parametrize("product", PRODUCTS)
    def test_upgrade_handler_installs_the_dependency(self, product):
        """The upgrade half: the site that predates the dependency.

        Uninstalling first is that site -- derico installed, the add-on
        never pulled in, because GenericSetup applies dependency profiles on
        install only.
        """
        self.installer.uninstall_product(product)
        assert not self.installer.is_product_installed(product)

        upgrade(self.portal.portal_setup)

        assert self.installer.is_product_installed(product)

    def test_upgrade_handler_installs_every_missing_dependency_at_once(self):
        """One run covers the whole list, not just the first gap."""
        for product in PRODUCTS:
            self.installer.uninstall_product(product)

        upgrade(self.portal.portal_setup)

        for product in PRODUCTS:
            assert self.installer.is_product_installed(product)

    def test_upgrade_handler_is_a_no_op_when_everything_is_installed(self):
        """Re-running the step must not disturb the installed add-ons."""
        for product in PRODUCTS:
            assert self.installer.is_product_installed(product)

        upgrade(self.portal.portal_setup)

        for product in PRODUCTS:
            assert self.installer.is_product_installed(product)
