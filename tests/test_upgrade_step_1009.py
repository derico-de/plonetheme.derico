"""Tests for upgrade step 1008 -> 1009: the contact band, retired.

The band's markup, template, stylesheet and registrations left with this
version, but three things it wrote into a SITE do not go with them: its name
in the stored layout order, its stylesheet bundle record and the setting
behind its call to action. Dropping the ZCML does not touch any of the three
— a registry record outlives the code that read it, and the layout order is
per-site state — so 1009 is 1006 in reverse, and these tests are the same
gap read from the other side.

The bundle is the one with teeth: left registered, every page would go on
requesting `++resource++plonetheme.derico/contact.css`, a resource this
version no longer ships.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility


PROFILE = "plonetheme.derico.upgrades:1009"
VIEWLET = "plonetheme.derico.contactband"
MANAGER = "plone.pageletlayout.layout"
BUNDLE = "plone.bundles/plonetheme-derico-contact"
CONTACT_PAGE_RECORD = "plonetheme.derico.contact_page"


class TestUpgrade1009:
    """Test upgrade to version 1009."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def _apply(self):
        for step in ("viewlets", "plone.app.registry"):
            self.setup_tool.runImportStepFromProfile(
                f"profile-{PROFILE}", step, run_dependencies=False
            )

    def _seed_a_1008_site(self):
        """A site that went through 1006: order, bundle and setting present."""
        order = list(self.storage.getOrder(MANAGER, "Plone Default"))
        if VIEWLET not in order:
            order.insert(0, VIEWLET)
            self.storage.setOrder(MANAGER, "Plone Default", tuple(order))
        self.setup_tool.runImportStepFromProfile(
            "profile-plonetheme.derico.upgrades:1006",
            "plone.app.registry",
            run_dependencies=False,
        )

    def test_the_upgrade_takes_the_band_out_of_the_layout(self):
        self._seed_a_1008_site()
        assert VIEWLET in self.storage.getOrder(MANAGER, "Plone Default")

        self._apply()

        assert VIEWLET not in self.storage.getOrder(MANAGER, "Plone Default")

    def test_the_upgrade_leaves_the_rest_of_the_layout_alone(self):
        """A removal, not a reordering: the file names one viewlet."""
        self._seed_a_1008_site()
        before = [
            name
            for name in self.storage.getOrder(MANAGER, "Plone Default")
            if name != VIEWLET
        ]

        self._apply()

        assert list(self.storage.getOrder(MANAGER, "Plone Default")) == before

    def test_the_upgrade_drops_the_stylesheet_and_the_setting(self):
        self._seed_a_1008_site()
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True

        self._apply()

        assert (
            api.portal.get_registry_record(f"{BUNDLE}.enabled", default=None) is None
        ), "the bundle would keep every page requesting a resource that is gone"
        assert (
            api.portal.get_registry_record(CONTACT_PAGE_RECORD, default=None) is None
        )

    def test_re_running_the_upgrade_changes_nothing(self):
        """`remove` on an absent name, and a record removal twice over."""
        self._seed_a_1008_site()
        self._apply()
        self._apply()

        assert VIEWLET not in self.storage.getOrder(MANAGER, "Plone Default")
        assert (
            api.portal.get_registry_record(f"{BUNDLE}.enabled", default=None) is None
        )

    def test_a_fresh_install_never_had_any_of_it(self):
        """1009 is for existing sites; the default profile says nothing."""
        assert VIEWLET not in self.storage.getOrder(MANAGER, "Plone Default")
        assert (
            api.portal.get_registry_record(f"{BUNDLE}.enabled", default=None) is None
        )
        assert (
            api.portal.get_registry_record(CONTACT_PAGE_RECORD, default=None) is None
        )
