"""The footer band: the design's `.site-footer` on the footer-blocks element.

`collective.blicca.footerblocks` renders the authored footer blocks inside
`<footer class="element-footerblocks">` at the tail of every page, and the
theme dresses that element the way the Jahresringe mockup dresses its
`.site-footer` (footer-blocks ticket 07). Two things ship it — the footer
bundle (registry.xml: footer.css) and the sheet itself — and each is checked
from the side that would fail silently without it: the record the page
reads, the resource it points at, and the handful of design values the sheet
exists to state.

Looks are not asserted here. The stylesheet's contract with Clara — that it
names no `--clara-*` token and reads only tokens derico.css declares — is
test_override_minimality.py's, which globs every sheet under static/.
"""

import re

import pytest
from plone import api

from . import clara_css as css_tools


BUNDLE = "plone.bundles/plonetheme-derico-footer"

FOOTER_CSS = css_tools.STATIC / "footer.css"

ROOT = ".element-footerblocks"

#: A paragraph or list block on the footer's flat ground — neither banded
#: itself nor inside a banded block. The design measures its footer type on
#: the page ground alone, and a band keeps its own foreground (a dark slot
#: hands its subtree `--aurora-block-fg-dark`; ink-soft on petrol would fail
#: AA).
FLAT_TEXT = (
    ".element-footerblocks :is(.block-p, .block-ul)"
    ':not([class*="has--backgroundColor--"])'
    ':not([class*="has--backgroundColor--"] *)'
)


def _style_rules():
    return css_tools.style_rules(FOOTER_CSS.read_text())


def _values_for(selector, property_name):
    return css_tools.values_for(FOOTER_CSS.read_text(), selector, property_name)


class TestFooterBundle:
    """One record, one file, served."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_bundle_registered_and_enabled(self):
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/footer.css"
        )

    def test_bundle_loads_after_the_token_layer(self):
        """Every value the sheet paints with is a token derico.css declares."""
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-derico"

    def test_static_resource_is_traversable(self):
        """A record pointing at a missing file is a 404 on every page."""
        resource = self.portal.restrictedTraverse("++resource++plonetheme.derico/footer.css")
        assert resource is not None

    def test_uninstall_profile_removes_the_record(self):
        """The mirror of the default profile, so uninstall leaves no orphan
        bundle requesting a stylesheet the site no longer ships."""
        uninstall = css_tools.PACKAGE / "src/plonetheme/derico/profiles/uninstall/registry.xml"
        text = uninstall.read_text()
        assert re.search(rf'prefix="{re.escape(BUNDLE)}"\s+remove="true"', text), (
            "profiles/uninstall/registry.xml does not remove the footer bundle"
        )

    def test_upgrade_profile_carries_the_same_record(self):
        """1012 adds the record to an existing site; it must be the record
        the default profile installs, byte for byte in every value."""
        default = (
            css_tools.PACKAGE / "src/plonetheme/derico/profiles/default/registry.xml"
        ).read_text()
        upgrade = (
            css_tools.PACKAGE / "src/plonetheme/derico/upgrades/1012/registry.xml"
        ).read_text()
        assert css_tools.bundle_record(default, BUNDLE) == css_tools.bundle_record(upgrade, BUNDLE)


class TestFooterSheet:
    """The design values the sheet exists to state, pinned on the file."""

    def test_every_rule_is_keyed_on_the_footer_element(self):
        """The sheet loads on every page and reaches nothing outside the
        footer: a footer rule that leaked to the body's paragraphs would
        shrink an article's running text to the label step."""
        astray = sorted(part for part, _ in _style_rules() if not part.startswith(ROOT + " "))
        assert not astray, f"rules not scoped to {ROOT}: {astray}"

    def test_flat_ground_text_takes_the_designs_footer_type(self):
        """The mockup's `.site-footer p` and `.footer-links`: ink-soft, at
        the label step — on the block wrapper, which Blicca never colours or
        sizes, so the bare `<p>` and `<li>` inherit it."""
        assert _values_for(FLAT_TEXT, "font-size") == ["var(--derico-text-label)"]
        assert _values_for(FLAT_TEXT, "color") == ["var(--derico-ink-soft)"]

    def test_flat_ground_links_are_ink_soft_and_hover_copper(self):
        """The mockup's `.footer-links a`, and the design's one link hover
        (`a:hover { color: var(--copper-text) }`) restated because an
        unlayered colour on the link would otherwise shadow Clara's layered
        hover — the same pairing Clara's own footer rows carry."""
        assert _values_for(FLAT_TEXT + " a", "color") == ["var(--derico-ink-soft)"]
        assert _values_for(FLAT_TEXT + " a:hover", "color") == ["var(--derico-copper-text)"]

    def test_a_list_is_the_designs_link_row(self):
        """The mockup's `.footer-links`: no bullets, a wrapping row, `xs`
        between rows and `m` between items. `.aurora-blocks-view` is in the
        selector on purpose — Blicca's own `.block-ul ul { display: block }`
        is unlayered and loads later, so a tie would go to Blicca."""
        selector = ROOT + " .aurora-blocks-view .block-ul ul"
        assert _values_for(selector, "display") == ["flex"]
        assert _values_for(selector, "flex-wrap") == ["wrap"]
        assert _values_for(selector, "gap") == ["var(--plone-space-xs) var(--plone-space-m)"]
        assert _values_for(selector, "list-style") == ["none"]
        assert _values_for(selector, "padding") == ["0"]
        # Item rhythm is the row's gap: Blicca's per-item padding is zeroed
        # through its token, on the wrapper the `<li>` inherits it from.
        assert _values_for(ROOT + " .block-ul", "--aurora-space-list") == ["0px"]

    def test_every_footer_link_is_a_touch_target(self):
        """PRODUCT.md's 44px floor, as the mockup draws it: `min-height:
        2.75rem` on an inline-flex link. On every footer link, banded or
        not — a target's size does not depend on its ground."""
        selector = ROOT + " :is(.block-p, .block-ul) a"
        assert _values_for(selector, "min-height") == ["2.75rem"]
        assert _values_for(selector, "display") == ["inline-flex"]
        assert _values_for(selector, "align-items") == ["center"]

    def test_no_rule_touches_the_authored_column_widths(self):
        """The mockup's `.footer-grid` (`1fr auto`) is NOT translated onto
        Blicca's column group: the author sets the columns' widths in the
        editor, and a theme that silently re-laid them on the page would make
        the canvas lie. The design's split is authored as a wide/narrow pair."""
        sizing = {"inline-size", "width", "flex", "flex-basis", "grid-template-columns"}
        offenders = sorted(
            part
            for part, properties in _style_rules()
            if ".column" in part and sizing & set(properties)
        )
        assert not offenders, f"rules re-laying the columns: {offenders}"
