"""Upgrade step 1015 -> 1016: the empty catalog.xml is gone."""

from pathlib import Path

import plonetheme.derico
from plonetheme.derico.upgrades.v1016 import upgrade


PROFILE = Path(plonetheme.derico.__file__).parent / "profiles" / "default"


def test_the_profile_ships_no_catalog_xml():
    assert not (PROFILE / "catalog.xml").exists()


def test_the_catalog_is_untouched(integration):
    catalog = integration["portal"].portal_catalog
    indexes, columns = set(catalog.indexes()), set(catalog.schema())
    upgrade(integration["portal"].portal_setup)
    assert set(catalog.indexes()) == indexes
    assert set(catalog.schema()) == columns
