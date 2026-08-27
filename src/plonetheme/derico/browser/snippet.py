"""The Derico Snippet's public renderer.

The generic brand block for the design's static ornaments — today the
Balkenlage divider and the Ständerwerk frame, tomorrow whatever other fixed
markup the Jahresringe language grows. One block, one choice field, because
the snippets differ in nothing but their markup: a block type per ornament
would clone the whole registration stack (record, bundle entry, view, tests)
to express a one-word difference.

The markup itself lives in ``../snippets/*.html``, one file per snippet, and
is the single source both halves inject verbatim: this view reads the file,
and the editor bundle imports the very same file ``?raw`` at build time
(``bundle-src/src/snippet/snippets.ts``). Neither half owns a copy, so the
two surfaces cannot drift — the property the hero buys with element-for-
element template parity, bought here for free by having no elements of its
own at all.

The styling is the theme's, not the block's: ``static/snippets.css``, shipped
as the ``plonetheme-derico-snippets`` bundle rather than through the block
record's ``css`` field. A snippet is pure markup; its stylesheet needs no
build step, so it skips the whole bundle-src pipeline.

The stored ``snippet`` value is untrusted — the block stays authorable
through the API — and is only ever used as a lookup key into the whitelist
below. An unknown or absent key falls back to the Balkenlage: the schema's
own default, and a divider is the least surprising thing a divider block can
render.
"""

from functools import cache
from pathlib import Path

from plone.blicca.auroraeditor.rendering import BaseBlockView


SNIPPETS_DIR = Path(__file__).resolve().parent.parent / "snippets"

#: The whitelist IS the directory listing, pinned at import: a key is valid
#: exactly when its file shipped with the package. Adding a snippet is adding
#: one file here and one choice in ``bundle-src/src/snippet/schema.ts`` —
#: ``tests/test_snippet_view.py`` holds the two lists in lockstep.
SNIPPET_NAMES = frozenset(path.stem for path in SNIPPETS_DIR.glob("*.html"))

DEFAULT_SNIPPET = "balkenlage"


@cache
def snippet_markup(name):
    """The verbatim markup of one shipped snippet.

    Cached forever: the corpus is a handful of package files that change only
    with the package, and the cache is at most one entry per file.
    """
    return SNIPPETS_DIR.joinpath(f"{name}.html").read_text()


class DericoSnippetView(BaseBlockView):
    """Render a ``derico-snippet`` block on the published page."""

    @property
    def markup(self):
        name = (self.data or {}).get("snippet")
        if name not in SNIPPET_NAMES:
            name = DEFAULT_SNIPPET
        return snippet_markup(name)
