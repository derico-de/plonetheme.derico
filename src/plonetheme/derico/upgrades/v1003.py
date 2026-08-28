"""Register derico as a fragment provider.

Narrowed to the one thing profile version 1003 changed: registry.xml grew
the ``plonetheme.derico.fragments`` record, which loads the bundle that
publishes the ``snippets/`` corpus as fragments for
``collective.fragmentsblock``'s generic fragment block.

The new profile dependency on ``collective.fragmentsblock:default`` is not
run from here: GenericSetup applies dependency profiles on install, not on
upgrade. The record is harmless meanwhile — a bundle nothing reads. Version
1005 installs the add-on for those sites, once 1004 made the missing block
a defect rather than an inconvenience.
"""

import logging


logger = logging.getLogger(__name__)

PROFILE = "profile-plonetheme.derico:default"


def upgrade(context):
    """Upgrade from profile version 1002 to 1003."""
    logger.info("Running upgrade step: Register derico as a fragment provider")
    context.runImportStepFromProfile(PROFILE, "plone.app.registry")
