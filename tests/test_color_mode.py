"""derico is light-only: every page pins `data-bs-theme="light"` on <html>."""

import re

import pytest
from bs4 import BeautifulSoup
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser

from . import clara_css as css_tools


@pytest.fixture
def browser(functional):
    return Browser(functional["app"])


def html_theme(browser, url):
    browser.open(url)
    return BeautifulSoup(browser.contents, "html.parser").html.get("data-bs-theme")


@pytest.mark.parametrize("path", ["", "/@@search", "/contact-info", "/login"])
def test_anonymous_pages_are_light(browser, functional, path):
    assert html_theme(browser, functional["portal"].absolute_url() + path) == "light"


def test_editor_pages_are_light(browser, functional):
    browser.addHeader("Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}")
    url = functional["portal"].absolute_url() + "/@@overview-controlpanel"
    assert html_theme(browser, url) == "light"


def test_the_attribute_is_set_once(browser, functional):
    browser.open(functional["portal"].absolute_url())
    assert browser.contents.count("data-bs-theme=") == 1


@pytest.mark.skipif(
    css_tools.clara_bundle_path() is None,
    reason="plonetheme.clara's compiled bundle is not available",
)
def test_clara_honours_the_pin():
    """The premise: Clara's OS-preference dark mode skips a light root."""
    css = css_tools.clara_bundle_path().read_text()
    assert re.search(r"prefers-color-scheme: *dark\)\{:root:not\(\[data-bs-theme=light\]\)", css)
