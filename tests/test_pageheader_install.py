"""Installing the Derico Page Header: the record, the renderer, the gate.

The same silent failures the hero's install test guards against (a record
that evaluates to a fail-soft skip is a block that is simply not in the slash
menu), so the assertions are Blicca's own verdicts. The one deliberate
difference from the hero: NO insert gate. A page header is how every page
opens, so the editor who writes the page may insert it.
"""

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import blockaddons
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.pageheader"
NAME = "plonetheme.derico.pageheader"
BLOCK_TYPE = "derico-page-header"
STATIC_BASE = "++plone++plonetheme.derico.blocks"


def record(name, default=None):
    return api.portal.get_registry_record(f"{RECORD}.{name}", default=default)


class InstallTestCase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, IPlonethemeDericoLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def status(self):
        """The page header's record, as Blicca's own discovery sees it."""
        found = [s for s in blockaddons.evaluate(self.portal) if s.name == NAME]
        assert found, "the page header's record is not discovered as a block add-on"
        return found[0]


class TestTheBlockRecord(InstallTestCase):
    def test_the_record_is_loadable(self):
        status = self.status()
        assert status.loadable, f"the page header would be skipped: {status.skip_reason}"

    def test_the_bundle_and_the_stylesheet_resolve(self):
        status = self.status()
        assert status.bundle_url
        assert status.css_url

    def test_the_assets_are_served_from_the_block_directory(self):
        assert record("bundle") == f"{STATIC_BASE}/pageheader.js"
        assert record("css") == f"{STATIC_BASE}/blocks.css"

    def test_the_stylesheet_is_the_one_the_hero_shares(self):
        """Lib mode emits ONE sheet per build (ticket 04 §5)."""
        hero = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero"
        assert record("css") == api.portal.get_registry_record(f"{hero}.css")

    def test_its_own_bundle_and_not_the_heros(self):
        """One record, one bundle, one `install()` — the per-record kill switch."""
        hero = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero"
        assert record("bundle") != api.portal.get_registry_record(f"{hero}.bundle")

    def test_the_record_declares_the_block_type(self):
        assert tuple(record("types")) == (BLOCK_TYPE,)

    def test_the_record_declares_the_block_api_floor(self):
        assert record("block_api") == "1.0"

    def test_the_record_is_enabled(self):
        assert record("enabled") is True

    def test_there_is_no_server_renderer_gap(self):
        gaps = blockaddons.lockstep_gaps(
            self.portal, self.request, blockaddons.evaluate(self.portal)
        )
        assert gaps == [], f"registered blocks with no server renderer: {gaps}"

    def test_the_renderer_is_this_packages(self):
        from plonetheme.derico.browser.pageheader import DericoPageHeaderView

        view = getMultiAdapter((self.portal, self.request), name=f"aurora-block-{BLOCK_TYPE}")
        assert isinstance(view, DericoPageHeaderView)


class TestNoInsertGate(InstallTestCase):
    def test_the_record_names_no_permission(self):
        assert not record("permission")

    def test_an_ordinary_editor_may_insert_it(self):
        setRoles(self.portal, TEST_USER_ID, ["Editor"])
        login(self.portal, TEST_USER_NAME)
        assert blockaddons.may_insert(self.portal, self.status())
        assert BLOCK_TYPE not in blockaddons.restricted_block_types(self.portal)
