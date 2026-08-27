"""derico's fragment corpus, published for the generic fragment block.

``collective.fragmentsblock`` renders *fragments* — static design markup an
add-on ships as files — into any Aurora-edited page. This module makes the
theme the first provider, over the corpus it already keeps: the very
``snippets/`` directory the Derico Snippet block reads. One corpus, one
file per ornament, now reachable through either block.

The editor half of the same registration lives in
``bundle-src/src/fragments/index.tsx``, which imports those files ``?raw``
and publishes them into ``@plone/registry``. Neither half owns a copy — the
same property the Derico Snippet buys, extended to a second reader.

Adding a fragment stays what it was: one file in ``snippets/``, one entry
in the editor's map. Nothing here needs touching; the provider is the
directory.
"""

from pathlib import Path

from collective.fragmentsblock.fragments import FragmentsFolder


#: The shared corpus. ``browser/snippet.py`` reads the same directory for
#: the Derico Snippet block; ``tests/test_fragments.py`` holds the two
#: readers and the editor's map in lockstep.
FRAGMENTS_DIR = Path(__file__).resolve().parent / "snippets"

#: Registered as a named ``IFragmentsProvider`` utility in configure.zcml.
#: The name is the package's, so a second provider in another add-on sorts
#: deterministically against it (ids share one site-wide namespace).
provider = FragmentsFolder(FRAGMENTS_DIR)
