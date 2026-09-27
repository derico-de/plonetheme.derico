"""The footer rows and the lead image, hidden in their slots."""

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


class TestHiddenViewlets:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def _hidden(self, manager=FOOTER):
        return self.storage.getHidden(manager, SKIN)

    def _unhide_all(self):
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
        self._unhide_all()
        assert marker in self._render(FOOTER)

    def test_the_header_still_renders(self):
        header = self._render("plone.portalheader") + self._render(
            "plone.mainnavigation"
        )
        for marker in ("element-logo", "element-globalnav", "element-searchbox"):
            assert marker in header

    # ── the mirror ────────────────────────────────────────────────────────

    def test_uninstall_shows_everything_again(self):
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{UNINSTALL}")
        assert not set(ROWS) & set(self._hidden())
        assert LEAD_IMAGE not in self._hidden(TITLE)

    # ── the files that must agree ─────────────────────────────────────────

    def test_the_uninstall_profile_names_the_same_viewlets(self):
        assert _nodes(_profile("profiles/uninstall/viewlets.xml")) == _nodes(
            _profile("profiles/default/viewlets.xml")
        )
