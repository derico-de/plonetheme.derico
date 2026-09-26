"""Tests for upgrade step 1014 -> 1015: the rows and the lead image, hidden
in their slots.

plone.pageletlayout renders its elements in the stock viewlet managers now, so
the three footer rows derico hides live in plone.portalfooter, and the content
header's managers render on every page — plone.abovecontenttitle among them,
where plone.app.contenttypes puts the lead image. The tests read the hidden
set from a fresh install, a site that predates 1015, a rendered manager and an
uninstall.
"""

import pathlib
import re

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


PROFILE = "plonetheme.derico.upgrades:1015"
UNINSTALL = "plonetheme.derico:uninstall"
SKIN = "Plone Default"
FOOTER = "plone.portalfooter"
TITLE = "plone.abovecontenttitle"
LEAD_IMAGE = "contentleadimage"

#: The three rows, each with the class its element carries on the page.
ROWS = {
    "plone.pageletlayout.copyright": "element-copyright",
    "plone.pageletlayout.colophon": "element-colophon",
    "plone.pageletlayout.siteactions": "element-siteactions",
}


def _profile(*parts):
    root = pathlib.Path(__file__).resolve().parent.parent
    return root.joinpath("src/plonetheme/derico", *parts).read_text()


def _nodes(text):
    """Each `hidden` node's manager with its viewlet names."""
    return {
        manager: re.findall(r'<viewlet name="([^"]+)"', body)
        for manager, body in re.findall(
            r'<hidden manager="([^"]+)"[^>]*>(.*?)</hidden>', text, re.S
        )
    }


class TestUpgrade1015:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def _hidden(self, manager=FOOTER):
        return self.storage.getHidden(manager, SKIN)

    def _seed_a_1014_site(self):
        """Rows and lead image showing: the hidden sets without our names."""
        self.storage.setHidden(
            FOOTER, SKIN, tuple(n for n in self._hidden() if n not in ROWS)
        )
        self.storage.setHidden(
            TITLE, SKIN, tuple(n for n in self._hidden(TITLE) if n != LEAD_IMAGE)
        )

    def _render(self, manager):
        request = self.portal.REQUEST
        alsoProvides(request, IPlonethemeDericoLayer)
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal, request, view), IContentProvider, name=manager
        )
        provider.update()
        return provider.render()

    # ── a fresh install ───────────────────────────────────────────────────

    @pytest.mark.parametrize("viewlet", sorted(ROWS))
    def test_a_fresh_install_hides_the_row(self, viewlet):
        assert viewlet in self._hidden()

    def test_a_fresh_install_hides_the_lead_image(self):
        assert LEAD_IMAGE in self._hidden(TITLE)

    @pytest.mark.parametrize("viewlet,marker", sorted(ROWS.items()))
    def test_the_row_is_absent_from_the_footer(self, viewlet, marker):
        assert marker not in self._render(FOOTER)

    @pytest.mark.parametrize("viewlet,marker", sorted(ROWS.items()))
    def test_the_row_renders_when_it_is_not_hidden(self, viewlet, marker):
        """The negative: the test above measures the hiding, not an empty
        footer."""
        self._seed_a_1014_site()
        assert marker in self._render(FOOTER)

    def test_the_header_still_renders(self):
        header = self._render("plone.portalheader") + self._render(
            "plone.mainnavigation"
        )
        for marker in ("element-logo", "element-globalnav", "element-searchbox"):
            assert marker in header

    # ── the step ──────────────────────────────────────────────────────────

    def test_the_upgrade_hides_rows_and_lead_image(self):
        self._seed_a_1014_site()
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        assert set(ROWS) <= set(self._hidden())
        assert LEAD_IMAGE in self._hidden(TITLE)

    def test_re_running_the_upgrade_changes_nothing(self):
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        hidden = list(self._hidden())
        for viewlet in ROWS:
            assert hidden.count(viewlet) == 1

    def test_the_profile_is_at_this_version(self):
        """The newest step's test owns the exact version."""
        (version,) = self.setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) == 1015

    def test_upgrade_profile_is_hidden(self):
        from plonetheme.derico.setuphandlers import HiddenProfiles

        assert PROFILE in HiddenProfiles().getNonInstallableProfiles()

    # ── the mirror ────────────────────────────────────────────────────────

    def test_uninstall_shows_everything_again(self):
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{UNINSTALL}")
        assert not set(ROWS) & set(self._hidden())
        assert LEAD_IMAGE not in self._hidden(TITLE)

    # ── the files that must agree ─────────────────────────────────────────

    def test_the_upgrade_profile_carries_the_default_profile_s_nodes(self):
        default = _nodes(_profile("profiles/default/viewlets.xml"))
        assert _nodes(_profile("upgrades/1015/viewlets.xml")) == default
        assert default == {FOOTER: sorted(ROWS, key=list(ROWS).index), TITLE: [LEAD_IMAGE]}

    def test_the_uninstall_profile_names_the_same_viewlets(self):
        assert _nodes(_profile("profiles/uninstall/viewlets.xml")) == _nodes(
            _profile("profiles/default/viewlets.xml")
        )
