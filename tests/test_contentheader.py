"""derico's values for Clara's content header layout (derico.css §5).

The design's inner pages open with the title on the left and the description
as the lede on the right (`.page-hero__grid`). Clara lays the pair out from
its `--plone-contentheader-*` tokens (architecture §1.7); derico moves two of
them and leaves the rest to Clara. A blocks page prints the pair from its own
tree since Blicca's ADR 0017, and §10 aliases these same tokens to Blicca's
title row, so the page hero is stated once for both markups
(tests/test_aurora_rhythm.py holds the aliases).
"""

import pytest

from . import clara_css as css_tools


DERICO = css_tools.DERICO_CSS.read_text()
CLARA_PATH = css_tools.clara_bundle_path()
needs_clara = pytest.mark.skipif(
    CLARA_PATH is None, reason="plonetheme.clara's compiled bundle is not available"
)


def _derico():
    return css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS)


def test_description_moves_beside_the_title_from_the_mockups_switch():
    assert _derico()["--plone-contentheader-threshold"] == "56rem"


def test_the_title_takes_the_wider_half():
    """The mockup's `minmax(0, 0.9fr) minmax(22rem, 0.75fr)`."""
    assert _derico()["--plone-contentheader-title-grow"] == "0.9"
    assert _derico()["--plone-contentheader-description-grow"] == "0.75"


def test_the_pair_is_bottom_aligned_like_the_page_hero():
    assert _derico()["--plone-contentheader-align"] == "end"


def test_the_description_parks_at_the_far_edge():
    assert _derico()["--plone-contentheader-justify"] == "space-between"


def test_the_column_gap_is_left_to_clara():
    """The mockup's gap is the `m` step, which is Clara's default already."""
    assert "--plone-contentheader-gap" not in _derico()


@needs_clara
def test_the_tokens_are_read_by_claras_header_rule():
    bundle = css_tools.strip_comments(CLARA_PATH.read_text())
    for name in (
        "--plone-contentheader-threshold",
        "--plone-contentheader-align",
        "--plone-contentheader-justify",
        "--plone-contentheader-title-grow",
        "--plone-contentheader-description-grow",
    ):
        assert f"var({name})" in bundle, f"Clara's bundle never reads {name}"
