"""The Derico Snippet's public renderer.

The block's whole contract is small enough to state in one sentence — the
stored key's fragment, injected verbatim, Balkenlage when in doubt — but it is
stated three times: by ``browser/snippet.py``, by ``bundle-src/src/snippet/``,
and by the ``snippets/*.html`` corpus both of them read. The editor side pins
its copy in ``snippets.test.tsx``; this is the server's, plus the lockstep
guards that hold the three statements together — the corpus on disk, the
Python whitelist derived from it, and the choice vocabulary the sidebar
offers.

Nothing here asserts how a snippet looks: the fragments are the design
mockup's own markup, and `static/snippets.css` restates the mockup's rules.
"""

import re
from pathlib import Path

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from plonetheme.derico.browser.snippet import DEFAULT_SNIPPET
from plonetheme.derico.browser.snippet import snippet_markup
from plonetheme.derico.browser.snippet import SNIPPET_NAMES
from plonetheme.derico.browser.snippet import SNIPPETS_DIR
from plonetheme.derico.interfaces import IPlonethemeDericoLayer


BLOCK_TYPE = "derico-snippet"
VIEW_NAME = f"aurora-block-{BLOCK_TYPE}"

BUNDLE_SRC = Path(__file__).resolve().parent.parent / "bundle-src" / "src" / "snippet"


class SnippetTestCase:
    """A snippet rendered on a real content object, on the theme's layer."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.doc = api.content.create(
            container=self.portal, type="Document", id="page", title="A page"
        )
        alsoProvides(self.doc, IBlocks)

    def render(self, data):
        view = getMultiAdapter((self.doc, self.request), name=VIEW_NAME)
        view.block_type = BLOCK_TYPE
        view.data = data
        return view()

    def page(self, node):
        """The whole published page, through Blicca's dispatcher."""
        self.doc.blocks = {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [dict(node, type="ploneBlock", children=[{"text": ""}])],
            }
        }
        self.doc.blocks_layout = {"items": [SOMERSAULT_BLOCK_ID]}
        view = getMultiAdapter((self.doc, self.request), name="aurora-blocks-view")
        return view.render()


class TestRendering(SnippetTestCase):
    def test_a_stored_key_renders_its_fragment_verbatim(self):
        """Injection, not templating: the file IS the markup, byte for byte.

        This is the property that lets the editor bundle import the same file
        ``?raw`` and claim the two surfaces cannot drift.
        """
        for name in SNIPPET_NAMES:
            assert snippet_markup(name) in self.render({"snippet": name})

    def test_the_fragment_lands_inside_the_parity_wrapper(self):
        """`.derico-snippet` exists for the editor half's injection host."""
        rendered = self.render({"snippet": "balkenlage"})
        assert '<div class="derico-snippet">' in rendered

    @pytest.mark.parametrize(
        "data",
        [
            pytest.param({}, id="a fresh unseeded node"),
            pytest.param({"snippet": "zapfen"}, id="an unknown key via the API"),
            pytest.param({"snippet": None}, id="a null written via the API"),
        ],
    )
    def test_anything_else_falls_back_to_the_balkenlage(self, data):
        """The schema default, restated at render time.

        The block stays authorable through the API, so the stored value is
        untrusted; it is only ever a lookup key, and a divider is the least
        surprising thing a divider block can render.
        """
        assert snippet_markup(DEFAULT_SNIPPET) in self.render(data)

    def test_the_dispatcher_finds_the_renderer(self):
        """End to end through `aurora-blocks-view`, not just the adapter."""
        page = self.page({"@type": BLOCK_TYPE, "snippet": "service-frame"})
        assert 'class="derico-staenderwerk"' in page


class TestTheCorpus:
    """The three statements of the snippet vocabulary, held in lockstep.

    Adding a snippet is one file plus one entry in two TypeScript modules;
    each of these tests names the edit its failure asks for. Parsed as text
    on the TS side — same trade `test_block_addon_lockstep.py` makes.
    """

    def test_the_whitelist_is_the_directory(self):
        files = {path.stem for path in SNIPPETS_DIR.glob("*.html")}
        assert files == SNIPPET_NAMES
        assert DEFAULT_SNIPPET in SNIPPET_NAMES

    def test_the_sidebar_offers_exactly_the_corpus(self):
        schema = BUNDLE_SRC.joinpath("schema.ts").read_text()
        choices = set(re.findall(r"^\s*\['([a-z-]+)',", schema, re.MULTILINE))
        assert choices == SNIPPET_NAMES, (
            "bundle-src/src/snippet/schema.ts SNIPPET_CHOICES does not match "
            "the snippets/ directory"
        )

    def test_the_editor_bundle_imports_exactly_the_corpus(self):
        module = BUNDLE_SRC.joinpath("snippets.ts").read_text()
        imported = set(re.findall(r"snippets/([a-z-]+)\.html\?raw", module))
        assert imported == SNIPPET_NAMES, (
            "bundle-src/src/snippet/snippets.ts does not import the same "
            "files browser/snippet.py serves"
        )

    def test_every_fragment_is_decorative(self):
        """The snippets are ornament; a fragment a screen reader announces
        is a fragment that has lost its `aria-hidden` in an edit."""
        for name in SNIPPET_NAMES:
            assert 'aria-hidden="true"' in snippet_markup(name).split("\n")[0], name

    def test_no_fragment_carries_an_animation_hook(self):
        """`data-balkenlage` / `data-service-frame` are site.js's arming
        hooks in the mockup; no snippet JS ships here, and the design defines
        the JS-less state as the finished one."""
        for name in SNIPPET_NAMES:
            assert not re.search(
                r"data-(balkenlage|service-frame)", snippet_markup(name)
            ), name
