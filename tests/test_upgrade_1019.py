"""Upgrade step 1018 -> 1019: the fragments editor bundle record is dropped."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import blockaddons
from plone.registry import field
from plone.registry import Record
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from plonetheme.derico.upgrades.v1019 import PREFIX
from plonetheme.derico.upgrades.v1019 import upgrade


PROFILE = "plonetheme.derico:default"
HERO = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.hero"


class TestUpgrade1019:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.registry = getUtility(IRegistry)
        # A site installed while profile 1018 still registered the record.
        self.registry.records[f"{PREFIX}.bundle"] = Record(
            field.TextLine(), "++plone++plonetheme.derico.blocks/fragments.js"
        )
        self.registry.records[f"{PREFIX}.block_api"] = Record(field.TextLine(), "1.0")
        self.registry.records[f"{PREFIX}.types"] = Record(
            field.List(value_type=field.TextLine()), []
        )
        self.registry.records[f"{PREFIX}.enabled"] = Record(field.Bool(), True)
        self.registry.records[f"{PREFIX}.weight"] = Record(field.Int(), 120)
        self.setup_tool.setLastVersionForProfile(PROFILE, "1018")

    def stale(self):
        return [name for name in self.registry.records if name.startswith(f"{PREFIX}.")]

    def test_removes_the_record(self):
        assert len(self.stale()) == 5
        self.setup_tool.upgradeProfile(PROFILE, dest="1019")
        assert self.stale() == []

    def test_keeps_the_block_records(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1019")
        assert api.portal.get_registry_record(f"{HERO}.enabled") is True

    def test_the_editor_stops_discovering_it(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1019")
        names = [status.name for status in blockaddons.evaluate(self.portal)]
        assert "plonetheme.derico.fragments" not in names

    def test_runs_twice_without_complaint(self):
        upgrade(self.setup_tool)
        upgrade(self.setup_tool)
        assert self.stale() == []

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1019")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1019",)
