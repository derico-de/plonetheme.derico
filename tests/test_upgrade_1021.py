"""Upgrade step 1020 -> 1021: the theme's own orphan block_api records are dropped."""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from plonetheme.derico.upgrades.v1021 import upgrade


PROFILE = "plonetheme.derico:default"
NAMES = ["plonetheme.derico.hero", "plonetheme.derico.pageheader"]
PREFIX = "plone.blicca.auroraeditor.blockaddons"


class TestUpgrade1021:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.registry = getUtility(IRegistry)
        self.setup_tool.setLastVersionForProfile(PROFILE, "1020")

    def _declare_orphan(self, name):
        self.registry.records[f"{PREFIX}/{name}.block_api"] = Record(field.TextLine(), "2.0")

    def test_drops_the_orphan_records_if_left(self):
        for name in NAMES:
            self._declare_orphan(name)
        self.setup_tool.upgradeProfile(PROFILE, dest="1021")
        for name in NAMES:
            assert f"{PREFIX}/{name}.block_api" not in self.registry.records

    def test_a_site_without_the_orphans_is_untouched(self):
        """A site that already upgraded through 1020 without the field."""
        before = {name: self.registry.records[f"{PREFIX}/{name}.bundle"].value for name in NAMES}
        self.setup_tool.upgradeProfile(PROFILE, dest="1021")
        for name in NAMES:
            assert f"{PREFIX}/{name}.block_api" not in self.registry.records
            assert self.registry.records[f"{PREFIX}/{name}.bundle"].value == before[name]

    def test_runs_twice_without_complaint(self):
        self._declare_orphan(NAMES[0])
        upgrade(self.setup_tool)
        upgrade(self.setup_tool)
        assert f"{PREFIX}/{NAMES[0]}.block_api" not in self.registry.records

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1021")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1021",)
