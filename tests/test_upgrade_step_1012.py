"""Tests for upgrade step 1011 -> 1012: the footer bundle.

An existing site carries the bundle records that were in the default
profile the day derico was installed there, and nothing declared since. The
footer's stylesheet is a NEW bundle record, and without it every page on an
upgraded site would render the footer blocks in the body's running type —
16px ink where the design puts 15px ink-soft, and links with no touch
target.
"""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


PROFILE = "plonetheme.derico.upgrades:1012"
BUNDLE = "plone.bundles/plonetheme-derico-footer"
FIELDS = (
    "csscompilation",
    "depends",
    "load_defer",
    "expression",
    "enabled",
)


class TestUpgrade1012:
    """Test upgrade to version 1012."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.registry = getUtility(IRegistry)

    def _drop_record(self):
        """The site that predates 1012: derico installed, no footer bundle."""
        for field in FIELDS:
            del self.registry.records[f"{BUNDLE}.{field}"]
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled", default=None) is None

    def test_upgrade_step_registered(self):
        steps = self.setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(step["sdest"] == "1012" and step["ssource"] == "1011" for step in flat)

    def test_upgrade_profile_is_hidden(self):
        from plonetheme.derico.setuphandlers import HiddenProfiles

        assert PROFILE in HiddenProfiles().getNonInstallableProfiles()

    def test_the_profile_is_at_this_version(self):
        """The newest step's test owns the exact version."""
        (version,) = self.setup_tool.getLastVersionForProfile("plonetheme.derico:default")
        assert int(version) == 1012

    def test_upgrade_adds_the_bundle(self):
        self._drop_record()
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        assert api.portal.get_registry_record(f"{BUNDLE}.enabled") is True
        assert api.portal.get_registry_record(f"{BUNDLE}.csscompilation") == (
            "++resource++plonetheme.derico/footer.css"
        )
        assert api.portal.get_registry_record(f"{BUNDLE}.depends") == "plonetheme-derico"

    def test_upgrade_is_idempotent(self):
        """Running it on a site that already has the record changes nothing."""
        before = {field: api.portal.get_registry_record(f"{BUNDLE}.{field}") for field in FIELDS}
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        after = {field: api.portal.get_registry_record(f"{BUNDLE}.{field}") for field in FIELDS}
        assert before == after

    def test_upgrade_leaves_the_site_logo_alone(self):
        """No reload of the default profile: an administrator's logo survives."""
        api.portal.set_registry_record("plone.site_logo", b"filenameb64:eA==;datab64:eA==")
        self._drop_record()
        self.setup_tool.runAllImportStepsFromProfile(f"profile-{PROFILE}")
        assert api.portal.get_registry_record("plone.site_logo") == b"filenameb64:eA==;datab64:eA=="
