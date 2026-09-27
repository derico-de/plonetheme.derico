"""derico's fragment corpus, published for the generic fragment block.

``collective.fragmentsblock`` renders *fragments* — static design markup an
add-on ships as files — into any Aurora-edited page. This module makes the
theme the first provider, over the corpus it keeps in ``snippets/``: one
file per ornament.

The editor half of the same registration lives in
``bundle-src/src/fragments/index.tsx``, which imports those files ``?raw``
and publishes them into ``@plone/registry``. Neither half owns a copy.

Adding a fragment stays what it was: one file in ``snippets/``, one entry
in the editor's map. Nothing here needs touching; the provider is the
directory.
"""

from pathlib import Path

from collective.fragmentsblock.fragments import FragmentsFolder


#: The shared corpus. ``tests/test_fragments.py`` holds this provider and
#: the editor's map in lockstep.
FRAGMENTS_DIR = Path(__file__).resolve().parent / "snippets"

#: Registered as a named ``IFragmentsProvider`` utility in configure.zcml.
#: The name is the package's, so a second provider in another add-on sorts
#: deterministically against it (ids share one site-wide namespace).
provider = FragmentsFolder(FRAGMENTS_DIR)
