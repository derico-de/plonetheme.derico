"""derico's values for Blicca's reading rhythm and type (derico.css §10, §11).

The third publisher's contract this sheet fills, and the one with the widest
reach: Blicca's ``blocks_view.css`` dresses every block on the published page
AND the editing canvas from one scale of ``--aurora-*`` tokens. Like the
palette (§8) and the promo seam (§9) it fails silently in both directions — a
token Blicca renamed leaves derico's value read by nobody, a name derico
misspells sets nothing — so these tests hold the two sheets to each other.

Blicca's half is read from the package rather than restated: the token names
come out of its stylesheet, the run-marker classes out of its renderer.
"""

import re
from pathlib import Path

import pytest

from . import clara_css as css_tools


DERICO = css_tools.DERICO_CSS.read_text()

try:
    from plone.blicca.auroraeditor.browser.rendering import plate as blicca_plate
except ImportError:  # pragma: no cover - the theme's floor makes this unlikely
    blicca_plate = None

needs_blicca = pytest.mark.skipif(
    blicca_plate is None, reason="plone.blicca.auroraeditor is not importable"
)

CLARA_PATH = css_tools.clara_bundle_path()
needs_clara = pytest.mark.skipif(
    CLARA_PATH is None, reason="plonetheme.clara's compiled bundle is not available"
)


def _blicca_sheet():
    return (
        Path(blicca_plate.__file__).parent / "static" / "blocks_view.css"
    ).read_text()


def _blicca_tokens():
    """Every `--aurora-*` token blocks_view.css declares on the root...

    ...plus the ones it only READS, as `var(--aurora-x, <fallback>)` at the
    point of use. A token whose default is "whatever this element's frame is"
    cannot be declared on the root — declared there it would resolve against
    the ROOT's frame and inherit that number down, past every block that
    scopes its own — so `--aurora-space-continued` exists only in the rule
    that reads it. Read is as good as declared for this test's purpose: the
    question is whether derico's value reaches anything.
    """
    declared = set(
        css_tools.declarations(
            _blicca_sheet(), (":where(:root)", ":root", "body")
        )
    )
    read = set(re.findall(r"var\(\s*(--aurora-[\w-]+)", _blicca_sheet()))
    return declared | read


def _derico_root():
    return css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS)


def _frame_rules():
    """The §11 rules: (selector, {token: value}) for every wrapper-scoped rule.

    Keyed on `.block`, not on `.block-`: a rule may name the background slot
    alone (`.block[class*="has--backgroundColor--"]`), which is the frame that
    belongs to a band rather than to any one block type.
    """
    rules = []
    for selector, body in css_tools._blocks(DERICO):
        selector = css_tools.normalise_selector(selector)
        if not selector.startswith(".block"):
            continue
        found = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;}]+)", body))
        rules.append((selector, {k: v.strip() for k, v in found.items()}))
    return rules


def _rhythm_tokens_derico_sets():
    root = {
        name for name in _derico_root()
        if name.startswith("--aurora-") and not name.startswith("--aurora-block-")
    }
    for _, tokens in _frame_rules():
        root.update(tokens)
    return root


# --------------------------------------------------------------------------
# The names: every token derico sets is one Blicca declares
# --------------------------------------------------------------------------

@needs_blicca
def test_every_rhythm_token_the_theme_sets_is_one_blicca_declares():
    """A name Blicca never declares is a value nothing reads."""
    unknown = sorted(_rhythm_tokens_derico_sets() - _blicca_tokens())
    assert not unknown, (
        f"derico.css sets {unknown}, which blocks_view.css does not declare"
    )


@needs_blicca
def test_blicca_declares_its_scale_at_zero_specificity():
    """The reason a plain `:root` rule here can win at all.

    A `body { }` declaration in Blicca would beat derico's `:root` on every
    element below body — which is every block — no matter the order the two
    sheets load in. §10 rests on Blicca's `:where(:root)`.
    """
    declared_on = {
        css_tools.normalise_selector(selector)
        for selector, body in css_tools._blocks(_blicca_sheet())
        if "--aurora-space-block" in body
    }
    assert ":where(:root)" in declared_on, (
        "blocks_view.css no longer declares its scale on `:where(:root)`; "
        f"found it on {sorted(declared_on)}. derico.css §10 can no longer win."
    )


@needs_blicca
def test_the_run_markers_the_frame_rules_key_on_are_blicca_s():
    """`is-background-continuation` / `-continued` come out of the renderer."""
    source = Path(blicca_plate.__file__).read_text()
    for selector, _ in _frame_rules():
        for marker in re.findall(r"is-background-[\w-]+", selector):
            assert marker in source, (
                f"{selector!r} keys on {marker!r}, which plate.py never stamps"
            )


# --------------------------------------------------------------------------
# The values: aliases of the theme's own steps, not a second scale
# --------------------------------------------------------------------------

#: token -> the step it must alias verbatim. The face and leadings are
#: Clara's; the heading steps are the design's prose and component headings
#: (derico.css §10 says why not the section step); the frames are §5's
#: section rhythm.
EXPECTED_ALIASES = {
    "--aurora-content-font-family": "--plone-font-body",
    "--aurora-content-line-height": "--plone-leading-body",
    "--aurora-h2-size": "--plone-text-2xl",
    "--aurora-h3-size": "--clara-text-title",
    "--aurora-h2-leading": "--plone-leading-tight",
    "--aurora-h3-leading": "--plone-leading-tight",
    "--aurora-space-block": "--plone-space-l",
    "--aurora-space-bleed": "--plone-space-xl",
}


@pytest.mark.parametrize(("token", "target"), sorted(EXPECTED_ALIASES.items()))
def test_each_root_token_aliases_a_step_rather_than_restating_a_value(
    token, target
):
    root = _derico_root()
    assert token in root, f"derico.css does not declare {token} on :root"
    assert re.fullmatch(rf"var\(\s*{re.escape(target)}\s*\)", root[token]), (
        f"{token} must alias {target} verbatim; it declares {root[token]!r}"
    )


def test_the_root_sets_no_rhythm_token_beyond_the_expected_ones():
    """A new token here is a new design claim; name it above."""
    root = {
        name for name in _derico_root()
        if name.startswith("--aurora-") and not name.startswith("--aurora-block-")
    }
    assert root == set(EXPECTED_ALIASES), (
        f"unexpected: {sorted(root - set(EXPECTED_ALIASES))}, "
        f"missing: {sorted(set(EXPECTED_ALIASES) - root)}"
    )


@needs_clara
def test_every_alias_points_at_a_token_clara_defines():
    clara = css_tools.declarations(CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS)
    missing = sorted(t for t in EXPECTED_ALIASES.values() if t not in clara)
    assert not missing, f"Clara no longer defines {missing}"


# --------------------------------------------------------------------------
# The frames (§11): the hero flush, the band heading, the promo's section air
# --------------------------------------------------------------------------

def _frame(selector_fragment):
    for selector, tokens in _frame_rules():
        if selector_fragment in selector:
            return tokens
    pytest.fail(f"no §11 rule matches {selector_fragment!r}")


def test_the_hero_wrapper_carries_no_bleed_frame():
    """Nothing between the photograph and the band beneath it (mockup)."""
    assert _frame(".block-derico-hero") == {"--aurora-space-bleed": "0px"}


def test_a_heading_that_opens_a_band_is_the_section_step():
    tokens = _frame(".block-h2[class*=\"has--backgroundColor--\"]")
    assert tokens == {"--aurora-h2-size": "var(--clara-text-heading)"}
    # ...and only the OPENER: a continuation heading keeps the prose step
    selector = next(
        s for s, _ in _frame_rules() if ".block-h2" in s
    )
    assert ":not(.is-background-continuation)" in selector


def test_a_background_run_opens_and_closes_on_the_section_step():
    """A band is a section, so it is framed like one.

    Blicca pads every block in a run from the same frame at both ends, which
    makes the band's outer air and the gaps between its blocks one number.
    The frame moves to §5's section step and the run's inner gaps are pinned
    back to the §10 reading step, so the band opens and closes on 2xl and
    still breathes on l inside.
    """
    tokens = _frame('.block[class*="has--backgroundColor--"]')
    assert tokens == {
        "--aurora-space-block": "var(--plone-space-2xl)",
        "--aurora-space-bleed": "var(--plone-space-2xl)",
        "--aurora-space-continued": "var(--plone-space-l)",
    }


@needs_blicca
def test_blicca_reads_the_inner_gap_at_its_point_of_use():
    """The reason `--aurora-space-continued` is not on Blicca's root.

    Declared on `:where(:root)` with a `var(--aurora-space-block)` default it
    would resolve against the ROOT's frame and inherit that number down, so
    the rule above would raise the band's frame and leave its inner gaps at
    the old value — the whole point of the token, silently lost. It only
    works read at the point of use, with the frame as the fallback.
    """
    sheet = re.sub(r"\s+", "", _blicca_sheet())
    assert "--aurora-space-continued:" not in sheet, (
        "blocks_view.css now DECLARES --aurora-space-continued; a root "
        "declaration cannot fall back to a frame the block scopes itself"
    )
    assert (
        "padding-block-end:var(--aurora-space-continued,"
        "var(--aurora-space-block))"
    ) in sheet, "the run's inner gap no longer falls back to the block frame"
    assert (
        "padding-block-end:var(--aurora-space-continued,"
        "var(--aurora-space-bleed))"
    ) in sheet, "a full-bleed run's inner gap no longer falls back to bleed"


def test_a_promo_sharing_a_band_breathes_on_the_xl_step_both_sides():
    """The user-facing claim: same background -> big space, both sides.

    Both of the promo's INNER edges — the gap to the block above it in the
    run (`continuation`) and the gap to the one below (`continued`). The
    run's outer frame is the band's, and is asserted separately.
    """
    tokens = _frame(".block-promo.is-background-continuation")
    assert tokens == {
        "--aurora-space-continuation": "var(--plone-space-xl)",
        "--aurora-space-continued": "var(--plone-space-xl)",
    }
    selector = next(s for s, _ in _frame_rules() if ".block-promo" in s)
    assert ".block-promo.is-background-continued" in selector, (
        "the first promo of a same-background pair must get the step too, "
        "or the pair is asymmetric"
    )


@needs_clara
def test_the_shared_band_step_is_at_least_three_rem():
    """The floor the spec named: 3rem top and bottom."""
    props = css_tools.declarations(CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS)
    props.update(_derico_root())
    value = css_tools.resolve("--plone-space-xl", props)
    assert value is not None
    floor = re.match(r"clamp\(\s*([\d.]+)rem", value)
    assert floor and float(floor.group(1)) >= 3, value


def test_an_unbanded_promo_gets_the_same_step_from_the_frame_token():
    """The other half of the claim: no background reads like one ground.

    Two promos on the white page stand on the same surface as two promos in
    one slot, so they get the same step. It has to come from
    `--aurora-space-frame` rather than from `--aurora-space-block`: Blicca
    reads the latter only for the block types it knows, and an add-on block
    is in none of those lists.
    """
    bare = [tokens for selector, tokens in _frame_rules() if selector == ".block-promo"]
    assert bare, "no §11 rule keys on a bare `.block-promo`"
    assert bare == [{"--aurora-space-frame": "var(--plone-space-xl)"}], (
        "the bare .block-promo rule must carry the frame and nothing else"
    )


@needs_blicca
def test_the_frame_token_is_read_under_every_background_rule():
    """Why the frame rule needs no `:not([background])`: it cannot double.

    Blicca reads `--aurora-space-frame` on the bare `.block`, which every
    background and full-width rule outranks — so a banded promo keeps its
    band's frame and an unbanded one is the only reader.
    """
    sheet = _blicca_sheet()
    readers = [
        css_tools.normalise_selector(selector)
        for selector, body in css_tools._blocks(sheet)
        if "--aurora-space-frame" in body and "padding" in body
    ]
    assert readers == [":is(.aurora-blocks-view, [data-slate-editor]) .block"], (
        f"blocks_view.css reads the frame token from {readers}; the theme's "
        "rule assumes the weakest possible one"
    )
