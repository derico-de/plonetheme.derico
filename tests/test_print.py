"""The print sheet: the design's `@media print` block on the site.

The Jahresringe mockup ships one whole-page print block
(docs/design/derico.de/site/assets/site.css, "@media print"): the chrome and
the calls to action go, the page prints ink on ground, a section's frame
closes up, links print underlined in the running ink with their address
beside them. `static/print.css` is that block said in the site's own
markup. Two things ship it — the print bundle (registry.xml: print.css) and
the sheet itself — and each is checked from the side that would fail
silently without it: the record the page reads, the resource it points at,
and the design values the sheet exists to state.

Looks are not asserted here. The stylesheet's contract with Clara — that it
names no `--clara-*` token and reads only tokens derico.css declares — is
test_override_minimality.py's, which globs every sheet under static/.
"""

import re

import pytest
from plone import api

from . import clara_css as css_tools


BUNDLE = "plone.bundles/plonetheme-derico-print"

PRINT_CSS = css_tools.STATIC / "print.css"

#: What Clara's own print block removes (clara.min.css, `@media print`) and
#: nothing in this theme puts back. A rule here that restated one of these
#: would be noise — the theme's standing rule is that a rule earns its place
#: only when nothing else can reach the thing it styles.
HIDDEN_BY_CLARA = {
    ".element-anontools",
    ".element-language",
    ".element-subnav",
    ".element-siteactions",
}

#: Clara's print block names these two as well, but header.css re-displays
#: them: it is unlayered and gives both `display: contents` below 64rem, and
#: unlayered beats Clara's layered `none`. A sheet of paper is narrower than
#: 64rem, so the print sheet has to take them itself.
RE_DISPLAYED_BY_THE_HEADER = (
    ".plone-layout .element-globalnav",
    ".plone-layout .element-searchbox",
)

#: A banded block on the public view — the design's `.section`, whose frame
#: the mockup closes up on paper.
SECTION = '.aurora-blocks-view .block[class*="has--backgroundColor--"]'


def _sheet():
    return css_tools.strip_comments(PRINT_CSS.read_text())


def _style_rules():
    return list(css_tools.style_rules(PRINT_CSS.read_text()))


def _values_for(selector, property_name):
    return css_tools.values_for(PRINT_CSS.read_text(), selector, property_name)


class TestPrintBundle:
    """One record, one file, served."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_bundle_registered_and_enabled(self):
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/print.css"
        )

    def test_bundle_loads_after_the_token_layer(self):
        """Every value the sheet paints with is a token derico.css declares."""
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-derico"

    def test_static_resource_is_traversable(self):
        """A record pointing at a missing file is a 404 on every page."""
        resource = self.portal.restrictedTraverse("++resource++plonetheme.derico/print.css")
        assert resource is not None

    def test_uninstall_profile_removes_the_record(self):
        """The mirror of the default profile, so uninstall leaves no orphan
        bundle requesting a stylesheet the site no longer ships."""
        uninstall = css_tools.PACKAGE / "src/plonetheme/derico/profiles/uninstall/registry.xml"
        text = uninstall.read_text()
        assert re.search(rf'prefix="{re.escape(BUNDLE)}"\s+remove="true"', text), (
            "profiles/uninstall/registry.xml does not remove the print bundle"
        )

    def test_upgrade_profile_carries_the_same_record(self):
        """1013 adds the record to an existing site; it must be the record
        the default profile installs, byte for byte in every value."""
        default = (
            css_tools.PACKAGE / "src/plonetheme/derico/profiles/default/registry.xml"
        ).read_text()
        upgrade = (
            css_tools.PACKAGE / "src/plonetheme/derico/upgrades/1013/registry.xml"
        ).read_text()
        assert css_tools.bundle_record(default, BUNDLE) == css_tools.bundle_record(upgrade, BUNDLE)


class TestPrintSheet:
    """The design values the sheet exists to state, pinned on the file."""

    def test_the_whole_sheet_is_one_print_block(self):
        """Nothing here may reach the screen: the sheet loads on every page
        with `media="all"`, so a rule outside `@media print` would hide the
        header for everyone. One at-rule, opened first and closed last."""
        text = _sheet().strip()
        assert re.match(r"@media\s+print\s*\{", text), "the sheet must open with @media print"
        depth = 0
        for position, char in enumerate(text):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                assert depth > 0 or position == len(text) - 1, (
                    "a rule sits outside the @media print block"
                )
        assert depth == 0

    def test_the_chrome_goes(self):
        """The mockup's `.site-header, .breadcrumbs, .site-footer`. Clara's
        own print block already takes the navigation, the search, the login
        link and the language switch (HIDDEN_BY_CLARA); what is left of the
        header is the logo, and the site's footer is the footer-blocks
        element, which also holds the design's `.contact-band` — the closing
        Promo on a band."""
        for element in (
            ".element-logo",
            ".element-breadcrumbs",
            ".element-portalfooter",
            ".element-footerblocks",
        ):
            assert _values_for(element, "display") == ["none"], element

    def test_nothing_clara_already_hides_is_restated(self):
        selectors = {part for part, _ in _style_rules()}
        restated = sorted(
            part for part in selectors if any(hidden in part for hidden in HIDDEN_BY_CLARA)
        )
        assert not restated, f"Clara's print block already hides these: {restated}"

    def test_the_header_elements_the_header_sheet_re_displays_go(self):
        """The menu pill and the magnifier: hidden by Clara in a layer,
        shown again by header.css unlayered below 64rem — which is every
        sheet of paper. One class deeper than header.css's `.element-*`
        rule, so specificity settles it rather than bundle order."""
        for element in RE_DISPLAYED_BY_THE_HEADER:
            assert _values_for(element, "display") == ["none"], element

    def test_the_calls_to_action_go(self):
        """The mockup's `.action-row`: the hero's two buttons and the Promo's
        actions — a button on paper is a promise nobody can keep. Keyed on
        `.aurora-blocks-view` to out-specify the blocks' own scoped rules
        (`.derico-hero .action-row`, `.promo .promo-actions`), which tie
        with a bare pair on specificity."""
        for row in (
            ".aurora-blocks-view .derico-hero .action-row",
            ".aurora-blocks-view .promo .promo-actions",
        ):
            assert _values_for(row, "display") == ["none"], row

    def test_the_page_prints_ink_on_ground(self):
        """The mockup's `body { color: var(--ink); background: var(--ground) }`
        — in the theme's names, which are the same near-black and white in
        either colour scheme."""
        assert _values_for("body", "color") == ["var(--derico-ink)"]
        assert _values_for("body", "background") == ["var(--derico-ground)"]

    def test_the_dark_slot_prints_ink_on_ground_too(self):
        """The one place the site paints light on dark. A browser drops
        backgrounds by default when it prints, which would leave the dark
        slot's white text on white paper; the slot's pair is re-pointed on
        the blocks view — an ancestor of every wrapper that reads them, so
        inheritance settles it, not load order."""
        assert _values_for(".aurora-blocks-view", "--aurora-block-bg-dark") == [
            "var(--derico-ground)"
        ]
        assert _values_for(".aurora-blocks-view", "--aurora-block-fg-dark") == ["var(--derico-ink)"]

    def test_a_section_closes_up_on_paper(self):
        """The mockup's `.section { padding-block: 1.5rem }`. Every block
        frame reads one of Blicca's two tokens — §10's reading frame from
        `:root`, §11's section frame on the banded wrapper — so both are
        re-pointed to the `m` step, the mockup's 1.5rem being that step's
        floor: on the blocks view for the inherited values, and on the
        banded wrapper, one class deeper, to out-specify §11's own rule."""
        for selector in (".aurora-blocks-view", SECTION):
            assert _values_for(selector, "--aurora-space-block") == ["var(--plone-space-m)"]
            assert _values_for(selector, "--aurora-space-bleed") == ["var(--plone-space-m)"]

    def test_the_content_header_closes_up_on_paper(self):
        """The `.page-hero` half of the same rule: an inner page's hero is
        its title and lede, the content header here."""
        assert _values_for(".element-contentheader", "padding-block") == ["var(--plone-space-m)"]

    def test_links_print_in_the_running_ink_underlined(self):
        """The mockup's `a { color: inherit; text-decoration: underline }`:
        cyan is a screen colour, and an underline is the one link marker a
        greyscale print keeps."""
        assert _values_for("a", "color") == ["inherit"]
        assert _values_for("a", "text-decoration") == ["underline"]

    def test_a_link_prints_its_address(self):
        """The mockup's `a[href^="http"]::after`. Plone writes every link
        absolute, so on the site this annotates internal links as well — on
        paper that is the address a reader would need either way."""
        selector = 'a[href^="http"]::after'
        assert _values_for(selector, "content") == ['" (" attr(href) ")"']
        assert _values_for(selector, "font-size") == ["0.85em"]

    def test_no_declaration_is_important(self):
        """Clara owns the cascade; the sheet wins by being unlayered."""
        assert "!important" not in _sheet()
