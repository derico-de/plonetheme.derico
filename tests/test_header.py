"""The header: the design's bar on Clara's header elements.

The search is Clara's on-demand toggle (plonetheme.clara.search_on_demand,
set by derico's profile); header.css only places and dresses it. Looks are
not asserted here; test_override_minimality.py holds the token contract.
"""

import re

import pytest
from bs4 import BeautifulSoup
from plone import api
from plone.testing.zope import Browser
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer

from . import clara_css as css_tools


BUNDLE = "plone.bundles/plonetheme-derico-header"
PROVIDER = "plone.pageletlayout.searchbox"

HEADER_CSS = css_tools.STATIC / "header.css"
RECORD = "plonetheme.clara.search_on_demand"


class TestHeaderBundle:
    """One record, two files, both served."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_bundle_registered_and_enabled(self):
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/header.css"
        )

    def test_bundle_ships_no_script(self):
        """Clara's clara.js drives the search now."""
        assert not api.portal.get_registry_record(f"{BUNDLE}.jscompilation")
        assert not (css_tools.STATIC / "header.js").exists()

    def test_bundle_loads_after_the_token_layer(self):
        """Every value the sheet paints with is a token derico.css declares."""
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-derico"

    def test_stylesheet_is_traversable(self):
        """A record pointing at a missing file is a 404 on every page."""
        assert self.portal.restrictedTraverse("++resource++plonetheme.derico/header.css")

    def test_uninstall_profile_removes_the_record(self):
        """The mirror of the default profile, so uninstall leaves no orphan
        bundle requesting a stylesheet the site no longer ships."""
        uninstall = css_tools.PACKAGE / "src/plonetheme/derico/profiles/uninstall/registry.xml"
        text = uninstall.read_text()
        assert re.search(
            rf'prefix="{re.escape(BUNDLE)}"\s+remove="true"', text
        ), "profiles/uninstall/registry.xml does not remove the header bundle"


class TestOnDemandSearch:
    """Clara's searchbox, switched to its on-demand toggle."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]

    def _render(self):
        alsoProvides(self.request, IPlonethemeDericoLayer)
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal, self.request, view), IContentProvider, name=PROVIDER
        )
        provider.update()
        return BeautifulSoup(provider.render(), "html.parser")

    def test_the_record_is_on(self):
        assert api.portal.get_registry_record(RECORD) is True

    def test_the_header_renders_the_toggle(self):
        soup = self._render()
        box = soup.select_one("#portal-searchbox")
        assert "searchbox-on-demand" in box["class"]
        assert box.select_one(":scope > input.opener#portal-searchbox-opener")
        assert box.select_one(":scope > label.searchbox-toggle[for=portal-searchbox-opener]")

    def test_the_form_keeps_livesearch(self):
        form = self._render().select_one("form#searchGadget_form")
        assert "pat-livesearch" in form["class"]
        assert form["action"] == f"{self.portal.absolute_url()}/@@search"


def test_the_page_header_is_on_demand(functional):
    browser = Browser(functional["app"])
    browser.open(functional["portal"].absolute_url())
    soup = BeautifulSoup(browser.contents, "html.parser")
    assert soup.select_one("#portal-top .searchbox-on-demand .searchbox-toggle")
    assert "header.js" not in browser.contents


class TestHeaderSheet:
    """The sheet's own claims — what test_override_minimality.py does not
    already hold every theme sheet to."""

    def test_no_layer_no_important(self):
        """Unlayered by design (it has to beat Clara's layered component
        rules), and never by force."""
        text = css_tools.strip_comments(HEADER_CSS.read_text())
        assert "@layer" not in text
        assert "!important" not in text

    def test_addresses_only_the_header(self):
        """Every selector names a header element, the layout container (its
        own knobs), the header landmark (the hairline pseudo item) or a
        descendant of one — the sheet reaches nothing beyond the bar."""
        roots = (
            ".plone-layout",
            "#portal-top",
            "#portal-logo",
            ".element-anontools",
            ".element-globalnav",
            "#portal-globalnav",
            ".globalnav-toggle",
            ".element-searchbox",
            ".searchbox-toggle",
            ".element-language",
        )
        for selector, _ in css_tools.rules(HEADER_CSS.read_text()):
            for part in selector.split(","):
                part = css_tools.normalise_selector(part)
                assert part.startswith(roots), f"{part!r} reaches outside the header"

    def test_the_closed_form_stays_hidden(self):
        """Unlayered, any `display` here beats Clara's closed state; only the
        open state may set one."""
        for selector, body in css_tools.rules(HEADER_CSS.read_text()):
            for part in selector.split(","):
                part = css_tools.normalise_selector(part)
                if part.endswith(("form", ".livesearch-results")) and "display" in body:
                    assert ":checked" in part, f"{part!r} would show a closed search"

    def test_reduced_motion_covers_every_animation(self):
        """Every animation and transition is declared under
        `prefers-reduced-motion: no-preference`; outside it there is none."""
        text = css_tools.strip_comments(HEADER_CSS.read_text())
        outside = re.sub(
            r"@media \(prefers-reduced-motion: no-preference\) \{.*?\n\}\n", "", text, flags=re.S
        )
        assert "transition" not in outside
        assert "animation:" not in outside


class TestLivesearchPanel:
    """The results panel is this sheet's in full, not a re-dress.

    `pat-livesearch` is written around its own `livesearch.scss` — the
    `position: absolute` that makes the list a dropdown — and that sheet
    reaches a page only through Barceloneta's bundle: the pattern's own
    `import("./livesearch.scss")` is commented out in mockup. On Clara it
    never loads, so an unpositioned list takes its place in the flow and
    pushes the whole page down by the height of the results. These hold the
    three declarations that stop it, each of which would fail in silence.
    """

    def _bodies(self, selector):
        return [
            body
            for sel, body in css_tools.rules(HEADER_CSS.read_text())
            if css_tools.normalise_selector(sel) == selector
        ]

    @pytest.mark.skipif(
        css_tools.clara_bundle_path() is None,
        reason="plonetheme.clara's compiled bundle is not available",
    )
    def test_the_base_theme_still_ships_no_livesearch_styles(self):
        """The premise. If Clara ever dresses the pattern, revisit below."""
        assert "livesearch" not in css_tools.clara_bundle_path().read_text()

    def test_the_panel_hangs_from_the_searchbox(self):
        bodies = self._bodies(".element-searchbox .livesearch-results")
        assert bodies, "the sheet no longer dresses the results list"
        assert "position: absolute" in bodies[0], (
            "the panel must be positioned here; unpositioned it lands in the "
            "flow and pushes the page down"
        )
        assert "z-index" in bodies[0], "a dropdown that the page paints over"

    def test_the_narrow_layout_puts_it_back_in_the_flow(self):
        """`display: contents` on the box leaves nothing to hang from."""
        assert any("position: static" in body for body in self._bodies(
            ".element-searchbox .livesearch-results"
        )), "the narrow header must place the panel as a row of its own"

    @pytest.mark.skipif(
        css_tools.clara_bundle_path() is None,
        reason="plonetheme.clara's compiled bundle is not available",
    )
    def test_closing_the_search_takes_the_panel_with_it(self):
        """Clara hides everything after the closed toggle, results included."""
        css = css_tools.clara_bundle_path().read_text()
        assert re.search(
            r"\.searchbox-on-demand>\.opener:not\(:checked\)~:not\(\.searchbox-toggle\)\{display:none",
            css,
        )


class TestLanguageSwitch:
    """The design's `DE / EN`, on Clara's language element.

    The element itself is Clara's (plonetheme.clara.languageselector) and
    exists because plone.app.multilingual registers its selector for a viewlet
    manager the pagelet layout never renders. What is derico's is where it
    stands in the bar and what it costs the row it stands in — and both are
    arithmetic, so both are pinned here.
    """

    def _bodies(self, selector):
        return [
            body
            for sel, body in css_tools.rules(HEADER_CSS.read_text())
            if css_tools.normalise_selector(sel) == selector
        ]

    def test_the_sheet_dresses_the_element(self):
        assert self._bodies(".element-language"), (
            "the header sheet no longer dresses the language switch"
        )

    def test_the_slash_is_drawn_not_written(self):
        """The mockup ships `<li aria-hidden="true">/</li>`; Clara's markup
        does not, and should not — a separator that can be selected, read
        aloud or sent to a translator is a word pretending to be a rule.

        Generated between items rather than after each: a third language gets
        two slashes and a single one gets none, with nothing to configure."""
        bodies = self._bodies(".element-language li + li::before")
        assert bodies, "the switch has lost its separator"
        assert 'content: "/"' in bodies[0]

    def test_the_current_language_is_marked_twice(self):
        """Ink AND an underline, so the marker survives a greyscale print."""
        bodies = self._bodies(".element-language .currentLanguage a")
        assert bodies, "the current language is no longer marked"
        assert "color:" in bodies[0] and "text-decoration: underline" in bodies[0]

    def test_the_end_lane_counts_the_switch(self):
        """`--derico-header-lane-end` is what the navigation keeps clear, and
        the switch stands in it. Stated as a sum of the three widths rather
        than as one measured number, so the lane and the margins that place
        the three elements cannot drift apart."""
        lane = css_tools.declarations(
            HEADER_CSS.read_text(), [".plone-layout"]
        )["--derico-header-lane-end"]
        for knob in (
            "--derico-header-toggle",
            "--derico-header-lang",
            "--derico-header-login",
        ):
            assert knob in lane, f"the end lane no longer counts {knob}"

    def test_the_lane_is_free_again_without_a_switch(self):
        """A monolingual site renders no switch at all (the pagelet's
        render() returns ""), and a lane reserved for an absent element would
        move the login link for nothing."""
        text = css_tools.strip_comments(HEADER_CSS.read_text())
        base = css_tools.declarations(HEADER_CSS.read_text(), [".plone-layout"])
        assert base["--derico-header-lang"] == "0rem"
        assert ".plone-layout:has(#portal-top > .element-language)" in text, (
            "nothing asks whether the switch is actually there"
        )

    def test_the_narrow_bar_keeps_the_switch(self):
        """The mockup keeps `DE / EN` on the bar row at every width — only
        the login link folds into the opened menu. The menu pill has to clear
        both the magnifier and the switch to leave room for it."""
        pill = self._bodies(".globalnav-toggle")
        assert pill, "the narrow header has lost its menu pill"
        clearing = [body for body in pill if "--derico-header-lang" in body]
        assert clearing, (
            "the menu pill does not clear the language switch; on the narrow "
            "bar the two would sit on top of each other"
        )
