"""Hashed `++resource++` URLs get plone.app.caching's one-year ruleset."""

import pytest
from plone.testing.zope import Browser


HASHED = "++webresource++9b7963ce-1e60-5cba-977f-9ea553b8ffd1/"
DERICO_CSS = "++resource++plonetheme.derico/derico.css"


@pytest.fixture
def browser(caching_functional):
    return Browser(caching_functional["app"])


def cache_control(browser, portal_url, path):
    browser.open(f"{portal_url}/{path}")
    return browser.headers["Cache-Control"]


def test_hashed_resource_is_cached_for_a_year(browser, caching_functional):
    portal_url = caching_functional["portal"].absolute_url()
    assert "max-age=31536000" in cache_control(browser, portal_url, HASHED + DERICO_CSS)


def test_unhashed_resource_keeps_the_short_ruleset(browser, caching_functional):
    portal_url = caching_functional["portal"].absolute_url()
    assert "max-age=86400" in cache_control(browser, portal_url, DERICO_CSS)
