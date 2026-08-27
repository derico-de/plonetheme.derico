"""Installing the fragment provider: the record that loads its bundle.

The provider's own registration is a global utility (``test_fragments.py``);
what the profile adds is the record that makes ``@@aurora-edit`` load the
bundle publishing that corpus into the editor's registry. The record is
unusual in one way worth pinning: it declares NO ``types``, because it
registers no block. Nothing in Blicca's discovery gates on ``types``, and
the assertions below are that verdict rather than raw values — a record
that silently stops being loadable costs the picker its entries with no
error anywhere.
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
from plonetheme.derico.testing import INTEGRATION_TESTING


RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.fragments"
ADDON_NAME = "plonetheme.derico.fragments"
STATIC_BASE = "++plone++plonetheme.derico.blocks"

CSS_BUNDLE = "plone.bundles/plonetheme-derico-snippets"
STATIC_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "plonetheme" / "derico" / "static"
)

#: Retired in profile 1004; the fragment block renders the ornaments now.
RETIRED_RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.snippet"


def record(name, default=None):
    return api.portal.get_registry_record(f"{RECORD}.{name}", default=default)


def bundle(name, default=None):
    return api.portal.get_registry_record(f"{CSS_BUNDLE}.{name}", default=default)


class InstallTestCase:
    """Shared fixture; not a test class of its own."""

    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def status(self):
        found = [
            status
            for status in blockaddons.evaluate(self.portal)
            if status.name == ADDON_NAME
        ]
        assert found, "the fragments record is not discovered as a block add-on"
        return found[0]


class TestTheFragmentsRecord(InstallTestCase):
    def test_the_record_is_loadable(self):
        """Every filter gate passed: enabled, resolvable, compatible."""
        status = self.status()
        assert status.loadable, f"the bundle would be skipped: {status.skip_reason}"

    def test_the_bundle_url_resolves(self):
        assert self.status().bundle_url

    def test_the_bundle_is_served_from_the_block_directory(self):
        assert record("bundle") == f"{STATIC_BASE}/fragments.js"

    def test_the_record_declares_no_block_types(self):
        """The record's whole point: a bundle, no block.

        An @type appearing here would claim a server renderer this package
        does not ship — the fragment block's renderer belongs to
        collective.fragmentsblock — and would be reported as a lockstep gap.
        """
        assert list(record("types") or []) == []

    def test_the_record_declares_no_stylesheet(self):
        # the ornaments are styled by the theme's own snippets.css bundle
        assert not record("css")

    def test_the_record_declares_the_block_api_floor(self):
        assert record("block_api") == "1.0"

    def test_the_record_is_enabled(self):
        assert record("enabled") is True

    def test_the_record_gates_nothing(self):
        """No `permission`, deliberately.

        Withholding this record would not withhold anything insertable; it
        would only empty the picker for the user allowed to insert the
        block. Insert-gating for fragments belongs to the fragment block's
        own record, in collective.fragmentsblock.
        """
        assert not record("permission")
        assert ADDON_NAME not in blockaddons.restricted_block_types(self.portal)

    def test_it_introduces_no_server_renderer_gap(self):
        """Contract §5.5: a typeless record cannot open one."""
        gaps = blockaddons.lockstep_gaps(
            self.portal, self.request, blockaddons.evaluate(self.portal)
        )
        assert [gap for gap in gaps if gap["addon"] == ADDON_NAME] == []


class TestTheRetiredSnippetRecord(InstallTestCase):
    """Profile 1004 removed the Derico Snippet block."""

    def test_the_record_is_gone(self):
        assert (
            api.portal.get_registry_record(f"{RETIRED_RECORD}.bundle", default=None)
            is None
        )

    def test_it_is_not_discovered_as_a_block_addon(self):
        names = [status.name for status in blockaddons.evaluate(self.portal)]
        assert "plonetheme.derico.snippet" not in names

    def test_its_bundle_no_longer_ships(self):
        blocks_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "plonetheme"
            / "derico"
            / "static-blocks"
        )
        assert not (blocks_dir / "snippet.js").exists()


class TestTheStylesheetBundle(InstallTestCase):
    """`plonetheme-derico-snippets`: the ornaments' styling, still shipped.

    It outlived the block it was written for — the markup it styles is the
    same, only the block injecting it changed — so it keeps the two checks
    that fail silently: the resource actually shipping, and the sheet
    actually carrying the scope wrap that lets it style the editing canvas.
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
