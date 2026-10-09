"""Lockstep with `plone.blicca.auroraeditor`: vendored scope-wrap and `block_api` floor.

Both skip when the Blicca checkout is missing; CI checks it out (needs `BLICCA_TOKEN`).
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


@needs_blicca
def test_the_declared_block_api_floor_is_one_the_host_provides():
    """Declare the floor, not the host's version; a mismatch makes the block vanish.

    Compatible iff same major and host minor >= declared minor (contract §2.3),
    for every record.
    """
    stamp = BLICCA / "src" / "plone" / "blicca" / "auroraeditor" / "static" / "block-api.json"
    assert stamp.is_file(), f"the host's block-api stamp is missing: {stamp}"
    host = json.loads(stamp.read_text())["blockApi"]

    declared = _declared_block_apis()
    if not declared:
        pytest.skip(
            "no block record declares a block_api yet — the record lands with "
            "the server half"
        )

    for floor in declared:
        assert _compatible(floor, host), (
            f"a record declares block_api {floor} but the host provides "
            f"{host}; the block would fail-soft and vanish from the slash menu"
        )


def _declared_block_apis():
    if not REGISTRY.is_file():
        return []
    return re.findall(
        r"""block_api["']?\s*[">]*\s*([0-9]+\.[0-9]+)""",
        REGISTRY.read_text(),
    )


def _compatible(declared, host):
    (major, minor), (host_major, host_minor) = _version(declared), _version(host)
    return major == host_major and minor <= host_minor


def _version(value):
    return tuple(int(part) for part in str(value).split("."))
