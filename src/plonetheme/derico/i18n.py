"""The theme's message factory, and one correction to Plone's German.

The correction is `locales/de/LC_MESSAGES/widgets.po`: pat-livesearch builds
its summary line as `_t("found") + " " + total + " " + _t("results")` and
plone.app.locales translates BOTH halves as "gefunden", so the German search
panel reads "gefunden 7 gefunden". Shipping the catalog is only half of it —
see below for the other half.
"""
import os

from zope.component import getUtilitiesFor
from zope.i18n.interfaces import ITranslationDomain
from zope.i18nmessageid import MessageFactory


_ = MessageFactory("plonetheme.derico")

#: Where this package's catalogs live on disk. A gettext catalog's identifier
#: in zope.i18n IS its .mo path, which is how ours are told from Plone's.
LOCALES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")


def prefer_this_packages_catalogs(event=None):
    """Move this package's catalogs to the front of every domain it joins.

    `<i18n:registerTranslations>` APPENDS to the domain, and both readers —
    zope.i18n's own `translate()` and plone.app.content's `@@plonejsi18n`,
    which serves the catalog the Mockup patterns translate against — take
    the FIRST catalog that has the message. Plone's ZCML is loaded before
    any add-on's, so a package that ships a correction to a Plone domain is
    registered second and read never. zope.i18n has no ordering knob, and
    the list `getCatalogsInfo()` hands back IS the domain's own, so moving
    ours to the front of it is the whole fix.

    Subscribed to `IDatabaseOpenedWithRoot` (configure.zcml): every
    package's ZCML has been processed by then, and no request has yet warmed
    the RAM cache `@@plonejsi18n` keeps its catalog in.
    """
    prefix = LOCALES + os.sep
    for _name, domain in getUtilitiesFor(ITranslationDomain):
        info = getattr(domain, "getCatalogsInfo", None)
        if info is None:  # a domain that is not a zope.i18n TranslationDomain
            continue
        for names in info().values():
            ours = [name for name in names if str(name).startswith(prefix)]
            if not ours or names[: len(ours)] == ours:
                continue
            names[:] = ours + [name for name in names if name not in ours]
