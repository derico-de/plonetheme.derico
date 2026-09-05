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
The tests read it from both sides — the fresh install and the site that
predates the version — plus the two things that make hiding the right verb
rather than removal: the elements keep their place in the stored order, and
uninstalling gives them back.
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


PROFILE = "plonetheme.derico.upgrades:1011"
UNINSTALL = "plonetheme.derico:uninstall"
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

    def _render_layout(self):
        """The whole managed layout, as a page renders it."""
        request = self.portal.REQUEST
        alsoProvides(request, IPlonethemeDericoLayer)
        view = self.portal.restrictedTraverse("@@plone")
        manager = getMultiAdapter(
            (self.portal, request, view), IContentProvider, name=MANAGER
        )
        manager.update()
        return manager.render()

    # ── the two sides of the same change ──────────────────────────────────

    @pytest.mark.parametrize("viewlet", sorted(ROWS))
    def test_a_fresh_install_hides_the_row(self, viewlet):
        """The default profile's half: installing derico hides it."""
        assert viewlet in self._hidden()

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

    # ── what the storage means for a rendered page ────────────────────────

    @pytest.mark.parametrize("viewlet,marker", sorted(ROWS.items()))
    def test_the_row_is_absent_from_the_rendered_layout(self, viewlet, marker):
        """The claim the storage assertions stand in for. The manager is a
        stock `OrderedViewletManager`, which filters the hidden names out of
        what it renders — but that is the base package's behaviour, not this
        theme's, and it is the whole reason a `hidden` node is the fix. If it
        ever stopped honouring the storage, every test above would still pass
        and the rows would still be on the page."""
        assert marker not in self._render_layout()

    @pytest.mark.parametrize("viewlet,marker", sorted(ROWS.items()))
    def test_the_row_renders_when_it_is_not_hidden(self, viewlet, marker):
        """The negative: each element is registered, has something to show and
        does render on this site — so the test above is measuring the hiding
        and not a footer that was empty all along."""
        self._seed_a_1010_site()
        assert marker in self._render_layout()

    # ── hidden, not removed ───────────────────────────────────────────────

    @pytest.mark.parametrize("viewlet", sorted(ROWS))
    def test_the_element_keeps_its_place_in_the_order(self, viewlet):
        """Hiding is the layout manager's own verb for an element it should
        keep knowing about: the stored sequence is untouched, so
        @@manage-layout-viewlets can put the row back."""
        assert viewlet in self.storage.getOrder(MANAGER, SKIN)

    @pytest.mark.parametrize("viewlet", KEPT)
    def test_the_rest_of_the_layout_stays(self, viewlet):
        """The blast radius of a `hidden` node is one manager, and everything
        else the theme renders shares it."""
        assert viewlet not in self._hidden()

    def test_the_rest_of_the_page_still_renders(self):
        """The three rows go; the page does not go with them.

        `plone.pageletlayout.body` is deliberately not among the names: it
        renders the PUBLISHED pagelet's content template, and this harness
        hands the manager `@@plone` rather than a published pagelet, so the
        body element cannot resolve its renderer here. The manager logs that
        and carries on, which is also why the absence tests above are paired
        with their positives — an element that merely errored would read as
        hidden otherwise."""
        markup = self._render_layout()
        for marker in (
            "element-logo",
            "element-globalnav",
            "element-searchbox",
            "element-breadcrumbs",
            "element-contentheader",
        ):
            assert marker in markup

    # ── the mirror ────────────────────────────────────────────────────────

    def test_uninstall_shows_the_rows_again(self):
        """Recreatable configuration this add-on owns: dropping the theme
        must not leave a site with three footer rows missing and nothing
        naming the add-on that hid them."""
        assert set(ROWS) <= set(self._hidden())
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{UNINSTALL}")
        assert not set(ROWS) & set(self._hidden())

    def test_uninstall_is_idempotent(self):
        """`remove` on a name that is not hidden has nothing to do — and in
        particular must not add it."""
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{UNINSTALL}")
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{UNINSTALL}")
        assert not set(ROWS) & set(self._hidden())

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

    def test_the_profile_is_at_this_version(self):
        """The newest step's test owns the exact version."""
        (version,) = self.setup_tool.getLastVersionForProfile(
            "plonetheme.derico:default"
        )
        assert int(version) == 1011

    # ── the three files that must agree ───────────────────────────────────

    @staticmethod
    def _node(text):
        """The `hidden` node's manager, skin and viewlet names."""
        match = re.search(r"<hidden\b(.*?)</hidden>", text, re.S)
        assert match, "no hidden node"
        body = match.group(0)
        return (
            re.findall(r'manager="([^"]+)"', body),
            re.findall(r'skinname="([^"]+)"', body),
            re.findall(r'<viewlet name="([^"]+)"', body),
        )

    @staticmethod
    def _profile(*parts):
        root = pathlib.Path(__file__).resolve().parent.parent
        return (root.joinpath("src/plonetheme/derico", *parts)).read_text()

    def test_the_upgrade_profile_carries_the_default_profile_s_node(self):
        """1011 hides on an existing site what the default profile hides on a
        fresh one; if the two drift, one kind of site keeps the rows."""
        assert self._node(
            self._profile("profiles/default/viewlets.xml")
        ) == self._node(self._profile("upgrades/1011/viewlets.xml"))

    def test_the_uninstall_profile_names_the_same_rows(self):
        """A row hidden on install and not named on uninstall would stay
        hidden on a site that dropped the theme."""
        default = self._node(self._profile("profiles/default/viewlets.xml"))
        uninstall = self._node(self._profile("profiles/uninstall/viewlets.xml"))
        assert default == uninstall

    def test_every_hidden_name_is_removed_on_uninstall(self):
        """The `remove` attribute is what makes the uninstall node an un-hide;
        without it the importer would append the name instead."""
        text = self._profile("profiles/uninstall/viewlets.xml")
        for viewlet in ROWS:
            assert re.search(
                rf'<viewlet name="{re.escape(viewlet)}" remove="True"\s*/>', text
            ), f"{viewlet} is not un-hidden on uninstall"

    def test_the_rows_hidden_are_the_rows_documented(self):
        """The default profile hides these three and no fourth: a row added
        here without a reason written next to it is the failure this catches."""
        _, _, names = self._node(self._profile("profiles/default/viewlets.xml"))
        assert sorted(names) == sorted(ROWS)
