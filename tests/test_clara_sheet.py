"""The Clara sheet: derico's compile of Clara's bundle loads in place of Clara's own.

`bundle-src/` builds `static/clara.min.css` from Clara's Sass sources without
the Bootstrap parts derico never uses; `clara-sheet.test.ts` holds the file to
a fresh build. These hold the site to the file.
"""

import re

import pytest
from bs4 import BeautifulSoup
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser

from . import clara_css as css_tools


CLARA_BUNDLE = "plone.bundles/plonetheme-clara"
DERICO_COMPILE = "++resource++plonetheme.derico/clara.min.css"
CLARA_OWN = "++resource++plonetheme.clara/clara.min.css"


def test_the_clara_bundle_loads_derico_compile(integration):
    assert api.portal.get_registry_record(f"{CLARA_BUNDLE}.csscompilation") == DERICO_COMPILE


def test_the_clara_bundle_stays_enabled_and_first(integration):
    assert api.portal.get_registry_record(f"{CLARA_BUNDLE}.enabled") is True
    assert api.portal.get_registry_record("plone.bundles/plonetheme-derico.depends") == (
        "plonetheme-clara"
    )


def test_the_page_links_the_compile_and_not_clara_own_sheet(functional):
    browser = Browser(functional["app"])
    browser.open(functional["portal"].absolute_url())
    soup = BeautifulSoup(browser.contents, "html.parser")
    hrefs = [link["href"] for link in soup.select("link[rel=stylesheet]")]
    assert [href for href in hrefs if href.endswith(f"/{DERICO_COMPILE}")]
    assert not [href for href in hrefs if href.endswith(f"/{CLARA_OWN}")]


def test_every_font_it_names_is_in_clara_resource_directory():
    """Served from derico's directory, the sheet reaches back into Clara's for the fonts."""
    clara_static = css_tools.clara_bundle_path()
    if clara_static is None:
        pytest.skip("plonetheme.clara's static directory is not available")
    urls = re.findall(r'url\("([^"]+\.woff2)"\)', css_tools.CLARA_SHEET.read_text())
    assert urls
    for url in urls:
        prefix, name = url.rsplit("/", 1)
        assert prefix == "../++resource++plonetheme.clara"
        assert (clara_static.parent / name).is_file(), name


class TestUninstall:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        api.addon.get_installer(self.portal).uninstall_product("plonetheme.derico")

    def test_clara_loads_its_own_sheet_again(self):
        """Clara stays installed; it must not keep pointing at a sheet that is gone."""
        assert api.portal.get_registry_record(f"{CLARA_BUNDLE}.csscompilation") == CLARA_OWN
        assert api.portal.get_registry_record(f"{CLARA_BUNDLE}.enabled") is True
