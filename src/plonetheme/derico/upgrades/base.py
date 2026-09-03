"""Shared upgrade step utilities for plonetheme.derico."""

import logging

from plone import api
from plone.app.upgrade.utils import loadMigrationProfile


logger = logging.getLogger(__name__)


def reload_gs_profile(context):
    """Reload the default GenericSetup profile."""
    loadMigrationProfile(context, "profile-plonetheme.derico:default")


# The add-on half of `profiles/default/metadata.xml`'s <dependencies>, in the
# order it lists them. `profile-plone.app.registry:default` is not here: it is
# a core Plone profile every site already has, not an add-on the installer
# manages. `test_setup` holds this tuple to the profile, so the two cannot
# drift apart silently.
ADDON_DEPENDENCIES = (
    "plone.blicca.auroraeditor",
    "plonetheme.clara",
    "collective.fragmentsblock",
    "derico.blicca.promoblock",
)


def install_addon_dependencies(context):
    """Install every declared add-on dependency this site is missing.

    GenericSetup applies dependency profiles on INSTALL only, so a site
    carries whichever dependencies were declared the day derico was installed
    there. Every upgrade step that adds one calls this, and it installs the
    whole list rather than the one name that prompted it: a site that skipped
    two versions is missing two add-ons, and there is nothing to gain from
    making it depend on which handler runs.

    Guarded per product: `install_product` logs an error and returns False
    for an already-installed product, and most sites have most of these.
    """
    installer = api.addon.get_installer(api.portal.get())
    for product in ADDON_DEPENDENCIES:
        if installer.is_product_installed(product):
            logger.info("%s is already installed, nothing to do", product)
            continue
        installer.install_product(product)
        logger.info("Installed %s", product)
