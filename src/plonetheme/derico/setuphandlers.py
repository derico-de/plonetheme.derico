"""Setup handlers for plonetheme.derico."""

import logging
from pathlib import Path

from plone import api
from plone.base.interfaces import IImagingSchema
from plone.base.interfaces import INonInstallable
from plone.formwidget.namedfile.converter import b64encode_file
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implementer


logger = logging.getLogger(__name__)

#: Plone stores the site logo as base64 bytes, not a resource URL.
LOGO = "derico-logo.svg"

#: Two uploads because named scales cannot art-direct; `sizes` is explicit
#: since the default assumes a non-full-width image. `media` must match
#: HeroMedia.tsx (`<picture>` has no container-query form).
HERO_VARIANTS = {
    "hero-wide": {
        "title": "Hero (wide)",
        "hideInEditor": True,
        "sourceset": [
            {
                "scale": "huge",
                "additionalScales": ["larger", "enormous"],
                "sizes": "100vw",
            }
        ],
    },
    "hero-portrait": {
        "title": "Hero (portrait)",
        "hideInEditor": True,
        "sourceset": [
            {
                "scale": "larger",
                "additionalScales": ["teaser", "great"],
                "media": "(max-width: 55.99rem)",
                "sizes": "100vw",
            }
        ],
    },
}


@implementer(INonInstallable)
class HiddenProfiles:
    """Hide the uninstall and upgrade profiles from the add-ons control panel."""

    def getNonInstallableProfiles(self):
        return [
            "plonetheme.derico:uninstall",
            "plonetheme.derico.upgrades:1017",
            "plonetheme.derico.upgrades:1018",
            "plonetheme.derico.upgrades:1019",
            "plonetheme.derico.upgrades:1020",
            "plonetheme.derico.upgrades:1021",
        ]


def set_site_logo():
    """Set derico's brand mark as site logo unless one is already set."""
    if api.portal.get_registry_record("plone.site_logo", default=None):
        logger.info("plonetheme.derico: site logo already set, leaving it alone")
        return
    path = Path(__file__).parent / "static" / LOGO
    api.portal.set_registry_record(
        "plone.site_logo",
        b64encode_file(LOGO, path.read_bytes()),
    )
    logger.info("plonetheme.derico: site logo set to %s", LOGO)


def ensure_hero_variants():
    """Add the hero's picture variants (a JSONField GS cannot express), add-only."""
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IImagingSchema, prefix="plone", check=False)
    variants = dict(settings.picture_variants or {})
    added = [name for name in HERO_VARIANTS if name not in variants]
    for name in added:
        variants[name] = HERO_VARIANTS[name]
    if added:
        settings.picture_variants = variants
        logger.info("plonetheme.derico: picture variants added: %s", ", ".join(added))


def post_install(context):
    """Run after the default profile is applied."""
    set_site_logo()
    ensure_hero_variants()
