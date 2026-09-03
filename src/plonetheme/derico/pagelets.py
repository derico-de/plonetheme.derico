"""derico's page-tail contact band: the design's „Erstgespräch vereinbaren".

One element of the whole-body layout, placed directly before the footer rows
(profiles/default/viewlets.xml), so it closes every page the way the mockup
closes every page — after the content, after Clara's sub-navigation, above the
footer (docs/design/derico.de/site/de/index.html, `section.contact-band`).

A chrome pagelet rather than a brand block, because it is not authored: the
design shows the same band on all 22 mockup pages, and an author who had to
place it would eventually forget one. That is also why it renders
unconditionally — no gate, no per-page opt-out.

The two links are the only thing about it that a site owns, so neither is
written into the markup:

* the call to action resolves `plonetheme.derico.contact_page`, a path
  relative to the NAVIGATION ROOT — a language folder is a navigation root, so
  one record serves a de/ and an en/ tree without knowing they exist. An empty
  record, a path that does not resolve and a path the visitor may not see all
  come out the same way: no button, band unchanged.
* the mail address is Plone's own `plone.email_from_address`. A theme that
  shipped its author's address would mail derico from every site that ever
  installed it.

The button is dropped on the target page itself. A call to action pointing at
the page it is printed on is not a call to anything, and the mail link still
gives the band something to do there.

Copy is translatable (templates/contact.pt, locales/), German included: the
design is written in German, the i18n domain speaks English, and the site
decides which one a visitor gets.
"""

import logging

from Acquisition import aq_base
from plone import api
from plone.pageletlayout.chrome import ChromePagelet
from zope.component import getMultiAdapter


logger = logging.getLogger(__name__)

#: Path to the site's contact page, relative to the navigation root.
#: Declared in profiles/default/registry.xml; `contact` is the id the Plone
#: distribution's own starter contact page ships with.
CONTACT_PAGE_RECORD = "plonetheme.derico.contact_page"

#: Plone's site-wide sender address, reused as the band's mail link.
EMAIL_RECORD = "plone.email_from_address"


class ContactBandChromePagelet(ChromePagelet):
    """The contact band: heading, one sentence, a call to action and a mail link."""

    def update(self):
        self.contact_url = self._contact_url()
        self.email = (api.portal.get_registry_record(EMAIL_RECORD, default="") or "").strip()

    def _contact_url(self):
        """The contact page's URL, or '' when there is nothing to link to."""
        path = (
            api.portal.get_registry_record(CONTACT_PAGE_RECORD, default="") or ""
        ).strip().strip("/")
        if not path:
            return ""
        state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        try:
            target = state.navigation_root().restrictedTraverse(path, None)
        except Exception:  # noqa: BLE001 - a bad record must not break the page
            logger.warning("contact band: %r does not resolve", path)
            return ""
        if target is None:
            return ""
        if aq_base(target) is aq_base(self.context):
            return ""
        return target.absolute_url()
