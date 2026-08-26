"""Install the Derico Hero brand block.

Narrowed to the four things profile version 1001 actually changed, rather
than reloading the whole default profile. A blanket reload would also re-run
`browserlayer`, `catalog` and the bundle records — harmless today, but it
makes the step's blast radius the whole profile forever, and the next reader
cannot tell which part of it this upgrade was for.

Fresh installs need none of this: GenericSetup applies the default profile
end to end and `post_install` runs. This step exists for the sites that
already have derico at 1000, where the theme was a token layer and there was
no brand block at all.
"""

import logging

from plone import api

from ..setuphandlers import ensure_hero_variants


logger = logging.getLogger(__name__)

PROFILE = "profile-plonetheme.derico:default"

#: The editor the brand blocks mount in, and the Python package this theme's
#: renderer imports its promised API from. New in 1001 as a GS dependency: a
#: Python dependency does not install a profile, and a GS dependency only
#: affects FRESH installs — so without this an already-installed site would
#: get the block record with no Blicca behind it to read it.
HOST = "plone.blicca.auroraeditor"


def upgrade(context):
    """Upgrade from profile version 1000 to 1001."""
    logger.info("Running upgrade step: Install the Derico Hero brand block")

    installer = api.addon.get_installer(api.portal.get())
    if not installer.is_product_installed(HOST):
        logger.info("plonetheme.derico: installing %s", HOST)
        installer.install_product(HOST)

    # registry.xml — the IAuroraBlockAddon record and the `enormous` scale
    # rung. The rung merges rather than replaces (`purge="false"`), so
    # re-running this never disturbs a ladder someone has since extended.
    context.runImportStepFromProfile(PROFILE, "plone.app.registry")

    # rolemap.xml — `plonetheme.derico: Insert Brand Block`, the insert gate.
    context.runImportStepFromProfile(PROFILE, "rolemap")

    # `plone.picture_variants` is a JSONField and has no import step to run:
    # GenericSetup has no syntax for one, so the two hero variants come from
    # the same add-only handler `post_install` calls.
    ensure_hero_variants()
