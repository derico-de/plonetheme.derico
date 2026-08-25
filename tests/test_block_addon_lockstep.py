"""Lockstep with `plone.blicca.auroraeditor` (hero ticket 04 §7/§8/§9).

Two things in this package are copies of, or claims about, another package.
Neither fails loudly on its own when it drifts:

1. `bundle-src/build-plugins/scope-wrap.ts` is **vendored** — copied verbatim
   so this repo builds without reaching across a checkout (§7). A vendored file
   is a fork the moment upstream changes and nobody notices.
2. The block record declares a `block_api` **floor** (§8). Declaring more than
   the host provides is a §2.4 mismatch, and a mismatch is a fail-soft skip:
   the block silently vanishes from the slash menu rather than erroring.

Both skip when `plone.blicca.auroraeditor` cannot be found. That is a real
weakness — §9: *"a guard that always skips reads green while protecting
nothing, which is worse than no guard"* — which is why CI checks the package
out for the pytest job. The package is private, so that step needs the
`BLICCA_TOKEN` secret; until it is set these guards skip on CI.
"""

import json
import os
import re
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent

VENDORED = PACKAGE / "bundle-src" / "build-plugins" / "scope-wrap.ts"
REGISTRY = PACKAGE / "src" / "plonetheme" / "derico" / "profiles" / "default" / "registry.xml"

# Everything below this line is upstream's; everything above is this package's
# note about why the copy exists.
SENTINEL = "/* ── upstream begins"


def _blicca():
    """The sibling checkout, by explicit path or by convention.

    `BLICCA_CHECKOUT` exists for CI, where `actions/checkout` refuses to write
    outside the workspace and the sibling convention cannot hold.
    """
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
    """§7 bought independence, not a fork.

    The *code* is upstream's; only the *invocation* differs (this build passes
    three scope roots where the wrapper passes two, because a block's sheet has
    to reach the published page as well). So everything below the sentinel must
    still be byte-identical.
    """
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


@needs_blicca
def test_the_declared_block_api_floor_is_one_the_host_provides():
    """§8: declare the floor, guard the ceiling.

    The record declares the minimum the block actually needs, not the host's
    current version — declaring the host's would let a later bump strand the
    block. Either way the declared value must not EXCEED what the host offers,
    because a mismatch is a fail-soft skip: the block just stops appearing.
    """
    stamp = BLICCA / "src" / "plone" / "blicca" / "auroraeditor" / "static" / "block-api.json"
    assert stamp.is_file(), f"the host's block-api stamp is missing: {stamp}"
    host = json.loads(stamp.read_text())["blockApi"]

    declared = _declared_block_api()
    if declared is None:
        pytest.skip(
            "no block record declares a block_api yet — the record lands with "
            "the server half (hero ticket 09)"
        )

    assert _version(declared) <= _version(host), (
        f"the record declares block_api {declared} but the host provides "
        f"{host}; the block would fail-soft and vanish from the slash menu"
    )


def _declared_block_api():
    if not REGISTRY.is_file():
        return None
    found = re.search(
        r"""block_api["']?\s*[">]*\s*([0-9]+\.[0-9]+)""",
        REGISTRY.read_text(),
    )
    return found.group(1) if found else None


def _version(value):
    return tuple(int(part) for part in str(value).split("."))
