"""Tests for upgrade step 1007 -> 1008: the Promo block."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.upgrades.base import ADDON_DEPENDENCIES
from plonetheme.derico.upgrades.v1008 import upgrade


PRODUCT = "derico.blicca.promoblock"


class TestUpgrade1008:
    """Test upgrade to version 1008."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = api.addon.get_installer(self.portal)

    def test_the_profile_is_at_this_version(self):
        """The newest step's test owns the exact version."""
        setup_tool = self.portal.portal_setup
        (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) == 1008

    def test_the_promo_block_is_a_declared_dependency(self):
        """What this version adds, read off the list the steps install from."""
        assert PRODUCT in ADDON_DEPENDENCIES

    def test_installing_derico_installs_the_promo_block(self):
        """The fresh-install half: the profile dependency in metadata.xml.

        The layer applies `plonetheme.derico:default` and nothing else, so
        the add-on is only here because derico's profile asked for it.
        """
        assert self.installer.is_product_installed(PRODUCT)

    def test_upgrade_handler_installs_the_promo_block(self):
        """The upgrade half: the site that predates the dependency."""
        self.installer.uninstall_product(PRODUCT)
        assert not self.installer.is_product_installed(PRODUCT)

        upgrade(self.portal.portal_setup)

        assert self.installer.is_product_installed(PRODUCT)

    def test_upgrade_handler_is_a_no_op_when_already_installed(self):
        """Re-running the step must not disturb the installed add-on."""
        assert self.installer.is_product_installed(PRODUCT)

        upgrade(self.portal.portal_setup)

        assert self.installer.is_product_installed(PRODUCT)
