"""Drop the retired block_api field."""
import logging

from .base import reload_gs_profile

logger = logging.getLogger(__name__)


def upgrade(context):
    """block_api is retired (ADR 0024 in plone.blicca.auroraeditor); delete the theme's own orphan block_api records if any are left.

    Upgrade from profile version 1020 to 1021.
    """
    logger.info("Running upgrade step: Drop the retired block_api field")
    reload_gs_profile(context)
