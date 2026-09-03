"""Tests for upgrade step 1004 -> 1005."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.upgrades.v1005 import PRODUCT
from plonetheme.derico.upgrades.v1005 import upgrade


class TestUpgrade1005:
    """Test upgrade to version 1005."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = api.addon.get_installer(self.portal)

    def test_installing_derico_installs_the_fragment_block(self):
        """The fresh-install half: the profile dependency in metadata.xml.

        The layer applies `plonetheme.derico:default` and nothing else, so
        the add-on is only here because derico's profile asked for it.
        """
        assert self.installer.is_product_installed(PRODUCT)

    def test_upgrade_handler_installs_the_fragment_block(self):
        """The upgrade half: the pre-1003 site, which the dependency misses.

        Uninstalling first is that site — derico installed, the add-on never
        pulled in, because GenericSetup applies dependency profiles on
        install only.
        """
        self.installer.uninstall_product(PRODUCT)
        assert not self.installer.is_product_installed(PRODUCT)

        upgrade(self.portal.portal_setup)

        assert self.installer.is_product_installed(PRODUCT)

    def test_upgrade_handler_is_a_no_op_when_already_installed(self):
        """Re-running the step must not disturb the installed add-on."""
        assert self.installer.is_product_installed(PRODUCT)

        upgrade(self.portal.portal_setup)

        assert self.installer.is_product_installed(PRODUCT)
