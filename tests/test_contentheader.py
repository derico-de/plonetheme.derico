"""derico's values for Clara's content header layout (derico.css §5).

The design's inner pages open with the title on the left and the description
as the lede on the right (`.page-hero__grid`). Clara lays the pair out from
its `--plone-contentheader-*` tokens (architecture §1.7); derico moves two of
them and leaves the rest to Clara. The start page keeps no content header at
all — the Hero opens it — which the §7 chrome rule already guards.
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


def test_description_moves_beside_the_title_on_a_wide_column():
    assert _derico()["--plone-contentheader-column-min"] == "27rem"


def test_the_pair_is_bottom_aligned_like_the_page_hero():
    assert _derico()["--plone-contentheader-align"] == "end"


def test_the_column_gap_is_left_to_clara():
    """The mockup's gap is the `m` step, which is Clara's default already."""
    assert "--plone-contentheader-gap" not in _derico()


@needs_clara
def test_the_tokens_are_read_by_claras_header_rule():
    bundle = css_tools.strip_comments(CLARA_PATH.read_text())
    for name in ("--plone-contentheader-column-min", "--plone-contentheader-align"):
        assert f"var({name})" in bundle, f"Clara's bundle never reads {name}"
