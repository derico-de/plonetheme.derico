"""The contact band: placement in the layout, its two links, its stylesheet.

Three things about it can break quietly, so each has its own group below.

* Placement is stored per site (IViewletSettingsStorage), not derived from the
  registration, so a viewlets.xml that never ran leaves a band that renders
  nowhere while every other test still passes.
* Both links are looked up rather than written down — a registry record for
  the page, Plone's own sender address for the mail — and every failure mode
  of a lookup is "no link", which is also what a correctly configured site
  shows on the contact page itself.
* The band has to be able to melt into an accent-tinted block above it. That
  is a claim about two colours being the same custom property and about one
  piece of padding not being there; both are read off the stylesheet.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.pagelets import CONTACT_PAGE_RECORD
from plonetheme.derico.pagelets import ContactBandChromePagelet
from plonetheme.derico.pagelets import EMAIL_RECORD

from . import clara_css as css_tools


VIEWLET = "plonetheme.derico.contactband"
MANAGER = "plone.pageletlayout.layout"
BUNDLE = "plone.bundles/plonetheme-derico-contact"
CONTACT_CSS = css_tools.STATIC / "contact.css"


class TestPlacement:
    """Where the band renders, which is a stored order and not a registration."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        storage = getUtility(IViewletSettingsStorage)
        self.order = list(storage.getOrder(MANAGER, "Plone Default"))

    def test_the_band_is_in_the_layout_order(self):
        assert VIEWLET in self.order

    def test_the_band_comes_after_the_page_body(self):
        """Under the content: the whole point of the placement."""
        assert self.order.index(VIEWLET) > self.order.index(
            "plone.pageletlayout.body"
        )

    def test_the_band_comes_before_every_footer_row(self):
        """The mockup closes with band then footer, never the other way round."""
        for row in (
            "plone.pageletlayout.copyright",
            "plone.pageletlayout.colophon",
            "plone.pageletlayout.siteactions",
        ):
            assert self.order.index(VIEWLET) < self.order.index(row), row

    def test_the_band_is_not_hidden(self):
        storage = getUtility(IViewletSettingsStorage)
        assert VIEWLET not in storage.getHidden(MANAGER, "Plone Default")

    def test_the_base_order_is_not_forked(self):
        """insert-before is additive: nothing the base package ships is lost."""
        from plone.pageletlayout.pagelets.layout import ELEMENTS

        assert set(ELEMENTS) <= set(self.order)


class TestRendering:
    """The pagelet's own two lookups, and the markup they produce."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        # not `contact`: Plone reserves that id on the site root.
        self.portal.invokeFactory("Document", "contact-page", title="Contact")
        self.portal.invokeFactory("Document", "somewhere", title="Somewhere")
        api.portal.set_registry_record(CONTACT_PAGE_RECORD, "contact-page")
        api.portal.set_registry_record(EMAIL_RECORD, "hello@example.com")

    def _render(self, context):
        pagelet = ContactBandChromePagelet(context, self.request)
        pagelet.update()
        return pagelet.render()

    def test_it_is_registered_under_the_name_the_layout_asks_for(self):
        """The wrapper viewlet looks the element up BY NAME, on (context,
        request, view) — so the class working says nothing about the page
        getting it."""
        view = self.portal.restrictedTraverse("@@plone")
        pagelet = getMultiAdapter(
            (self.portal.somewhere, self.request, view),
            IContentProvider,
            name="plonetheme.derico.contactband",
        )
        pagelet.update()

        assert "element-contact-band" in pagelet.render()

    def test_it_renders_the_designs_heading(self):
        markup = self._render(self.portal.somewhere)
        assert "element-contact-band" in markup
        assert "Arrange an initial conversation" in markup

    def test_the_call_to_action_points_at_the_configured_page(self):
        markup = self._render(self.portal.somewhere)
        assert self.portal["contact-page"].absolute_url() in markup

    def test_the_mail_link_is_the_sites_own_sender_address(self):
        """A theme that shipped its author's address would mail derico from
        every site that ever installed it."""
        assert "mailto:hello@example.com" in self._render(self.portal.somewhere)

    def test_the_call_to_action_is_dropped_on_the_page_it_points_at(self):
        markup = self._render(self.portal["contact-page"])
        assert "clara-button" not in markup
        assert "mailto:hello@example.com" in markup

    def test_it_still_renders_when_the_record_is_empty(self):
        api.portal.set_registry_record(CONTACT_PAGE_RECORD, "")
        markup = self._render(self.portal.somewhere)
        assert "element-contact-band" in markup
        assert "clara-button" not in markup

    def test_it_still_renders_when_the_record_points_nowhere(self):
        """A mistyped path must cost the button, not the page."""
        api.portal.set_registry_record(CONTACT_PAGE_RECORD, "no-such-page")
        markup = self._render(self.portal.somewhere)
        assert "element-contact-band" in markup
        assert "clara-button" not in markup

    def test_the_action_row_goes_when_neither_link_survives(self):
        api.portal.set_registry_record(CONTACT_PAGE_RECORD, "")
        api.portal.set_registry_record(EMAIL_RECORD, "")
        assert "contact-band-actions" not in self._render(self.portal.somewhere)


class TestInstall:
    """The stylesheet and the setting, as the profile leaves them."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_the_stylesheet_bundle_is_registered_and_enabled(self):
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/contact.css"
        )

    def test_the_bundle_loads_after_the_token_layer(self):
        """Every value the band paints with is declared by derico.css."""
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == (
            "plonetheme-derico"
        )

    def test_the_stylesheet_is_served(self):
        """The bundle above only names a URL; nothing else in the install
        would notice the file behind it 404ing."""
        resources = self.portal.restrictedTraverse("++resource++plonetheme.derico")

        assert resources["contact.css"] is not None

    def test_the_contact_page_record_defaults_to_plones_own_starter_page(self):
        assert api.portal.get_registry_record(CONTACT_PAGE_RECORD) == "contact"


class TestMelt:
    """The band flows into an accent block above it, or it is just a box.

    Both halves are stylesheet claims. Asserting them here rather than in a
    browser is the same trade the rest of this package's CSS tests make: the
    values are what can silently drift, and a rendered screenshot cannot say
    which custom property a colour came from.
    """

    SHEET = css_tools.strip_comments(CONTACT_CSS.read_text())

    def _band_rules(self):
        return [
            body
            for selector, body in css_tools.rules(self.SHEET)
            if ".element-contact-band" in selector
        ]

    def test_the_ground_is_the_aurora_accent_slot(self):
        """Not a colour of its own, and not the design's committed cyan band:
        a block can only be tinted from the palette, so naming the slot's own
        custom property is what makes the two grounds provably identical."""
        grounds = [
            body
            for body in self._band_rules()
            if "var(--aurora-block-bg-accent)" in body
        ]
        assert grounds, "the band must paint the accent slot's own property"

    def test_the_band_opens_with_no_space_and_no_rule(self):
        joined = "\n".join(self._band_rules())
        assert "margin-block-start: 0" in joined
        assert "border-block-start" not in joined
        assert "border-block:" not in joined

    def test_the_body_drops_its_closing_air_under_an_accent_block(self):
        """The other half of the melt: `.element-body` closes with
        `padding-block-end` on the page ground, which would show as a strip
        between two identical accents."""
        matches = [
            (selector, body)
            for selector, body in css_tools.rules(self.SHEET)
            if ".element-body" in selector
        ]
        assert len(matches) == 1
        selector, body = matches[0]
        assert "padding-block-end: 0" in body
        assert ":last-child" in selector
        assert "has--backgroundColor--accent" in selector

    def test_the_melt_is_not_opened_for_the_other_slots(self):
        """`grey` and `dark` want the separation the strip gives them."""
        assert "has--backgroundColor--grey" not in self.SHEET
        assert "has--backgroundColor--dark" not in self.SHEET


class TestLinkColours:
    """The local repair of Clara's `a:not(.btn)`.

    Clara paints both link classes at 0,1,0 and then repaints every anchor at
    0,1,1 in the same layer, so on the published page the call to action came
    out link-cyan on its copper fill — 1.4:1 — and the quiet link came out
    cyan where the design asks for ink. contact.css restates both at 0,2,0.

    Remove this group together with the rules the day Clara stops overriding
    its own button; leaving it would then pin a repair that is no longer a
    repair.
    """

    SHEET = css_tools.strip_comments(CONTACT_CSS.read_text())

    def _declared(self, needle):
        return [
            body
            for selector, body in css_tools.rules(self.SHEET)
            if needle in selector and "color:" in body
        ]

    def test_the_call_to_action_keeps_its_label_colour(self):
        bodies = self._declared(".clara-button")
        assert bodies, "the button's label colour is not restated"
        assert all("var(--derico-on-copper)" in body for body in bodies)

    def test_the_restatement_outranks_claras_own_anchor_rule(self):
        """Two classes beat one class plus one pseudo-class only because the
        band's own class is in the selector — `.clara-button` alone would not."""
        selectors = [
            css_tools.normalise_selector(selector)
            for selector, _ in css_tools.rules(self.SHEET)
            if ".clara-button" in selector or ".clara-text-link" in selector
        ]
        assert selectors
        for selector in selectors:
            for part in selector.split(","):
                assert part.strip().startswith(".element-contact-band ")

    def test_the_quiet_link_is_ink_and_hovers_into_copper(self):
        bodies = "\n".join(self._declared(".clara-text-link"))
        assert "var(--derico-ink)" in bodies
        assert "var(--derico-copper-text)" in bodies
