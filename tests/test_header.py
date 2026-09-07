"""The header: the design's bar on Clara's header elements.

Three things ship it — the searchbox override (browser/configure.zcml +
templates/searchbox.pt), the header bundle (registry.xml: header.css +
header.js) and the layer change that makes the override win — and each is
checked from the side that would fail silently without it: the provider that
renders, the record the page reads, the layer the lookup resolves through.

Looks are not asserted here. The stylesheet's contract with Clara — that it
names no `--clara-*` token and reads only tokens derico.css declares — is
test_override_minimality.py's, which globs every sheet under static/.
"""

import re

import pytest
from bs4 import BeautifulSoup
from plone import api
from plone.app.testing import logout
from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer
from plone.pageletlayout.pagelets.header import SearchboxChromePagelet
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer

from . import clara_css as css_tools


BUNDLE = "plone.bundles/plonetheme-derico-header"
PROVIDER = "plone.pageletlayout.searchbox"

HEADER_CSS = css_tools.STATIC / "header.css"
HEADER_JS = css_tools.STATIC / "header.js"


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
        assert api.portal.get_registry_record(f"{BUNDLE}.jscompilation") == (
            "++resource++plonetheme.derico/header.js"
        )

    def test_bundle_loads_after_the_token_layer(self):
        """Every value the sheet paints with is a token derico.css declares."""
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-derico"

    @pytest.mark.parametrize("filename", ["header.css", "header.js"])
    def test_static_resources_are_traversable(self, filename):
        """A record pointing at a missing file is a 404 on every page."""
        resource = self.portal.restrictedTraverse(
            f"++resource++plonetheme.derico/{filename}"
        )
        assert resource is not None

    def test_uninstall_profile_removes_the_record(self):
        """The mirror of the default profile, so uninstall leaves no orphan
        bundle requesting a stylesheet the site no longer ships."""
        uninstall = css_tools.PACKAGE / "src/plonetheme/derico/profiles/uninstall/registry.xml"
        text = uninstall.read_text()
        assert re.search(
            rf'prefix="{re.escape(BUNDLE)}"\s+remove="true"', text
        ), "profiles/uninstall/registry.xml does not remove the header bundle"

    def test_upgrade_profile_carries_the_same_record(self):
        """1010 adds the record to an existing site; it must be the record
        the default profile installs, byte for byte in every value."""
        default = (
            css_tools.PACKAGE
            / "src/plonetheme/derico/profiles/default/registry.xml"
        ).read_text()
        upgrade = (
            css_tools.PACKAGE
            / "src/plonetheme/derico/upgrades/1010/registry.xml"
        ).read_text()

        def record(text):
            match = re.search(
                rf'<records[^>]*prefix="{re.escape(BUNDLE)}">(.*?)</records>', text, re.S
            )
            assert match, "record not found"
            return sorted(re.findall(r"<value key=\"(\w+)\">(.*?)</value>", match.group(1)))

        assert record(default) == record(upgrade)


class TestSearchboxOverride:
    """The same provider name as the base, on the theme's layer."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]

    def _render(self, layered=True):
        # The test request arrives with every installed browser layer already
        # marked on it (plone.browserlayer marks on traversal, which the
        # integration layer simulates), so "off the theme's layer" is a
        # removal, not the absence of an addition.
        if layered:
            alsoProvides(self.request, IPlonethemeDericoLayer)
        else:
            noLongerProvides(self.request, IPlonethemeDericoLayer)
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal, self.request, view), IContentProvider, name=PROVIDER
        )
        provider.update()
        return BeautifulSoup(provider.render(), "html.parser")

    def test_layer_extends_the_pagelet_layout_layer(self):
        """What makes the override unambiguous: a request that provides the
        theme's layer provides the base layer THROUGH it, so the more
        specific registration is the theme's and never a coin toss between
        two unrelated layers."""
        assert IPlonethemeDericoLayer.extends(IPlonePageletlayoutLayer)

    def test_override_wins_on_the_theme_layer(self):
        soup = self._render()
        assert soup.select_one("#portal-searchbox > .opener#portal-searchbox-opener")
        toggle = soup.select_one("#portal-searchbox > label.searchbox-toggle")
        assert toggle["for"] == "portal-searchbox-opener"
        assert len(toggle.select("svg.searchbox-toggle__glyph")) == 2

    def test_base_template_off_the_theme_layer(self):
        """Every other layer keeps plone.pageletlayout's always-open form."""
        soup = self._render(layered=False)
        assert soup.select_one("#portal-searchbox")
        assert not soup.select_one(".searchbox-toggle")

    def test_provider_is_the_base_class(self):
        """The class stays the base's: livesearch setting and action URL are
        its computation, and this template reads exactly those."""
        alsoProvides(self.request, IPlonethemeDericoLayer)
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal, self.request, view), IContentProvider, name=PROVIDER
        )
        assert isinstance(provider, SearchboxChromePagelet)

    def test_form_keeps_the_base_contract(self):
        """`pat-livesearch` and `@@search` read the form by id, name and
        class; the override changes how it opens, not what it submits."""
        soup = self._render()
        form = soup.select_one("form#searchGadget_form")
        assert form["action"] == f"{self.portal.absolute_url()}/@@search"
        assert form["role"] == "search"
        assert "pat-livesearch" in form["class"]
        assert form["data-pat-livesearch"] == (
            f"ajaxUrl:{self.portal.absolute_url()}/@@ajax-search"
        )
        field = form.select_one("input#searchGadget")
        assert field["name"] == "SearchableText"
        assert field["type"] == "text", "pat-livesearch binds input[type=text]"
        assert "searchField" in field["class"]
        assert form.select_one("button.searchButton[type=submit]")
        assert form.select_one("#portal-advanced-search a")["href"].endswith("/@@search")

    def test_toggle_has_an_accessible_name(self):
        """The label's text is visually hidden, never absent."""
        soup = self._render()
        name = soup.select_one(".searchbox-toggle .visually-hidden")
        assert name and name.get_text(strip=True)

    def test_submit_keeps_its_label(self):
        soup = self._render()
        assert soup.select_one("button.searchButton .visually-hidden").get_text(strip=True)

    def test_renders_for_anonymous(self):
        logout()
        soup = self._render()
        assert soup.select_one(".searchbox-toggle")


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
        own knobs and the hairline pseudo item) or a descendant of one —
        the sheet reaches nothing beyond the bar."""
        roots = (
            ".plone-layout",
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

    def test_script_is_gestures_only(self):
        """It toggles the checkbox and moves focus; it never writes markup
        or styles, which stay the template's and the sheet's."""
        text = HEADER_JS.read_text()
        for forbidden in (
            "innerHTML",
            "insertAdjacentHTML",
            "createElement",
            ".style.",
            "classList",
        ):
            assert forbidden not in text, f"header.js uses {forbidden}"

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

    def test_closing_the_search_takes_the_panel_with_it(self):
        """The pattern inserts the list beside the form, not inside it."""
        hidden = [
            body
            for sel, body in css_tools.rules(HEADER_CSS.read_text())
            if ".opener:not(:checked)" in css_tools.normalise_selector(sel)
            and "livesearch-results" in css_tools.normalise_selector(sel)
        ]
        assert hidden and all("display: none" in body for body in hidden), (
            "a closed search must not leave its results standing over the page"
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
        assert ".plone-layout:has(> .element-language)" in text, (
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
