"""Upgrade step 1019 -> 1020: a no-op now that block_api is retired.

The step used to declare block-API 2.0 on both records; `block_api` has
since left `IAuroraBlockAddon` (ADR 0024 in `plone.blicca.auroraeditor`), so
setting it here would raise `KeyError` on import. Nothing is left for this
step to do except carry a site across the version number.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


PROFILE = "plonetheme.derico:default"
NAMES = ["plonetheme.derico.hero", "plonetheme.derico.pageheader"]
PREFIX = "plone.blicca.auroraeditor.blockaddons"


class TestUpgrade1020:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.setup_tool.setLastVersionForProfile(PROFILE, "1019")

    def test_leaves_the_block_records_alone(self):
        before = {name: api.portal.get_registry_record(f"{PREFIX}/{name}.bundle") for name in NAMES}
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        for name in NAMES:
            assert api.portal.get_registry_record(f"{PREFIX}/{name}.bundle") == before[name]

    def test_reaches_the_profile_version(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1020")
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1020",)
