"""Setup handlers for plonetheme.derico."""

import logging
from pathlib import Path

from plone import api
from plone.base.interfaces import INonInstallable
from plone.formwidget.namedfile.converter import b64encode_file
from zope.interface import implementer


logger = logging.getLogger(__name__)

#: The cloud-and-wordmark brand mark. Plone's site logo is a Bytes record
#: holding `filenameb64:…;datab64:…`, not a resource URL, so the file has to be
#: read in and encoded rather than pointed at from registry.xml.
LOGO = "derico-logo.svg"


@implementer(INonInstallable)
class HiddenProfiles:
    """Hidden profiles from the Plone add-ons control panel."""

    def getNonInstallableProfiles(self):
        """Return list of profiles that should not be available for install."""
        return [
            "plonetheme.derico:uninstall",
        ]


def set_site_logo():
    """Point plone.site_logo at derico's brand mark.

    Identity, not styling: the one part of the design that cannot be a token.
    An existing logo is left alone, so re-running the profile on a live site
    never clobbers an editor's upload.
    """
    if api.portal.get_registry_record("plone.site_logo", default=None):
        logger.info("plonetheme.derico: site logo already set, leaving it alone")
        return
    path = Path(__file__).parent / "static" / LOGO
    api.portal.set_registry_record(
        "plone.site_logo",
        b64encode_file(LOGO, path.read_bytes()),
    )
    logger.info("plonetheme.derico: site logo set to %s", LOGO)


def post_install(context):
    """Run after the default profile is applied."""
    set_site_logo()


def uninstall(context):
    """Uninstall script."""
    # Do something on uninstall if needed
    pass
