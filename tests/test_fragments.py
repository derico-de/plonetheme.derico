"""derico as a fragment provider for ``collective.fragmentsblock``.

The corpus under ``snippets/`` has two readers: the ``IFragmentsProvider``
utility in ``fragments.py``, which serves classic rendering, and the
``fragments`` bundle, which publishes the same files into ``@plone/registry``
for the editor. Since profile 1004 they are the only readers — the Derico
Snippet brand block that used to render them was retired in favour of
``collective.fragmentsblock``'s generic fragment block.

What is worth testing is exactly the seam: that the utility is registered
and resolves the shipped corpus, that the ids the editor half publishes are
the ids the server can resolve (a mismatch renders on the canvas and
vanishes when published), and that a page carrying a ``fragment`` block
comes out with the ornament's own markup. How a fragment looks is the
mockup's business: it is the design's own markup, restated by
``static/snippets.css``.
"""

import re
from pathlib import Path

import pytest
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

from plonetheme.derico.fragments import FRAGMENTS_DIR
from plonetheme.derico.interfaces import IPlonethemeDericoLayer
from plonetheme.derico.testing import INTEGRATION_TESTING


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
EDITOR_ENTRY = PACKAGE / "bundle-src" / "src" / "fragments" / "index.tsx"

PROVIDER_NAME = "plonetheme.derico"

#: `{ id: 'balkenlage', title: '…', html: balkenlage },`
_RECORD_RE = re.compile(r"\{\s*id:\s*'([^']+)',\s*title:\s*'((?:[^'\\]|\\.)*)'")


def editor_records():
    """The (id, title) pairs the editor bundle publishes.

    Read out of the source rather than imported: the seam under test is
    that two languages agree about one corpus, and a Node round-trip in a
    Python suite would only move the question.
    """
    source = EDITOR_ENTRY.read_text(encoding="utf-8")
    return [
        (fragment_id, title.replace("\\'", "'"))
        for fragment_id, title in _RECORD_RE.findall(source)
    ]


class TestProviderRegistration:
    """The utility half, no site needed."""

    layer = INTEGRATION_TESTING

    def test_provider_is_registered_under_the_package_name(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        assert provider is not None

    def test_provider_serves_the_shipped_corpus(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        for path in FRAGMENTS_DIR.glob("*.html"):
            assert provider.get(path.stem) == path.read_text(encoding="utf-8")

    def test_unknown_fragment_is_none(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        assert provider.get("no-such-fragment") is None

    def test_the_corpus_is_the_shipped_directory(self):
        # the ornaments keep their historical home; only the block changed
        assert FRAGMENTS_DIR == PACKAGE / "src" / "plonetheme" / "derico" / "snippets"
        assert sorted(p.name for p in FRAGMENTS_DIR.glob("*.html"))


class TestCorpusLockstep:
    """The editor bundle's map against the files the server resolves."""

    layer = INTEGRATION_TESTING

    def test_editor_publishes_every_shipped_fragment(self):
        assert sorted(id_ for id_, _ in editor_records()) == sorted(
            path.stem for path in FRAGMENTS_DIR.glob("*.html")
        )

    def test_editor_ids_are_resolvable_by_the_server(self):
        provider = getUtility(IFragmentsProvider, name=PROVIDER_NAME)
        for fragment_id, _title in editor_records():
            assert provider.get(fragment_id) is not None, fragment_id

    def test_editor_titles_are_not_empty(self):
        for fragment_id, title in editor_records():
            assert title.strip(), fragment_id


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
        self.page.blocks = {
            SOMERSAULT_BLOCK_ID: {"@type": SOMERSAULT_BLOCK_TYPE, "value": value}
        }
        self.page.blocks_layout = {"items": [SOMERSAULT_BLOCK_ID]}
        view = getMultiAdapter((self.page, self.request), name="aurora-blocks-view")
        return view.render()

    def test_fragment_block_renders_the_ornament(self):
        html = self._render(
            [
                {
                    "type": "ploneBlock",
                    "@type": "fragment",
                    "children": [{"text": ""}],
                    "fragment": "balkenlage",
                }
            ]
        )
        source = (FRAGMENTS_DIR / "balkenlage.html").read_text(encoding="utf-8")
        # the ornament's own root class, injected verbatim
        assert 'class="block-fragment"' in html
        assert source.strip() in html

    def test_unknown_fragment_leaves_no_visible_trace(self):
        html = self._render(
            [
                {
                    "type": "ploneBlock",
                    "@type": "fragment",
                    "children": [{"text": ""}],
                    "fragment": "no-such-fragment",
                }
            ]
        )
        assert "block-fragment-unresolved" in html
