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

#: The cloud-and-wordmark brand mark. Plone's site logo is a Bytes record
#: holding `filenameb64:…;datab64:…`, not a resource URL, so the file has to be
#: read in and encoded rather than pointed at from registry.xml.
LOGO = "derico-logo.svg"

#: The hero's two crops, as picture variants (hero ticket 05 §3).
#:
#: Two uploads and not one, because Plone's named scales give variants of ONE
#: crop and never art direction — the wide and the portrait framing are
#: different photographs of the same subject, not different sizes of one.
#:
#: `additionalScales` and `sizes` are both given EXPLICITLY. Omitted,
#: `additionalScales` defaults to every other allowed scale, and `sizes`
#: defaults to `(min-width: 576px) {target}px, (min-width: 768px) 600px,
#: 98vw` — which is wrong for a block that is always the full viewport wide.
#:
#: `hideInEditor` on both: picture variants surface as a picker for images
#: placed by hand in the richtext editor, where these two are meaningless.
#: (Blicca's `fullwidth` does not set it, but `fullwidth` is plausibly useful
#: to a hand-placed image; these are not.)
#:
#: The portrait `media` matches `HeroMedia.tsx`'s source query exactly. It is
#: a VIEWPORT query while the hero's layout switch next door is a container
#: query, deliberately: `<picture>` has no container-query form, and the
#: mismatch costs at most a slightly-too-large image for a logged-in author
#: whose canvas is narrower than the viewport by the toolbar.
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
    """Hidden profiles from the Plone add-ons control panel.

    Both the panel and `GET /@addons` build their list the same way
    (`ManageProductsView.marshall_addons`, `plone.restapi`'s `Addons`): every
    EXTENSION profile is offered unless its own id is hidden, or its product
    is. `plonetheme.derico.upgrades:1001` has to be an EXTENSION profile for
    `genericsetup:upgradeDepends` to import it, so without this line the
    add-ons control panel offers it — and applying an upgrade profile by hand
    runs a migration out of order. Found on the sandbox site by hero ticket 19.

    The product route (`getNonInstallableProducts`, which Clara also declares)
    would hide it too, and would keep hiding it for upgrade profiles nobody
    has written yet. It is deliberately NOT taken: it says the same thing a
    second way, and the second way cannot be held to the per-profile line, so
    `test_every_upgrade_profile_is_hidden` would go on passing over a
    `HiddenProfiles` that had quietly stopped naming them. One answer, one
    place; the enumeration in that test is what carries the next
    `plonecli add upgrade_step`.
    """

    def getNonInstallableProfiles(self):
        """Return list of profiles that should not be available for install."""
        return [
            "plonetheme.derico:uninstall",
            "plonetheme.derico.upgrades:1001",
            "plonetheme.derico.upgrades:1002",
            "plonetheme.derico.upgrades:1003",
            "plonetheme.derico.upgrades:1004",
            "plonetheme.derico.upgrades:1005",
            "plonetheme.derico.upgrades:1006",
            "plonetheme.derico.upgrades:1007",
            "plonetheme.derico.upgrades:1008",
            "plonetheme.derico.upgrades:1009",
            "plonetheme.derico.upgrades:1010",
            "plonetheme.derico.upgrades:1011",
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


def ensure_hero_variants():
    """Add the hero's two picture variants, without touching anyone else's.

    `plone.picture_variants` is a JSONField, and GenericSetup has no syntax
    for one — Blicca hit the same wall and adds its `fullwidth` variant from a
    setuphandler for exactly this reason. The companion half of ticket 05's
    imaging setup, the `enormous` scale rung, IS a plain list and rides
    registry.xml with `purge="false"`.

    Add-only and idempotent, on Blicca's `ensure_fullwidth_variant` pattern: a
    variant already present is left alone, so re-running the profile on a live
    site never clobbers an administrator's edit, and no variant this theme did
    not create is ever touched.
    """
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


def uninstall(context):
    """Uninstall script."""
    # Do something on uninstall if needed
    pass
