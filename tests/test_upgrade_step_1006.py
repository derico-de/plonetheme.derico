"""Tests for upgrade step 1005 -> 1006: the contact band on an existing site.

1006 is purely declarative — two import steps against an upgrade profile that
holds exactly the two files 1005 did not have. So what is worth testing is the
gap it closes: a site upgraded from 1005 has a stored layout order with no
band in it, and a registry with neither the band's stylesheet bundle nor the
setting behind its call to action.

The band itself is gone — 1009 retires it, and its content is authored as a
footer block instead. This step stays, and stays tested: a site sitting at
1005 still walks the whole chain, and a step that errors on the way past is a
site that cannot be upgraded at all. The record name is spelled out here now
that no module declares it.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility


CONTACT_PAGE_RECORD = "plonetheme.derico.contact_page"

PROFILE = "plonetheme.derico.upgrades:1006"
VIEWLET = "plonetheme.derico.contactband"
MANAGER = "plone.pageletlayout.layout"
BUNDLE = "plone.bundles/plonetheme-derico-contact"


class TestUpgrade1006:
    """Test upgrade to version 1006."""

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

    def test_the_upgrade_places_the_band_in_the_layout(self):
        """The 1005 site: the element exists, the stored order predates it."""
        order = [
            name
            for name in self.storage.getOrder(MANAGER, "Plone Default")
            if name != VIEWLET
        ]
        self.storage.setOrder(MANAGER, "Plone Default", tuple(order))
        assert VIEWLET not in self.storage.getOrder(MANAGER, "Plone Default")

        self._apply()

        upgraded = list(self.storage.getOrder(MANAGER, "Plone Default"))
        assert VIEWLET in upgraded
        assert upgraded.index(VIEWLET) < upgraded.index(
            "plone.pageletlayout.copyright"
        )

    def test_the_upgrade_registers_the_stylesheet_and_the_setting(self):
        self._apply()

        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(CONTACT_PAGE_RECORD) == "contact"

    def test_re_running_the_upgrade_changes_nothing(self):
        """insert-before removes the name before re-inserting it, so a second
        run must not leave the band in the order twice."""
        self._apply()
        self._apply()

        order = list(self.storage.getOrder(MANAGER, "Plone Default"))
        assert order.count(VIEWLET) == 1
