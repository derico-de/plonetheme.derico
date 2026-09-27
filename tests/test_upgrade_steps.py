"""Checks every upgrade step shares: registered, and its profile hidden."""

from pathlib import Path
from xml.etree import ElementTree

import pytest
from plone import api

from plonetheme.derico.setuphandlers import HiddenProfiles


METADATA = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "plonetheme"
    / "derico"
    / "profiles"
    / "default"
    / "metadata.xml"
)
LATEST = int(ElementTree.parse(METADATA).findtext("version"))
VERSIONS = range(1001, LATEST + 1)


@pytest.fixture
def upgrades(integration):
    setup_tool = api.portal.get_tool("portal_setup")
    steps = setup_tool.listUpgrades("plonetheme.derico:default", show_old=True)
    flat = []
    for step in steps:
        flat.extend(step if isinstance(step, list) else [step])
    return {(step["ssource"], step["sdest"]) for step in flat}


@pytest.mark.parametrize("version", VERSIONS)
def test_upgrade_step_registered(upgrades, version):
    assert (str(version - 1), str(version)) in upgrades


@pytest.mark.parametrize("version", VERSIONS)
def test_upgrade_profile_is_hidden(version):
    profile = f"plonetheme.derico.upgrades:{version}"
    assert profile in HiddenProfiles().getNonInstallableProfiles()
