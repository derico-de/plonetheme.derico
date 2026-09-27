"""Upgrade steps since the 1015 baseline are registered."""

from pathlib import Path
from xml.etree import ElementTree

import pytest
from plone import api


METADATA = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "plonetheme"
    / "derico"
    / "profiles"
    / "default"
    / "metadata.xml"
)
BASELINE = 1015
LATEST = int(ElementTree.parse(METADATA).findtext("version"))
VERSIONS = range(BASELINE + 1, LATEST + 1)


@pytest.fixture
def upgrades(integration):
    setup_tool = api.portal.get_tool("portal_setup")
    steps = setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
    flat = []
    for step in steps:
        flat.extend(step if isinstance(step, list) else [step])
    return {(step["ssource"], step["sdest"]) for step in flat}


def test_the_profile_is_at_the_latest_version(integration):
    setup_tool = api.portal.get_tool("portal_setup")
    (version,) = setup_tool.getLastVersionForProfile("plonetheme.derico:default")
    assert int(version) == LATEST


@pytest.mark.parametrize("version", VERSIONS)
def test_upgrade_step_registered(upgrades, version):
    assert (str(version - 1), str(version)) in upgrades
