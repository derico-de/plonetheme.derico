"""Install the add-ons derico depends on.

`profiles/default/metadata.xml` names three add-on profiles as dependencies,
and GenericSetup applies dependency profiles on INSTALL only -- an upgrade
never revisits them. So a site carries whichever dependencies were declared
on the day derico was installed there, and every dependency declared since
is simply absent: the machinery derico renders against, missing, with a
theme that looks installed.

1005 closed that gap for `collective.fragmentsblock` alone, because 1004
turned its absence into stored blocks nothing could resolve. This step
closes it for the whole dependency list at once, so the answer to "is this
site missing an add-on derico needs?" stops depending on which version it
was installed at.

`profile-plone.app.registry:default` is deliberately not here: it is a core
Plone profile, present in every site before derico arrives, not an add-on
the installer manages.

Guarded per product rather than unconditional: `install_product` logs an
error and returns False for an already-installed product, and most sites
will have most of these. Re-running the step must be a no-op, not a screen
of red herrings in the log.
"""

import logging

from plone import api


logger = logging.getLogger(__name__)

# The add-on half of metadata.xml's <dependencies>, in the order it lists
# them: the editor before the theme it mounts in, because that is the deeper
# requirement, and the fragment block last.
PRODUCTS = (
    "plone.blicca.auroraeditor",
    "plonetheme.clara",
    "collective.fragmentsblock",
)


def upgrade(context):
    """Upgrade from profile version 1006 to 1007."""
    logger.info("Running upgrade step: Install the add-ons derico depends on")
    installer = api.addon.get_installer(api.portal.get())
    for product in PRODUCTS:
        if installer.is_product_installed(product):
            logger.info("%s is already installed, nothing to do", product)
            continue
        installer.install_product(product)
        logger.info("Installed %s", product)
