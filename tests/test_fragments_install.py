"""Nothing of derico's loads into the editor for the snippets any more.

Up to profile 1018 a block add-on record loaded ``fragments.js`` — one
``?raw`` import per snippet — into the editor, because a record is the only
way a bundle loads at all. Since ``collective.fragmentsblock`` lists every
provider's fragments itself (``@fragments``, its ADR 0002) the record, the
bundle and the rebuild they implied are gone (upgrade step 1019). What
stays is the stylesheet bundle that styles the ornaments on both surfaces.
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


#: Retired in profile 1019; collective.fragmentsblock fetches the corpus.
RETIRED_FRAGMENTS_RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.fragments"
#: Retired in profile 1004; the fragment block renders the ornaments now.
RETIRED_SNIPPET_RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.snippet"

CSS_BUNDLE = "plone.bundles/plonetheme-derico-snippets"
PACKAGE_DIR = Path(__file__).resolve().parent.parent / "src" / "plonetheme" / "derico"
STATIC_DIR = PACKAGE_DIR / "static"
BLOCKS_DIR = PACKAGE_DIR / "static-blocks"


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


class TestTheRetiredRecords(InstallTestCase):
    """Neither bundle derico once loaded for the ornaments exists any more."""

    @pytest.mark.parametrize("record", [RETIRED_FRAGMENTS_RECORD, RETIRED_SNIPPET_RECORD])
    def test_the_profile_registers_no_record(self, record):
        assert api.portal.get_registry_record(f"{record}.bundle", default=None) is None
        assert api.portal.get_registry_record(f"{record}.enabled", default=None) is None

    def test_nothing_of_derico_is_discovered_for_the_ornaments(self):
        names = [status.name for status in blockaddons.evaluate(self.portal)]
        assert "plonetheme.derico.fragments" not in names
        assert "plonetheme.derico.snippet" not in names

    @pytest.mark.parametrize("filename", ["fragments.js", "snippet.js"])
    def test_the_bundle_no_longer_ships(self, filename):
        assert not (BLOCKS_DIR / filename).exists()

    def test_the_uninstall_profile_names_no_fragments_record(self):
        uninstall = (PACKAGE_DIR / "profiles" / "uninstall" / "registry.xml").read_text()
        assert "plonetheme.derico.fragments" not in uninstall


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
        assert "@scope (.aurora-editor, .aurora-editor-portal, .aurora-blocks-view)" in sheet
        assert "to (.aurora-pattern-island)" in sheet

    def test_the_sheet_speaks_only_derico_tokens(self):
        """The seam rule the block sheets follow, applied to this one."""
        sheet = (STATIC_DIR / "snippets.css").read_text()
        assert "--clara-" not in sheet
