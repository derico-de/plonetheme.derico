"""Register the copper block background."""
import logging

from .base import reload_gs_profile

logger = logging.getLogger(__name__)


def upgrade(context):
    """A custom upgrade step

    Upgrade from profile version 1024 to 1025.
    """
    logger.info("Running upgrade step: Register the copper block background")
    reload_gs_profile(context)
