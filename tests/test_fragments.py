"""derico as a fragment provider for ``collective.fragmentsblock``.

The corpus under ``snippets/`` is registered with one ``fragments:folder``
line in ``configure.zcml``. The server renders from the folder, and the
editor fetches the same files through the block's ``@fragments`` service
(collective.fragmentsblock, ADR 0002), so nothing editor-side ships from
this package. What is worth testing is the seam: the utility is registered
under the expected name over the shipped directory, every snippet carries
the title the picker shows, the service lists exactly the corpus, and a
page carrying a ``fragment`` block comes out with the ornament's own
markup. How a fragment looks is the mockup's business: it is the design's
own markup, restated by ``static/snippets.css``.
"""

from pathlib import Path

import pytest
from collective.fragmentsblock.fragments import derived_title
from collective.fragmentsblock.fragments import FragmentsFolder
from collective.fragmentsblock.fragments import records
from collective.fragmentsblock.interfaces import IFragmentsProvider
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.testing import INTEGRATION_TESTING


PACKAGE = Path(__file__).resolve().parent.parent
SNIPPETS_DIR = PACKAGE / "src" / "plonetheme" / "derico" / "snippets"

PROVIDER_NAME = "plonetheme.derico"

#: What the picker shows per snippet: each file's first-line title comment.
TITLES = {
    "balkenlage": "Balkenlage (Trenner)",
    "service-frame": "Ständerwerk (Rahmen)",
}


class TestProviderRegistration:
    layer = INTEGRATION_TESTING

    def test_registered_under_the_package_name_over_the_snippets_folder(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        assert isinstance(provider, FragmentsFolder)
        assert provider.directory == SNIPPETS_DIR

    def test_serves_the_shipped_corpus(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        for path in SNIPPETS_DIR.glob("*.html"):
            assert provider.get(path.stem) == path.read_text(encoding="utf-8")

    def test_unknown_fragment_is_none(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        assert provider.get("no-such-fragment") is None


class TestTheCorpus:
    """Every ornament the directory holds, titled for the picker."""

    layer = INTEGRATION_TESTING

    def test_the_corpus_is_the_shipped_directory(self):
        assert sorted(path.stem for path in SNIPPETS_DIR.glob("*.html")) == sorted(TITLES)

    def test_every_snippet_carries_its_title(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        assert {record["id"]: record["title"] for record in provider.records()} == TITLES

    def test_titles_are_the_design_s_names_not_the_fallback(self):
        # Without its comment line a snippet would show up as a name derived
        # from the file ("Service frame"), not the design's German one.
        for fragment_id, title in TITLES.items():
            assert title != derived_title(fragment_id), fragment_id


class TestWhatTheEditorFetches:
    """``records()``: what the ``@fragments`` service hands the block before its first render."""

    layer = INTEGRATION_TESTING

    def test_lists_the_corpus_with_titles_and_markup(self, integration):
        items = records()
        assert {item["id"]: item["title"] for item in items} == TITLES
        for item in items:
            source = (SNIPPETS_DIR / f"{item['id']}.html").read_text(encoding="utf-8")
            assert item["html"] == source


class TestFragmentBlockRendering:
    """A page carrying a ``fragment`` block, rendered end to end."""

    layer = INTEGRATION_TESTING

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        alsoProvides(self.request, IPlonethemeDericoLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.page = api.content.create(
            container=self.portal, type="Document", id="page", title="A page"
        )

    def _render(self, value):
        alsoProvides(self.page, IBlocks)
        self.page.blocks = {SOMERSAULT_BLOCK_ID: {"@type": SOMERSAULT_BLOCK_TYPE, "value": value}}
        self.page.blocks_layout = {"items": [SOMERSAULT_BLOCK_ID]}
        view = getMultiAdapter((self.page, self.request), name="aurora-blocks-view")
        return view.render()

    def test_fragment_block_renders_the_ornament(self):
        html = self._render([
            {
                "type": "ploneBlock",
                "@type": "fragment",
                "children": [{"text": ""}],
                "fragment": "balkenlage",
            }
        ])
        source = (SNIPPETS_DIR / "balkenlage.html").read_text(encoding="utf-8")
        # the ornament's own root class, injected verbatim
        assert 'class="block-fragment"' in html
        assert source.strip() in html

    def test_unknown_fragment_leaves_no_visible_trace(self):
        html = self._render([
            {
                "type": "ploneBlock",
                "@type": "fragment",
                "children": [{"text": ""}],
                "fragment": "no-such-fragment",
            }
        ])
        assert "block-fragment-unresolved" in html
