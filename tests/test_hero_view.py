"""The Derico Hero's public renderer (hero ticket 09).

Two implementations render this block: `bundle-src/src/hero/` draws the
editing canvas, `browser/hero.py` draws the published page. They share one
scope-wrapped stylesheet and one degradation table, and neither owns both — so
the guard against them drifting apart has to exist on both sides. The editor's
copy is `degradation.test.tsx`; this is the server's, written against the same
rules and, where it can be, against the same cases.

What is deliberately NOT asserted here:

- **Anything about how the block looks.** `test_hero_sheet.py` pins the
  stylesheet, and the pixels were settled by measurement in ticket 07.
- **Anything about who may insert a hero.** The gate is guidance, not
  security (ticket 03), and this renderer is explicitly indifferent to it.
- **The block wrapper's full-bleed breakout.** It is Blicca's, stamped by
  `plate.py` from the `blockWidth` the editor materialises onto the node
  (ticket 11). The one thing worth checking here is the negative: that this
  view adds no breakout of its own.
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
from plone.namedfile.file import NamedBlobImage
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


BLOCK_TYPE = "derico-hero"
VIEW_NAME = f"aurora-block-{BLOCK_TYPE}"

#: A valid 1x1 transparent PNG.
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xfc\xff"
    b"\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND"
    b"\xaeB`\x82"
)

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"></svg>'

#: The design's breakpoint, as `HeroMedia.tsx` and `ensure_hero_variants`
#: both spell it. A `<picture>` takes the first source that matches, so this
#: is what makes portrait-before-wide art direction rather than an ordering
#: accident.
PORTRAIT_MEDIA = "(max-width: 55.99rem)"


class HeroTestCase:
    """A hero rendered on a real content object, on the theme's layer."""

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

    # ── fixtures the tests build data out of ──────────────────────────────

    def image(self, item_id, data=PNG, filename="pic.png"):
        """An Image content item, catalogued so `image_scales` exists."""
        item = api.content.create(container=self.portal, type="Image", id=item_id, title=item_id)
        item.image = NamedBlobImage(data=data, filename=filename)
        item.reindexObject()
        return item

    def enriched(self, node):
        """`node`, put through the very transformer loop the page view runs.

        Not a stand-in for it: `serialize_blocks` IS what
        `blocks_view.py` calls before dispatching, so whatever comes back here
        is exactly what the renderer is handed in production.
        """
        from plone.blicca.auroraeditor.browser.rendering.serializer import serialize_blocks

        return serialize_blocks(self.doc, {"0": dict(node, **{"@type": BLOCK_TYPE})})["0"]

    # ── rendering ─────────────────────────────────────────────────────────

    def render(self, data):
        view = getMultiAdapter((self.doc, self.request), name=VIEW_NAME)
        view.block_type = BLOCK_TYPE
        view.data = data
        return view()

    def soup(self, data):
        return BeautifulSoup(self.render(data), "html.parser")

    def hero(self, data):
        """The block's own root element."""
        return self.soup(data).find("section", class_="derico-hero")

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


class TestEmptyHero(HeroTestCase):
    """Nothing in the schema is `required`, so an empty hero has to render.

    A half-authored hero must save and preview — the editor's nag, not a
    validator, is what tells the author what is still missing. Every one of
    these would be an exception if a field's absence were not handled.
    """

    def test_an_empty_hero_still_renders_its_root(self):
        assert self.hero({}) is not None

    def test_an_empty_hero_renders_no_copy(self):
        hero = self.hero({})
        assert hero.find(class_="kicker") is None
        assert hero.find("h1") is None
        assert hero.find(class_="lede") is None

    def test_an_empty_hero_renders_no_action_row(self):
        """Not an empty row: an `.action-row` with nothing in it is a gap."""
        assert self.hero({}).find(class_="action-row") is None

    def test_an_empty_hero_renders_no_photograph_and_no_wash(self):
        hero = self.hero({})
        assert hero.find("picture") is None
        assert hero.find(class_="hero-wash") is None

    def test_an_empty_hero_still_renders_four_numbered_rings(self):
        """The rings are template. They do not wait for content."""
        rows = self.hero({}).select(".ring-legend > div")
        assert [row.b.get_text() for row in rows] == ["1", "2", "3", "4"]
        assert all(row.find("dt") is None for row in rows)
        assert all(row.find("dd") is None for row in rows)

    def test_a_hero_of_None_renders(self):
        """`self.data` is `None` until the dispatcher stamps it."""
        assert self.hero(None) is not None


class TestText(HeroTestCase):
    def test_text_is_trimmed(self):
        assert self.hero({"headline": "  Anwendungen  "}).h1.get_text() == ("Anwendungen")

    def test_whitespace_only_text_counts_as_absent(self):
        assert self.hero({"headline": "   "}).find("h1") is None

    def test_a_non_string_is_not_rendered(self):
        """A value that never went through the widget is not worth throwing over."""
        assert self.hero({"headline": 42}).find("h1") is None

    def test_the_three_copy_fields_keep_their_classes(self):
        hero = self.hero({"kicker": "k", "headline": "h", "lede": "l"})
        assert hero.find("p", class_="kicker").get_text() == "k"
        assert hero.h1.get_text() == "h"
        assert hero.find("p", class_="lede").get_text() == "l"


class TestLinks(HeroTestCase):
    """A link renders only with BOTH a label and a target.

    Symmetric on purpose, and specifically NOT falling back to the target's
    Title: a fallback would make the canvas fetch the target just to agree
    with this view, and the two surfaces would still disagree for the moment
    between picking and reloading.
    """

    TARGET = [{"@id": "http://nohost/plone/kontakt"}]

    def test_a_label_without_a_target_renders_nothing(self):
        assert self.hero({"cta_label": "Erstgespräch"}).find(class_="button") is None

    def test_a_target_without_a_label_renders_nothing(self):
        assert self.hero({"cta_href": self.TARGET}).find(class_="button") is None

    def test_both_halves_render_the_primary_call_to_action(self):
        link = self.hero({"cta_label": "Erstgespräch", "cta_href": self.TARGET}).find(
            "a", class_="button"
        )
        assert link.get_text() == "Erstgespräch"

    def test_a_resolved_target_is_emitted_site_relative(self):
        """`path_of`: the serializer stamps the API host, classic UI must not."""
        link = self.hero({"cta_label": "K", "cta_href": self.TARGET}).find("a", class_="button")
        assert link["href"] == "/plone/kontakt"

    def test_the_secondary_link_is_independent_of_the_primary(self):
        hero = self.hero({"link_label": "Leistungen", "link_href": self.TARGET})
        assert hero.find("a", class_="quiet-link").get_text() == "Leistungen"
        assert hero.find("a", class_="button") is None

    def test_one_surviving_link_is_enough_for_the_action_row(self):
        hero = self.hero({"link_label": "Leistungen", "link_href": self.TARGET})
        assert hero.find(class_="action-row") is not None


class TestReferenceShapes(HeroTestCase):
    """The widget writes a one-element list of `{"@id": …}` (ticket 02).

    A value that never went through the widget may be a bare dict or a plain
    string. Neither is worth throwing over — a hero authored through the API
    or carried in by a migration still has to render.
    """

    def test_the_widget_shape_is_read(self):
        hero = self.hero({"cta_label": "K", "cta_href": [{"@id": "/plone/a"}]})
        assert hero.find("a", class_="button")["href"] == "/plone/a"

    def test_a_bare_dict_is_read(self):
        hero = self.hero({"cta_label": "K", "cta_href": {"@id": "/plone/a"}})
        assert hero.find("a", class_="button")["href"] == "/plone/a"

    def test_a_plain_string_is_read(self):
        hero = self.hero({"cta_label": "K", "cta_href": "/plone/a"})
        assert hero.find("a", class_="button")["href"] == "/plone/a"

    def test_an_empty_list_is_absent(self):
        assert self.hero({"cta_label": "K", "cta_href": []}).find("a") is None

    def test_a_dict_without_an_id_is_absent(self):
        hero = self.hero({"cta_label": "K", "cta_href": [{"title": "no @id"}]})
        assert hero.find("a") is None


class TestLegend(HeroTestCase):
    """Always exactly four rows; the numerals are position, never content."""

    def _rows(self, legend):
        return self.hero({"legend": legend}).select(".ring-legend > div")

    def test_a_short_list_is_padded_to_four(self):
        rows = self._rows([{"title": "Prototyp"}])
        assert len(rows) == 4
        assert rows[0].dt.get_text() == "Prototyp"
        assert rows[1].find("dt") is None

    def test_a_long_list_is_truncated_to_four(self):
        rows = self._rows([{"title": str(n)} for n in range(9)])
        assert len(rows) == 4
        assert [row.dt.get_text() for row in rows] == ["0", "1", "2", "3"]

    def test_the_numerals_come_from_position_not_content(self):
        rows = self._rows([{"title": "z"}, {"title": "y"}])
        assert [row.b.get_text() for row in rows] == ["1", "2", "3", "4"]

    def test_only_the_last_ring_is_marked_now(self):
        rows = self._rows([])
        assert [row.get("class") for row in rows[:3]] == [None, None, None]
        assert rows[3]["class"] == ["is-now"]

    def test_the_markers_carry_the_same_highlight(self):
        markers = self.hero({}).select(".ring-markers > li")
        assert [marker.get_text() for marker in markers] == ["1", "2", "3", "4"]
        assert markers[3]["class"] == ["is-now"]

    def test_a_half_filled_entry_keeps_its_numeral(self):
        rows = self._rows([{"subtitle": "in Wochen bedienbar"}])
        assert rows[0].b.get_text() == "1"
        assert rows[0].find("dt") is None
        assert rows[0].dd.get_text() == "in Wochen bedienbar"

    def test_a_non_list_legend_degrades_to_four_empty_rows(self):
        assert len(self._rows("nonsense")) == 4

    def test_a_non_dict_entry_degrades_to_an_empty_row(self):
        rows = self._rows(["nonsense", None])
        assert rows[0].find("dt") is None and rows[0].b.get_text() == "1"


class TestPhotograph(HeroTestCase):
    """Two uploads, one `<picture>`, art-directed by splicing (ticket 05 §6).

    Plone's named scales give variants of ONE crop, never art direction, so
    the wide and the portrait framing stay two uploads. Two separate
    `<picture>` elements toggled by CSS would download both.
    """

    def _crops(self, wide=None, portrait=None):
        node = {}
        if wide is not None:
            node["image_wide"] = [{"@id": f"../resolveuid/{wide.UID()}"}]
        if portrait is not None:
            node["image_portrait"] = [{"@id": f"../resolveuid/{portrait.UID()}"}]
        return self.enriched(node)

    def test_no_crop_means_no_photograph_and_no_wash(self):
        hero = self.hero(self._crops())
        assert hero.find("picture") is None
        assert hero.find(class_="hero-wash") is None

    def test_a_crop_brings_the_wash_with_it(self):
        """Keyed off the data: the wash is the photograph's gradient.

        Over the flat token ground of a hero that has no photograph at all it
        would read as a rendering fault.
        """
        hero = self.hero(self._crops(wide=self.image("wide")))
        assert hero.find(class_="hero-wash") is not None

    def test_the_photograph_is_decorative(self):
        """No alt field anywhere in the schema; the whole picture is hidden."""
        picture = self.hero(self._crops(wide=self.image("wide"))).find("picture")
        assert picture["aria-hidden"] == "true"
        assert picture["class"] == ["hero-media"]
        assert picture.img["alt"] == ""

    def test_the_photograph_is_never_lazy(self):
        """It is the page's LCP image (ticket 05 §8)."""
        img = self.hero(self._crops(wide=self.image("wide"))).find("picture").img
        assert img.get("loading") is None
        assert img["fetchpriority"] == "high"
        assert img["decoding"] == "async"

    def test_the_resolution_ladder_includes_the_new_top_rung(self):
        """`enormous 2600` is what ticket 05 added the scale for."""
        source = self.hero(self._crops(wide=self.image("wide"))).find("source")
        assert "/@@images/image/enormous 2600w" in source["srcset"]
        assert "/@@images/image/huge 1600w" in source["srcset"]
        assert source["sizes"] == "100vw"

    def test_one_crop_carries_no_media_query(self):
        """One crop renders at EVERY breakpoint.

        Through the wide sourceset either way: the portrait variant's own
        query would leave everything above the breakpoint with no matching
        source and therefore no ladder at all.
        """
        sources = self.hero(self._crops(wide=self.image("wide"))).find_all("source")
        assert len(sources) == 1
        assert sources[0].get("media") is None

    def test_a_portrait_alone_renders_at_every_breakpoint(self):
        sources = self.hero(self._crops(portrait=self.image("tall"))).find_all("source")
        assert len(sources) == 1
        assert sources[0].get("media") is None
        assert "/plone/tall/" in sources[0]["srcset"]

    def test_two_crops_are_spliced_portrait_first(self):
        """First matching source wins, so order IS the art direction."""
        picture = self.hero(self._crops(wide=self.image("wide"), portrait=self.image("tall"))).find(
            "picture"
        )
        sources = picture.find_all("source")
        assert len(sources) == 2
        assert sources[0]["media"] == PORTRAIT_MEDIA
        assert "/plone/tall/" in sources[0]["srcset"]
        assert sources[1].get("media") is None
        assert "/plone/wide/" in sources[1]["srcset"]

    def test_the_spliced_picture_keeps_exactly_one_img(self):
        """The portrait's own `<img>` is discarded, not left behind."""
        picture = self.hero(self._crops(wide=self.image("wide"), portrait=self.image("tall"))).find(
            "picture"
        )
        assert len(picture.find_all("img")) == 1
        assert "/plone/wide/" in picture.img["src"]

    def test_the_img_carries_intrinsic_dimensions(self):
        """Without them the LCP element is a layout shift."""
        img = self.hero(self._crops(wide=self.image("wide"))).find("picture").img
        assert img["width"] == "1"
        assert img["height"] == "1"


class TestUnscalableCrop(HeroTestCase):
    """`image_source` returning None means "do not build a `<picture>`".

    No scales, no download URL, no base to hang it off, or an SVG — where
    scaling vector art buys nothing. One code path, so an SVG crop and a
    reference that never went through the widget degrade identically.
    """

    def test_an_svg_is_served_whole(self):
        logo = self.image("logo", SVG, "logo.svg")
        node = self.enriched({"image_portrait": [{"@id": f"../resolveuid/{logo.UID()}"}]})
        picture = self.hero(node).find("picture")
        assert picture.find("source") is None
        assert picture.img["src"] == "/plone/logo/@@images/image"

    def test_an_unenriched_reference_is_served_whole(self):
        picture = self.hero({"image_wide": [{"@id": "/plone/pic"}]}).find("picture")
        assert picture.find("source") is None
        assert picture.img["src"] == "/plone/pic/@@images/image"

    def test_it_keeps_the_element_the_stylesheet_expects(self):
        """`object-fit: cover` frames it exactly as it frames every other crop."""
        picture = self.hero({"image_wide": [{"@id": "/plone/pic"}]}).find("picture")
        assert picture["class"] == ["hero-media"]
        assert picture["aria-hidden"] == "true"

    def test_it_still_brings_the_wash(self):
        hero = self.hero({"image_wide": [{"@id": "/plone/pic"}]})
        assert hero.find(class_="hero-wash") is not None


class TestMarkupParity(HeroTestCase):
    """The template and the TSX emit one tree, or the shared sheet lies.

    `static-blocks/blocks.css` is scope-wrapped for `.aurora-blocks-view` as
    well as the editor's roots, so a class renamed on one side is a rule that
    silently stops matching on the other — with nothing failing anywhere.
    """

    FULL = {
        "kicker": "Nachhaltige Lösungen",
        "headline": "Anwendungen, die bleiben.",
        "lede": "Wir entwickeln Geschäftsanwendungen.",
        "cta_label": "Erstgespräch",
        "cta_href": [{"@id": "http://nohost/plone/kontakt"}],
        "link_label": "Alle Leistungen",
        "link_href": [{"@id": "http://nohost/plone/leistungen"}],
        "legend": [{"title": f"t{n}", "subtitle": f"s{n}"} for n in range(4)],
    }

    #: Every class `Hero.tsx`, `HeroMedia.tsx` and `Rings.tsx` emit.
    CLASSES = [
        "derico-hero",
        "home-hero__grid",
        "kicker",
        "lede",
        "action-row",
        "button",
        "quiet-link",
        "rings-figure",
        "rings-stage",
        "rings-disc",
        "ring-thin",
        "ring-now",
        "ring-future",
        "ring-markers",
        "ring-legend",
    ]

    @pytest.mark.parametrize("name", CLASSES)
    def test_every_class_the_editor_emits_is_emitted_here(self, name):
        assert self.soup(self.FULL).find(class_=name) is not None, (
            f"`.{name}` is in the TSX but not in hero.pt; the shared sheet's "
            "rules for it would apply in the canvas and nowhere else"
        )

    def test_the_hero_root_is_not_auroras_wrapper_stamp(self):
        """Ticket 07 measured why: the wrapper is a different box per surface.

        Painting the hero on `.block-derico-hero` gives the canvas a hero
        whose `overflow: hidden` clips the very breakout it is meant to have.
        """
        assert self.soup(self.FULL).find(class_="block-derico-hero") is None

    def test_the_shell_is_folded_in_rather_than_emitted(self):
        """06 §7: the mockup's `.shell` formula became a rule, not an element."""
        assert self.soup(self.FULL).find(class_="shell") is None

    def test_nothing_stamps_a_language(self):
        """`hyphens: auto` reads the page language, which main_template sets.

        A `lang` here would override it with the wrong one on a translated
        page — and the block has no `lang` field to get it right from.
        """
        assert not self.soup(self.FULL).find(attrs={"lang": True})

    def test_the_view_emits_no_breakout_of_its_own(self):
        """Ticket 11: the wrapper carries the breakout, and twice is a bug.

        Blicca stamps `has--block-width--full` and the `--block-width` custom
        property on the block WRAPPER, from the width the editor materialises
        onto the node. A hero that also sized itself would be a second,
        competing breakout — and one that differs between the two surfaces,
        since the wrapper is a different box on each.
        """
        hero = self.hero(self.FULL)
        assert "block-width" not in self.render(self.FULL)
        assert hero.get("style") is None
        assert not hero.find(attrs={"style": True})

    def test_the_ring_markers_are_decorative(self):
        """They repeat the legend's numerals; a screen reader wants one copy."""
        assert self.soup(self.FULL).find(class_="ring-markers")["aria-hidden"] == "true"

    def test_the_rings_figure_labels_itself(self):
        disc = self.soup(self.FULL).find("svg", class_="rings-disc")
        assert disc["role"] == "img"
        assert disc["aria-label"]

    def test_the_template_ships_none_of_its_own_commentary(self):
        """Chameleon's hidden comments; the reasoning is not the visitor's."""
        assert "<!--" not in self.render(self.FULL)


class TestDispatch(HeroTestCase):
    """Contract §5.1: the view NAME is the whole of the registration."""

    NODE = {"@type": BLOCK_TYPE, "headline": "Anwendungen, die bleiben."}

    def test_the_published_page_renders_the_hero(self):
        html = self.page(self.NODE)
        assert "derico-hero" in html
        assert "Anwendungen, die bleiben." in html

    def test_the_block_does_not_fall_through_to_the_default_view(self):
        """`block-unrendered` is what an unregistered @type collapses to."""
        assert "block-unrendered" not in self.page(self.NODE)

    def test_the_renderer_does_not_error(self):
        """§5.4 swallows a renderer exception into this placeholder."""
        assert "block-render-error" not in self.page(self.NODE)


class TestDerivedDataIsSuppliedByStockRestapi(HeroTestCase):
    """Contract §5.3, satisfied without an add-on transformer of our own.

    §5.3 requires the derived data the EDITOR component expects at render
    time to be injected by an `IBlockFieldSerializationTransformer`, so both
    surfaces see identical data, and stripped again by a paired
    deserialization transformer so it is never persisted.

    Ticket 01 found that stock `plone.restapi` already does exactly this for
    a nested `{"@id": …}`, regardless of the field's name — which is why this
    package registers no transformer. That is a claim about somebody else's
    code, so it is asserted here rather than trusted: the day it stops being
    true, the hero silently loses its resolution ladder and serves one
    full-size original to every visitor.
    """

    def _node(self, item):
        return {"@type": BLOCK_TYPE, "image_wide": [{"@id": f"../resolveuid/{item.UID()}"}]}

    def test_the_nested_id_is_resolved_to_an_absolute_url(self):
        crop = self.enriched(self._node(self.image("wide")))["image_wide"][0]
        assert crop["@id"] == "http://nohost/plone/wide"

    def test_image_scales_is_injected_beside_it(self):
        crop = self.enriched(self._node(self.image("wide")))["image_wide"][0]
        assert crop["image_scales"]["image"][0]["download"]

    def test_the_injected_data_is_not_persisted(self):
        """The paired stripping half — derived data is never stored.

        The loop below is `BlocksJSONFieldDeserializer.__call__`'s, run over
        the same enriched value the serializer produced. Stock restapi's
        `ResolveUIDDeserializerBase` pops `image_scales` from every dict it
        walks and turns the absolute `@id` back into a `resolveuid` link, so
        what is persisted is exactly what the widget wrote.
        """
        from plone.restapi.blocks import iter_block_transform_handlers
        from plone.restapi.blocks import visit_blocks
        from plone.restapi.interfaces import IBlockFieldDeserializationTransformer

        item = self.image("wide")
        stored = {"0": self.enriched(self._node(item))}
        for block in visit_blocks(self.doc, stored):
            new_block = block.copy()
            for handler in iter_block_transform_handlers(
                self.doc, block, IBlockFieldDeserializationTransformer
            ):
                new_block = handler(new_block)
            block.clear()
            block.update(new_block)

        crop = stored["0"]["image_wide"][0]
        assert "image_scales" not in crop, (
            "derived data is being persisted; a stale ladder would outlive the image it describes"
        )
        assert crop["@id"] == f"../resolveuid/{item.UID()}", (
            "the reference is not being stored uid-first; a rename would "
            "break the hero's photograph"
        )
