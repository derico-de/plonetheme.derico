"""Tests for upgrade step 1001 -> 1002."""
import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.testing import INTEGRATION_TESTING


class TestUpgrade1002:
    """Test upgrade to version 1002."""

    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_the_profile_is_at_least_at_this_version(self):
        """Not `== 1002`: the newest step's test owns the exact version.

        Pinning the installed version here made every later
        `plonecli add upgrade_step` fail this file for no reason of its own.
        """
        setup_tool = self.portal.portal_setup
        (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) >= 1002

    def test_upgrade_handler_importable(self):
        """Test the upgrade handler can be imported."""
        from plonetheme.derico.upgrades.v1002 import upgrade

        assert callable(upgrade)

    def test_upgrade_handler_runs(self):
        """Test the upgrade handler can be executed."""
        from plonetheme.derico.upgrades.v1002 import upgrade

        setup_tool = self.portal.portal_setup
        upgrade(setup_tool)
