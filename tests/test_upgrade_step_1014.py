"""Tests for upgrade step 1013 -> 1014: the Derico Page Header's record.

An existing site carries the block records that were in the default profile
the day derico was installed there. The page header is a NEW record, and
without it @@aurora-edit never loads the bundle: the block is not in the
slash menu, and a page authored with it elsewhere renders `block-unrendered`.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


PROFILE = "plonetheme.derico.upgrades:1014"
RECORD = "plone.blicca.auroraeditor.blockaddons/plonetheme.derico.pageheader"
FIELDS = ("bundle", "block_api", "css", "types", "permission", "enabled", "weight")


class TestUpgrade1014:
    """Test upgrade to version 1014."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.registry = getUtility(IRegistry)

    def _drop_record(self):
        """The site that predates 1014: derico installed, no page header record."""
        for field in FIELDS:
            del self.registry.records[f"{RECORD}.{field}"]
        assert api.portal.get_registry_record(f"{RECORD}.enabled", default=None) is None

    def test_upgrade_step_registered(self):
        steps = self.setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(step["sdest"] == "1014" and step["ssource"] == "1013" for step in flat)

    def test_upgrade_profile_is_hidden(self):
        from plonetheme.derico.setuphandlers import HiddenProfiles

        assert PROFILE in HiddenProfiles().getNonInstallableProfiles()

    def test_upgrade_adds_the_record(self):
        self._drop_record()
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        assert api.portal.get_registry_record(f"{RECORD}.enabled") is True
        assert api.portal.get_registry_record(f"{RECORD}.bundle") == (
            "++plone++plonetheme.derico.blocks/pageheader.js"
        )
        assert tuple(api.portal.get_registry_record(f"{RECORD}.types")) == ("derico-page-header",)

    def test_upgrade_is_idempotent(self):
        before = {f: api.portal.get_registry_record(f"{RECORD}.{f}") for f in FIELDS}
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        after = {f: api.portal.get_registry_record(f"{RECORD}.{f}") for f in FIELDS}
        assert before == after

    def test_upgrade_leaves_the_site_logo_alone(self):
        """No reload of the default profile: an administrator's logo survives."""
        api.portal.set_registry_record("plone.site_logo", b"filenameb64:eA==;datab64:eA==")
        self._drop_record()
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        assert api.portal.get_registry_record("plone.site_logo") == b"filenameb64:eA==;datab64:eA=="
