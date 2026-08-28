"""Install collective.fragmentsblock on sites that already have derico.

`profiles/default/metadata.xml` has depended on
`profile-collective.fragmentsblock:default` since 1003, but GenericSetup
applies dependency profiles on INSTALL only — an upgrade never revisits
them. So every site installed before 1003 kept a derico that provides
fragments and a portal with no block to place them in, and 1003 said so and
left the add-on to the control panel.

1004 makes that gap a defect rather than an inconvenience: it converts every
stored `derico-snippet` node into a `fragment` node, so a site that upgrades
without the add-on ends up with blocks whose type nothing resolves. The
add-on is installed here instead, in the same upgrade run and right after
the conversion that needs it.

Guarded rather than unconditional: `install_product` logs an error and
returns False on an already-installed product, and a site installed fresh
since 1003 got the add-on from the dependency. Re-running the step must be
a no-op, not a red herring in the log.
"""

import logging

from plone import api


logger = logging.getLogger(__name__)

PRODUCT = "collective.fragmentsblock"


def upgrade(context):
    """Upgrade from profile version 1004 to 1005."""
    logger.info("Running upgrade step: Install %s", PRODUCT)
    installer = api.addon.get_installer(api.portal.get())
    if installer.is_product_installed(PRODUCT):
        logger.info("%s is already installed, nothing to do", PRODUCT)
        return
    installer.install_product(PRODUCT)
    logger.info("Installed %s", PRODUCT)
