"""Install the Promo block.

`derico.blicca.promoblock` joins metadata.xml's <dependencies> at this
version, which covers sites installed from here on. Existing sites need this
step for the same reason 1007 exists: a dependency profile is applied on
install and never again.

The handler is 1007's, unchanged -- `install_addon_dependencies` walks the
whole declared list, and the Promo block is now on it. A site upgrading
straight from 1006 therefore installs it in 1007 and finds nothing left to
do here; a site already at 1007 installs it here. Both land in the same
place, which is the point of the list being one list.
"""

import logging

from .base import install_addon_dependencies


logger = logging.getLogger(__name__)


def upgrade(context):
    """Upgrade from profile version 1007 to 1008."""
    logger.info("Running upgrade step: Install the Promo block")
    install_addon_dependencies(context)
