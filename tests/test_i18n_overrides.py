"""The one place this theme corrects Plone's own translations.

pat-livesearch renders its summary line as
``_t("found") + " " + total + " " + _t("results")`` (mockup
src/pat/livesearch/livesearch.js) and plone.app.locales translates BOTH
halves of it as "gefunden", so the German search panel read
"gefunden 7 gefunden". `locales/de/LC_MESSAGES/widgets.po` corrects the two
msgids; `i18n.prefer_this_packages_catalogs` is what makes them win.

Every claim here fails in silence without a test: a `.po` edited without
recompiling, a msgid that quietly shadows another Plone string, and above
all the catalog ORDER, where the correction is loaded, registered, correct —
and never read.
"""

import os
import re
from pathlib import Path

from zope.component import getUtility
from zope.i18n import translate
from zope.i18n.interfaces import ITranslationDomain

from plonetheme.derico import i18n


LOCALES = Path(i18n.LOCALES)
PO = LOCALES / "de" / "LC_MESSAGES" / "widgets.po"
MO = LOCALES / "de" / "LC_MESSAGES" / "widgets.mo"
CONFIGURE = Path(i18n.__file__).parent / "configure.zcml"

#: What the pattern's two halves must say. `Treffer` is the same word in the
#: singular, which this line needs: pat-livesearch has no plural form and
#: renders one string for one result and for seven.
EXPECTED = {"found": "Gefunden:", "results": "Treffer"}


#: `msgid "x"` / `msgstr "y"` pairs, header entry (an empty msgid) dropped.
_ENTRY = re.compile(r'^msgid "(.+)"\n^msgstr "(.*)"$', re.M)


def _po_catalog():
    return dict(_ENTRY.findall(PO.read_text(encoding="utf-8")))


class TestTheCatalogOnDisk:

    def test_the_source_catalog_is_where_the_theme_keeps_its_translations(self):
        """`.mo` is a build artifact here — the instance compiles it at
        startup (`zope_i18n_compile_mo_files`, the same setting the test
        layer sets), and .gitignore keeps compiled catalogs out of the
        repository. The `.po` is the file that ships."""
        assert PO.is_file(), f"{PO} is missing"
        assert MO.parent == PO.parent, "the two must sit in the same directory"

    def test_it_corrects_the_summary_line_and_nothing_else(self):
        """A catalog in a Plone domain shadows every msgid it names."""
        assert _po_catalog() == EXPECTED

    def test_the_line_reads_as_German_for_one_result_and_for_many(self):
        catalog = _po_catalog()

        def line(total):
            return f"{catalog['found']} {total} {catalog['results']}"

        assert line(1) == "Gefunden: 1 Treffer"
        assert line(7) == "Gefunden: 7 Treffer"


class TestTheCatalogWins:
    """Shipping it is half; being READ is the other half."""

    def test_the_reorder_runs_at_startup(self):
        """Registered on IDatabaseOpenedWithRoot: after every package's ZCML."""
        zcml = CONFIGURE.read_text()
        assert "zope.processlifetime.IDatabaseOpenedWithRoot" in zcml
        assert ".i18n.prefer_this_packages_catalogs" in zcml

    def test_this_packages_catalogs_come_first(self, integration):
        """`registerTranslations` appends; the first catalog with the message
        is the one both readers take."""
        i18n.prefer_this_packages_catalogs()
        domain = getUtility(ITranslationDomain, "widgets")
        catalogs = domain.getCatalogsInfo()["de"]
        assert len(catalogs) > 1, (
            "Plone's own German widgets catalog is not registered here, so "
            "this test proves nothing about order any more"
        )
        assert str(catalogs[0]).startswith(str(LOCALES) + os.sep), (
            f"this package's catalog is not first: {catalogs}"
        )

    def test_the_summary_line_translates_to_ours(self, integration):
        i18n.prefer_this_packages_catalogs()
        for msgid, msgstr in EXPECTED.items():
            assert translate(msgid, domain="widgets", target_language="de") == msgstr
