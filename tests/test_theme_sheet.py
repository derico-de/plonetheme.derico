"""The theme sheet: every hand-written sheet under `static/`, delivered as one.

`bundle-src/` builds them into `static/derico.min.css`, committed like the
block bundles, so a page makes one render-blocking request for the theme
instead of five. Its own test (`theme-sheet.test.ts`) holds the committed
file to a fresh build; these hold the site to the file.
"""

import json

from bs4 import BeautifulSoup
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from zope.component import getUtility

from . import clara_css as css_tools


BUNDLE = "plone.bundles/plonetheme-derico"


def _sources():
    """The sheets the build read, in sheet order: an index map, one section per sheet."""
    source_map = css_tools.THEME_SHEET.with_name(f"{css_tools.THEME_SHEET.name}.map")
    sections = json.loads(source_map.read_text())["sections"]
    return [name for section in sections for name in section["map"]["sources"]]


def test_the_theme_has_one_bundle(integration):
    records = getUtility(IRegistry).records
    bundles = {name.rsplit(".", 1)[0] for name in records if name.startswith(BUNDLE)}
    assert bundles == {BUNDLE}


def test_the_page_links_one_theme_sheet(functional):
    browser = Browser(functional["app"])
    browser.open(functional["portal"].absolute_url())
    soup = BeautifulSoup(browser.contents, "html.parser")
    sheets = [
        link["href"]
        for link in soup.select("link[rel=stylesheet]")
        if "/++resource++plonetheme.derico/" in link["href"]
    ]
    assert len(sheets) == 1, sheets
    assert sheets[0].endswith("/derico.min.css")


class TestComposition:
    """What the committed sheet is built from, read off its source map."""

    def test_every_hand_written_sheet_ships_in_it(self):
        """Globbed, like the corpus tests: a new sheet must join the build."""
        assert sorted(_sources()) == sorted(path.name for path in css_tools.hand_written_sheets())

    def test_the_token_layer_comes_first(self):
        assert _sources()[0] == "derico.css"

    def test_the_print_sheet_comes_last(self):
        """Unlayered and unscoped, so source order is cascade order: last, a
        print rule wins every tie with a screen rule."""
        assert _sources()[-1] == "print.css"
