"""Install the Derico Snippet brand block.

Narrowed to the one thing profile version 1002 changed: registry.xml grew the
snippet's ``IAuroraBlockAddon`` record and the ``plonetheme-derico-snippets``
stylesheet bundle. Everything else the block needs was already on a 1001 site
— the insert permission and its rolemap grant, the Blicca host, the browser
layer — and the snippet markup, its view and its stylesheet are code, which
arrives with the package rather than with an import step.
"""

import logging


logger = logging.getLogger(__name__)

PROFILE = "profile-plonetheme.derico:default"


def upgrade(context):
    """Upgrade from profile version 1001 to 1002."""
    logger.info("Running upgrade step: Install the Derico Snippet brand block")
    context.runImportStepFromProfile(PROFILE, "plone.app.registry")
