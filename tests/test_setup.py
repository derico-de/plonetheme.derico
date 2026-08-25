"""Test plonetheme.derico installation."""
import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


BUNDLE = "plone.bundles/plonetheme-derico"


class TestSetup:
    """Test installation and setup."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_addon_installed(self):
        """Test addon is installed."""
        installer = api.addon.get_installer(self.portal)
        assert installer.is_product_installed("plonetheme.derico")

    def test_base_theme_installed(self):
        """derico is a token layer: installing it must bring Clara along."""
        installer = api.addon.get_installer(self.portal)
        assert installer.is_product_installed("plonetheme.clara")

    def test_browserlayer(self):
        """Test browserlayer is registered."""
        from plone.browserlayer import utils

        assert IPlonethemeDericoLayer in utils.registered_layers()

    def test_block_bundles_are_served(self):
        """The editor bundles are only useful if they have a URL.

        A second static directory, `++plone++` rather than `++resource++`,
        because the contract's cache-buster names `++plone++` and one
        directory under both directives would give every file two public URLs
        (hero ticket 04 §3). Registration is ZCML, so nothing else in the
        install would notice it missing — the artifacts would simply 404.
        """
        from plone.resource.interfaces import IResourceDirectory
        from zope.component import getUtility

        directory = getUtility(
            IResourceDirectory, name="++plone++plonetheme.derico.blocks"
        )
        assert "hero.js" in directory.listDirectory()
        assert "blocks.css" in directory.listDirectory()

    def test_bundle_registered_and_enabled(self):
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/derico.css"
        )

    def test_bundle_loads_after_clara(self):
        """Documented order.

        The cascade does not actually depend on it — derico.css is unlayered
        and Clara's tokens sit in `@layer tokens` — but a reader should not
        have to know that to understand the stack.
        """
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-clara"
        assert (
            api.portal.get_registry_record("plone.bundles/plonetheme-clara.enabled")
            is True
        )

    def test_ships_no_second_javascript_or_stylesheet(self):
        """One override sheet: no forked Bootstrap, no second behaviour bundle."""
        assert not api.portal.get_registry_record(
            f"{BUNDLE}.jscompilation", default=""
        )

    def test_site_logo_is_the_derico_mark(self):
        from plone.formwidget.namedfile.converter import b64decode_file

        logo = api.portal.get_registry_record("plone.site_logo")
        assert logo, "the brand mark is the one part of the design that is not a token"
        filename, data = b64decode_file(logo)
        assert filename == "derico-logo.svg"
        assert b"<svg" in data

    def test_static_resources_are_traversable(self):
        """The bundle URL has to resolve, or the whole theme silently vanishes."""
        css = self.portal.restrictedTraverse(
            "++resource++plonetheme.derico/derico.css"
        )
        assert css is not None
        logo = self.portal.restrictedTraverse(
            "++resource++plonetheme.derico/derico-logo.svg"
        )
        assert logo is not None


class TestUninstall:
    """Test uninstallation."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = api.addon.get_installer(self.portal)
        self.installer.uninstall_product("plonetheme.derico")

    def test_addon_uninstalled(self):
        """Test addon is uninstalled."""
        assert not self.installer.is_product_installed("plonetheme.derico")

    def test_browserlayer_removed(self):
        from plone.browserlayer import utils

        assert IPlonethemeDericoLayer not in utils.registered_layers()

    def test_bundle_records_removed(self):
        """No orphaned bundle: derico.css must stop loading after uninstall."""
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled", default=None) is None
        assert (
            api.portal.get_registry_record(f"{BUNDLE}.csscompilation", default=None)
            is None
        )
