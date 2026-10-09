"""Lockstep with `plone.blicca.auroraeditor`: vendored scope-wrap, and the
name check that replaced the `block_api` counter (ADR 0024 in the editor).

Both groups skip when the Blicca checkout is missing; CI checks it out (needs
`BLICCA_TOKEN`).
"""
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent

VENDORED = PACKAGE / "bundle-src" / "build-plugins" / "scope-wrap.ts"
BLOCKS_DIR = PACKAGE / "src" / "plonetheme" / "derico" / "static-blocks"
BLOCKS = {
    "plonetheme.derico.hero": BLOCKS_DIR / "hero.js",
    "plonetheme.derico.pageheader": BLOCKS_DIR / "pageheader.js",
}

# Everything below this line is upstream's; everything above is this package's
# note about why the copy exists.
SENTINEL = "/* ── upstream begins"


def _blicca():
    """The sibling checkout, by explicit path or by convention.

    `BLICCA_CHECKOUT` exists for CI, where `actions/checkout` refuses to write
    outside the workspace and the sibling convention cannot hold.
    """
    import os

    explicit = os.environ.get("BLICCA_CHECKOUT")
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.append(PACKAGE.parent / "plone.blicca.auroraeditor")
    for candidate in candidates:
        if (candidate / "wrapper").is_dir():
            return candidate
    return None


BLICCA = _blicca()

needs_blicca = pytest.mark.skipif(
    BLICCA is None,
    reason=(
        "plone.blicca.auroraeditor is not checked out beside this package; "
        "set BLICCA_CHECKOUT to point at it"
    ),
)


def _below_sentinel(text):
    start = text.index(SENTINEL)
    return text[start + text[start:].index("\n") + 1 :]


@needs_blicca
def test_the_vendored_scope_wrap_still_matches_upstream():
    """Only the invocation differs; the code below the sentinel must be byte-identical."""
    upstream = BLICCA / "wrapper" / "build-plugins" / "scope-wrap.ts"
    assert upstream.is_file(), f"upstream plugin is missing: {upstream}"

    vendored = VENDORED.read_text()
    assert SENTINEL in vendored, (
        f"the sentinel line is gone from {VENDORED.name}; without it there is "
        "no boundary between this package's note and upstream's code"
    )
    assert _below_sentinel(vendored) == upstream.read_text(), (
        f"{VENDORED.name} has drifted from upstream. Re-copy it (and update "
        "the commit named in its header), or the vendored copy is a silent fork"
    )


def test_no_record_declares_block_api():
    """block_api left `IAuroraBlockAddon` (ADR 0024); nothing should resurrect it.

    Every `registry.xml` in this package, including old upgrade steps: a site
    upgrading through an old step would otherwise hit the same `KeyError`.
    """
    registries = list(PACKAGE.glob("src/**/registry.xml"))
    assert registries, "no registry.xml found to check"
    for path in registries:
        assert "block_api" not in path.read_text(), path


@needs_blicca
@pytest.mark.parametrize("name", sorted(BLOCKS))
def test_the_bundle_passes_the_hosts_name_check(name):
    """Compatibility is the set of names a bundle imports (ADR 0024), checked
    against the names the host's committed facades export."""
    from plone.blicca.auroraeditor import namecheck

    stamp = BLICCA / "src" / "plone" / "blicca" / "auroraeditor" / "static" / "block-api.json"
    assert stamp.is_file(), f"the host's block-api stamp is missing: {stamp}"
    exports = namecheck.load_exports(stamp)

    bundle = BLOCKS[name]
    assert bundle.is_file(), f"{name}'s bundle is missing: {bundle}"
    check = namecheck.check_bundle(bundle, exports)
    assert not check.missing, (
        f"{name}'s bundle imports names the host does not export: "
        f"{namecheck.describe(check.missing)}"
    )
