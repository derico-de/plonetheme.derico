"""Tests for upgrade step 1010 -> 1011: the stock footer rows, hidden.

plone.pageletlayout closes a page with three elements, and a derico site has
its own answer for each. `siteactions` renders the `site_actions` category —
Sitemap, Accessibility, Contact — which are authored content here: the footer
is editable and the Actions block puts a category of portal actions on a page
as designed links, so the stock row renders the same actions twice.
`copyright` is Plone's copyright and GPL notice and `colophon` the „Powered by
Plone" badge; the design closes every page with its own footer band instead,
authored as footer blocks.

Hiding is per-site state (`IViewletSettingsStorage`), so the default profile
alone reaches no site that is already installed; that gap is what 1011 is.
This file covers the step itself, on the retired whole-body manager it
wrote to. Where the rows are hidden today — plone.portalfooter — and what a
fresh install, a rendered page and an uninstall do with them is
test_upgrade_step_1015.py.
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility


PROFILE = "plonetheme.derico.upgrades:1011"
MANAGER = "plone.pageletlayout.layout"
SKIN = "Plone Default"

#: The three rows, each with the class its element carries on the page. The
#: markup half matters: every storage assertion below would go on passing if
#: the manager stopped honouring the hidden list.
ROWS = {
    "plone.pageletlayout.copyright": "element-copyright",
    "plone.pageletlayout.colophon": "element-colophon",
    "plone.pageletlayout.siteactions": "element-siteactions",
}

#: Everything else the theme renders. A `hidden` node reaches one manager, and
#: these share it.
KEPT = (
    "plone.pageletlayout.logo",
    "plone.pageletlayout.globalnav",
    "plone.pageletlayout.searchbox",
    "plone.pageletlayout.breadcrumbs",
    "plone.pageletlayout.contentheader",
    "plone.pageletlayout.body",
)


class TestUpgrade1011:
    """Test upgrade to version 1011."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def _hidden(self):
        return self.storage.getHidden(MANAGER, SKIN)

    def _seed_a_1010_site(self):
        """The site that predates the version: the rows still showing."""
        self.storage.setHidden(
            MANAGER, SKIN, tuple(n for n in self._hidden() if n not in ROWS)
        )
        assert not set(ROWS) & set(self._hidden())

    def _apply(self):
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")

    # ── the step ──────────────────────────────────────────────────────────

    @pytest.mark.parametrize("viewlet", sorted(ROWS))
    def test_the_upgrade_hides_the_row(self, viewlet):
        """The existing site's half, which the default profile cannot reach."""
        self._seed_a_1010_site()
        self._apply()
        assert viewlet in self._hidden()

    def test_re_running_the_upgrade_changes_nothing(self):
        """The importer removes each name before appending it, so a second
        run neither duplicates an entry nor un-hides one."""
        self._apply()
        self._apply()
        hidden = list(self._hidden())
        for viewlet in ROWS:
            assert hidden.count(viewlet) == 1


    @pytest.mark.parametrize("viewlet", KEPT)
    def test_the_rest_of_the_layout_stays(self, viewlet):
        """The blast radius of a `hidden` node is one manager, and everything
        else the theme renders shares it."""
        assert viewlet not in self._hidden()

    # ── the step itself ───────────────────────────────────────────────────

    def test_upgrade_step_registered(self):
        steps = self.setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(
            step["sdest"] == "1011" and step["ssource"] == "1010" for step in flat
        )

    def test_upgrade_profile_is_hidden(self):
        from plonetheme.derico.setuphandlers import HiddenProfiles

        assert PROFILE in HiddenProfiles().getNonInstallableProfiles()
