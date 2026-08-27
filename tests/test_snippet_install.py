"""Installing the Derico Snippet: the record, the stylesheet bundle, the gate.

Same failure landscape as the hero's packaging (see test_hero_install.py):
almost everything here fails as a silent slash-menu absence, so the
assertions are mostly Blicca's own verdicts via ``evaluate()`` rather than
raw record values. What is different is the delivery of the styling — a theme
bundle instead of a block-record ``css`` — so that bundle gets the checks the
``css`` field would otherwise have received.
"""

from pathlib import Path

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import blockaddons
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.snippet"
BLOCK_TYPE = "derico-snippet"
PERMISSION = "plonetheme.derico: Insert Brand Block"
STATIC_BASE = "++plone++plonetheme.derico.blocks"

CSS_BUNDLE = "plone.bundles/plonetheme-derico-snippets"
STATIC_DIR = (
    Path(__file__).resolve().parent.parent
    / "src" / "plonetheme" / "derico" / "static"
)


def record(name, default=None):
    return api.portal.get_registry_record(f"{RECORD}.{name}", default=default)


def bundle(name, default=None):
    return api.portal.get_registry_record(f"{CSS_BUNDLE}.{name}", default=default)


class InstallTestCase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def status(self):
        """The snippet's record, as Blicca's own discovery sees it."""
        found = [
            status
            for status in blockaddons.evaluate(self.portal)
            if status.name == "plonetheme.derico.snippet"
        ]
        assert found, "the snippet's record is not discovered as a block add-on"
        return found[0]


class TestTheBlockRecord(InstallTestCase):
    def test_the_record_is_loadable(self):
        """Every filter gate passed: enabled, resolvable, compatible."""
        status = self.status()
        assert status.loadable, f"the snippet would be skipped: {status.skip_reason}"

    def test_the_bundle_url_resolves(self):
        assert self.status().bundle_url

    def test_the_bundle_is_served_from_the_block_directory(self):
        assert record("bundle") == f"{STATIC_BASE}/snippet.js"

    def test_the_record_declares_no_stylesheet(self):
        """The one deliberate difference from the hero's record.

        The snippets are pure markup; their styling is the theme's own
        `snippets.css` bundle (checked below), so a `css` value appearing
        here would mean the delivery story has silently changed shape.
        """
        assert not record("css")

    def test_the_record_declares_the_block_type(self):
        assert tuple(record("types")) == (BLOCK_TYPE,)

    def test_the_record_declares_the_block_api_floor(self):
        assert record("block_api") == "1.0"

    def test_the_record_is_enabled(self):
        assert record("enabled") is True

    def test_there_is_no_server_renderer_gap(self):
        """Contract §5.5, run for real — now over BOTH brand blocks."""
        gaps = blockaddons.lockstep_gaps(
            self.portal, self.request, blockaddons.evaluate(self.portal)
        )
        assert gaps == [], f"registered blocks with no server renderer: {gaps}"


class TestTheStylesheetBundle(InstallTestCase):
    """`plonetheme-derico-snippets`: the styling the record's `css` is not.

    A bundle record has no `evaluate()` to borrow verdicts from, so these
    check the two things that fail silently: the resource actually shipping,
    and the sheet actually carrying the scope wrap that lets it style the
    editing canvas.
    """

    def test_the_bundle_is_registered_and_enabled(self):
        assert bundle("csscompilation") == "++resource++plonetheme.derico/snippets.css"
        assert bundle("enabled") is True

    def test_it_depends_on_the_token_layer(self):
        """Every value it paints with is a `--derico-*` token."""
        assert bundle("depends") == "plonetheme-derico"

    def test_the_sheet_ships(self):
        assert (STATIC_DIR / "snippets.css").is_file()

    def test_the_sheet_is_scope_wrapped(self):
        """Hand-written, so nothing but this test enforces it.

        Unwrapped rules die against Aurora's scoped Tailwind preflight in the
        editing canvas — the failure the block pipeline's scope-wrap plugin
        exists to prevent, prevented here by hand. Same three roots, same
        donut limit (contract §6.1).
        """
        sheet = (STATIC_DIR / "snippets.css").read_text()
        assert (
            "@scope (.aurora-editor, .aurora-editor-portal, .aurora-blocks-view)"
            in sheet
        )
        assert "to (.aurora-pattern-island)" in sheet

    def test_the_sheet_speaks_only_derico_tokens(self):
        """The seam rule the block sheets follow, applied to this one."""
        sheet = (STATIC_DIR / "snippets.css").read_text()
        assert "--clara-" not in sheet


class TestTheInsertGate(InstallTestCase):
    """The same gate as the hero's: one permission for all brand blocks."""

    def test_the_record_names_the_permission(self):
        assert record("permission") == PERMISSION

    def test_a_site_administrator_may_insert_a_snippet(self):
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        login(self.portal, TEST_USER_NAME)
        assert blockaddons.may_insert(self.portal, self.status())

    def test_an_editor_may_not(self):
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        login(self.portal, TEST_USER_NAME)
        assert not blockaddons.may_insert(self.portal, self.status())
