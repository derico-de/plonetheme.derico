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
