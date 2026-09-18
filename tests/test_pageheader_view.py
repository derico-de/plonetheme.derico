"""The Derico Page Header's public renderer.

Two implementations render this block: `bundle-src/src/pageheader/` draws the
editing canvas, `browser/pageheader.py` the published page. They share one
scope-wrapped stylesheet, so the classes each emits are a contract; the
editor's copy is `render.test.tsx`, this is the server's.

The block stores the kicker and nothing else. The title and the description
are the page's own fields — bound on the canvas through the host's form atom,
read from the context here — so what is asserted about them is that they
come from the CONTEXT, never from the block's data.
"""

import pytest
from bs4 import BeautifulSoup
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

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


BLOCK_TYPE = "derico-page-header"
VIEW_NAME = f"aurora-block-{BLOCK_TYPE}"


class PageHeaderTestCase:
    """A page header rendered on a real content object, on the theme's layer."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.doc = api.content.create(
            container=self.portal,
            type="Document",
            id="page",
            title="Nachhaltige Softwareentwicklung",
            description="Offene Software schützt Investitionen.",
        )
        alsoProvides(self.doc, IBlocks)

    def render(self, data):
        view = getMultiAdapter((self.doc, self.request), name=VIEW_NAME)
        view.block_type = BLOCK_TYPE
        view.data = data
        return view()

    def soup(self, data):
        return BeautifulSoup(self.render(data), "html.parser")

    def header(self, data):
        """The block's own root element."""
        return self.soup(data).find("section", class_="derico-page-header")

    def page(self, node, *before):
        """The whole published page, through Blicca's dispatcher; ``before``
        are tree nodes standing above the header."""
        self.doc.blocks = {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [
                    *before,
                    dict(node, type="ploneBlock", children=[{"text": ""}]),
                ],
            }
        }
        self.doc.blocks_layout = {"items": [SOMERSAULT_BLOCK_ID]}
        view = getMultiAdapter((self.doc, self.request), name="aurora-blocks-view")
        return BeautifulSoup(view.render(), "html.parser")


class TestTheWords(PageHeaderTestCase):
    def test_the_title_is_the_contexts(self):
        assert self.header({}).h1.get_text() == "Nachhaltige Softwareentwicklung"

    def test_the_description_is_the_contexts(self):
        lede = self.header({}).find("p", class_="lede")
        assert lede.get_text() == "Offene Software schützt Investitionen."

    def test_the_kicker_is_the_blocks(self):
        kicker = self.header({"kicker": "Nachhaltigkeit"}).find("p", class_="page-context")
        assert kicker.get_text() == "Nachhaltigkeit"

    def test_the_block_cannot_override_the_page_fields(self):
        """`title` / `description` in the data are not read: the field is the truth."""
        header = self.header({"title": "Not this", "description": "Nor this"})
        assert header.h1.get_text() == "Nachhaltige Softwareentwicklung"
        assert header.find("p", class_="lede").get_text() == (
            "Offene Software schützt Investitionen."
        )

    def test_a_header_of_None_renders(self):
        """`self.data` is `None` until the dispatcher stamps it."""
        assert self.header(None).h1 is not None


class TestDegradation(PageHeaderTestCase):
    """An empty slot is omitted, never an empty element (as `PageHeader.tsx`)."""

    def test_no_kicker_no_kicker_element(self):
        assert self.header({}).find(class_="page-context") is None

    def test_a_blank_kicker_counts_as_absent(self):
        assert self.header({"kicker": "   "}).find(class_="page-context") is None

    def test_a_non_string_kicker_is_not_rendered(self):
        assert self.header({"kicker": 42}).find(class_="page-context") is None

    def test_the_kicker_is_trimmed(self):
        kicker = self.header({"kicker": "  Leistungen  "}).find(class_="page-context")
        assert kicker.get_text() == "Leistungen"

    def test_no_description_no_lede(self):
        self.doc.description = ""
        header = self.header({})
        assert header.find(class_="lede") is None
        assert header.h1 is not None

    def test_no_title_no_h1(self):
        self.doc.title = ""
        assert self.header({}).find("h1") is None

    def test_an_empty_page_still_renders_its_root(self):
        self.doc.title = ""
        self.doc.description = ""
        assert self.header({}) is not None


class TestMarkupParity(PageHeaderTestCase):
    """The template and the TSX emit one tree, or the shared sheet lies."""

    FULL = {"kicker": "Nachhaltigkeit"}

    #: Every class `PageHeader.tsx` emits.
    CLASSES = [
        "derico-page-header",
        "page-header__grid",
        "page-context",
        "documentFirstHeading",
        "documentDescription",
        "lede",
    ]

    @pytest.mark.parametrize("name", CLASSES)
    def test_every_class_the_editor_emits_is_emitted_here(self, name):
        assert self.soup(self.FULL).find(class_=name) is not None

    def test_the_tree_is_the_mockups(self):
        """Kicker and title share the left cell; the lede is the grid's second child."""
        grid = self.header(self.FULL).find(class_="page-header__grid")
        cells = grid.find_all(recursive=False)
        assert [cell.name for cell in cells] == ["div", "p"]
        assert [child.name for child in cells[0].find_all(recursive=False)] == ["p", "h1"]
        assert "lede" in cells[1]["class"]

    def test_the_root_is_not_auroras_wrapper_stamp(self):
        assert self.soup(self.FULL).find(class_="block-derico-page-header") is None

    def test_nothing_stamps_a_language(self):
        assert not self.soup(self.FULL).find(attrs={"lang": True})

    def test_the_view_emits_no_breakout_of_its_own(self):
        """The wrapper carries the width, from the rung the editor materialises."""
        header = self.header(self.FULL)
        assert "block-width" not in self.render(self.FULL)
        assert header.get("style") is None
        assert not header.find(attrs={"style": True})


class TestOnThePage(PageHeaderTestCase):
    """Through Blicca's dispatcher, on a tree that has no title node."""

    def test_the_page_prints_exactly_one_h1(self):
        soup = self.page({"@type": BLOCK_TYPE, "kicker": "Nachhaltigkeit"})
        headings = soup.find_all("h1")
        assert [h.get_text() for h in headings] == ["Nachhaltige Softwareentwicklung"]

    def test_the_block_is_the_document_header(self):
        """A tree that still holds the title and description nodes — authored
        before the block existed, or through the API — prints the opening
        once, through the header (Blicca's contract §1.8)."""
        soup = self.page(
            {"@type": BLOCK_TYPE, "kicker": "Nachhaltigkeit"},
            {"type": "title", "children": [{"text": "Nachhaltige Softwareentwicklung"}]},
            {"type": "description", "children": [{"text": "Offene Software."}]},
        )
        assert [h.get_text() for h in soup.find_all("h1")] == [
            "Nachhaltige Softwareentwicklung"
        ]
        assert soup.find(class_="documentFirstHeading").find_parent(
            class_="derico-page-header"
        )
        assert len(soup.find_all(class_="documentDescription")) == 1
        assert soup.find(class_="documentDescription").find_parent(
            class_="derico-page-header"
        )

    def test_the_wrapper_carries_the_stamp_the_sheet_leaves_free(self):
        soup = self.page({"@type": BLOCK_TYPE, "blockWidth": "layout"})
        wrapper = soup.find(class_="block-derico-page-header")
        assert wrapper is not None
        assert "has--block-width--layout" in wrapper["class"]
        assert wrapper.find(class_="derico-page-header") is not None
