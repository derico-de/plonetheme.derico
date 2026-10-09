"""Upgrade step 1019 -> 1020: the block records declare block-API 2.0."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import blockaddons


PROFILE = "plonetheme.derico:default"
NAMES = ["plonetheme.derico.hero", "plonetheme.derico.pageheader"]
PREFIX = "plone.blicca.auroraeditor.blockaddons"


class TestUpgrade1020:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        for name in NAMES:
            api.portal.set_registry_record(f"{PREFIX}/{name}.block_api", "1.0")
        self.setup_tool.setLastVersionForProfile(PROFILE, "1019")

    def test_declares_block_api_2(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        for name in NAMES:
            assert api.portal.get_registry_record(f"{PREFIX}/{name}.block_api") == "2.0"

    def test_the_blocks_load_again(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        statuses = {s.name: s for s in blockaddons.evaluate(self.portal)}
        for name in NAMES:
            assert statuses[name].loadable

    def test_leaves_the_rest_of_the_records_alone(self):
        hero = f"{PREFIX}/{NAMES[0]}"
        api.portal.set_registry_record(f"{hero}.enabled", False)
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        assert api.portal.get_registry_record(f"{hero}.enabled") is False
        assert api.portal.get_registry_record(f"{hero}.bundle") == (
            "++plone++plonetheme.derico.blocks/hero.js"
        )

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1020",)
