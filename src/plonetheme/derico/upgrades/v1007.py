"""Install the add-ons derico depends on.

`profiles/default/metadata.xml` names its add-on profiles as dependencies,
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

The list and the guard live in `base`, because 1008 needs exactly the same
pass over exactly the same list.
"""

import logging

from .base import install_addon_dependencies


logger = logging.getLogger(__name__)


def upgrade(context):
    """Upgrade from profile version 1006 to 1007."""
    logger.info("Running upgrade step: Install the add-ons derico depends on")
    install_addon_dependencies(context)
