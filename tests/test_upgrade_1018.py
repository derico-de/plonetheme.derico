"""Upgrade step 1017 -> 1018: the AVIF settings of the imaging control panel."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IImagingSchema
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


PROFILE = "plonetheme.derico:default"
AVIF_DEFAULTS = {
    "plone.avif_mode": "avif_with_fallback",
    "plone.avif_quality": 65,
    "plone.avif_speed": 8,
}

pytestmark = pytest.mark.skipif(
    "avif_mode" not in IImagingSchema,
    reason="plone.base without the AVIF settings; the step registers nothing",
)


class TestUpgrade1018:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.registry = getUtility(IRegistry)
        # A site installed before plone.base learned the AVIF settings.
        for name in AVIF_DEFAULTS:
            del self.registry.records[name]
        self.setup_tool.setLastVersionForProfile(PROFILE, "1017")

    def upgrade(self):
        self.setup_tool.upgradeProfile(PROFILE, dest="1018")

    def test_adds_the_avif_records_with_their_defaults(self):
        self.upgrade()
        for name, default in AVIF_DEFAULTS.items():
            assert api.portal.get_registry_record(name) == default

    def test_keeps_the_other_imaging_settings(self):
        api.portal.set_registry_record("plone.quality", 70)
        api.portal.set_registry_record("plone.allowed_sizes", ["huge 1600:65536"])
        self.upgrade()
        assert api.portal.get_registry_record("plone.quality") == 70
        assert api.portal.get_registry_record("plone.allowed_sizes") == ["huge 1600:65536"]

    def test_keeps_an_avif_mode_the_site_already_has(self):
        self.registry.registerInterface(IImagingSchema, prefix="plone")
        api.portal.set_registry_record("plone.avif_mode", "disabled")
        self.upgrade()
        assert api.portal.get_registry_record("plone.avif_mode") == "disabled"

    def test_leaves_the_other_registry_records_alone(self):
        api.portal.set_registry_record("plone.navigation_depth", 5)
        self.upgrade()
        assert api.portal.get_registry_record("plone.navigation_depth") == 5

    def test_reaches_the_profile_version(self):
        self.upgrade()
        assert self.setup_tool.getLastVersionForProfile(PROFILE) == ("1018",)
