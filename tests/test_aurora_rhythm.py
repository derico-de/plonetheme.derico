"""derico's values for Blicca's reading rhythm and type.

The third publisher's contract this sheet fills, and the one with the widest
reach: Blicca's ``blocks_view.css`` dresses every block on the published page
AND the editing canvas from one scale of ``--aurora-*`` tokens. Like the
palette and the promo seam it fails silently in both directions — a
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
    """The frame rules: (selector, {token: value}) for every wrapper-scoped rule.

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
    sheets load in. The `--aurora-*` aliases rest on Blicca's `:where(:root)`.
    """
    declared_on = {
        css_tools.normalise_selector(selector)
        for selector, body in css_tools._blocks(_blicca_sheet())
        if "--aurora-space-block" in body
    }
    assert ":where(:root)" in declared_on, (
        "blocks_view.css no longer declares its scale on `:where(:root)`; "
        f"found it on {sorted(declared_on)}. derico.css's `--aurora-*` aliases can no longer win."
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
#: (not the section step); the frames are the design's
#: section rhythm; the sticky offset is the mockup's `.detail-aside` pin
#: (`--space-l`), read by Blicca at the point of use only.
EXPECTED_ALIASES = {
    "--aurora-content-font-family": "--plone-font-body",
    "--aurora-content-line-height": "--plone-leading-body",
    "--aurora-h2-size": "--plone-text-2xl",
    "--aurora-h3-size": "--clara-text-title",
    "--aurora-h2-leading": "--plone-leading-tight",
    "--aurora-h3-leading": "--plone-leading-tight",
    "--aurora-space-block": "--plone-space-l",
    "--aurora-space-bleed": "--plone-space-xl",
    "--aurora-sticky-offset": "--plone-space-l",
    # the gutter between two grid columns' text boxes: the design's article
    # gap, the one rhythm step it states outside its space scale
    "--aurora-column-gutter": "--derico-article-gap",
    # the text styles: the display face, the
    # lede step and the three inks the mockup sets a kicker, a lede, a byline,
    # a term and a definition in. Copper is reached as Clara's amber-text,
    # which derico.css re-points, so the alias stays a Clara name.
    "--aurora-display-font-family": "--clara-font-display",
    "--aurora-lede-size": "--clara-text-lede",
    "--aurora-text-accent-color": "--clara-amber-text",
    "--aurora-text-soft-color": "--clara-ink-soft",
    "--aurora-text-strong-color": "--clara-brand-deep",
    # the list and quote styles: the hairline between rows, the structural
    # rule a quote stands on, and the thesis and public-code sizes
    "--aurora-divider": "--clara-rule",
    "--aurora-quote-border": "--clara-band-rule",
    "--aurora-quote-statement-size": "--clara-text-title",
    "--aurora-quote-display-size": "--clara-text-heading",
    # the title block's air and its row with the description block (Blicca
    # ADR 0017): the content header's own values, stated once in derico.css
    "--aurora-title-size": "--clara-text-heading",
    "--aurora-title-space-above": "--plone-space-xl",
    "--aurora-title-space-below": "--plone-space-m",
    "--aurora-title-row-threshold": "--plone-contentheader-threshold",
    "--aurora-title-row-gap": "--plone-contentheader-gap",
    "--aurora-title-row-align": "--plone-contentheader-align",
}

#: token -> the literal it states. The one place the rhythm is not an alias: Blicca's
#: 24px view gutter sets every block 24px inside Clara's content header, and
#: the design puts a section's text on the h1's own edge. "None" is not a
#: step, so no token can be aliased for it.
EXPECTED_LITERALS = {
    "--aurora-view-gutter": "0px",
    # the title row's shares: the mockup's 0.9fr/0.75fr as fractions of the
    # row, where Blicca reads a share of the line and Clara a grow factor
    "--aurora-title-row-title-share": "54%",
    "--aurora-title-row-lede-share": "42%",
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


@pytest.mark.parametrize(("token", "value"), sorted(EXPECTED_LITERALS.items()))
def test_the_view_gutter_is_handed_back_to_the_theme(token, value):
    root = _derico_root()
    assert token in root, f"derico.css does not declare {token} on :root"
    assert root[token] == value, f"{token} declares {root[token]!r}, not {value!r}"


def test_the_root_sets_no_rhythm_token_beyond_the_expected_ones():
    """A new token here is a new design claim; name it above."""
    root = {
        name for name in _derico_root()
        if name.startswith("--aurora-") and not name.startswith("--aurora-block-")
    }
    expected = set(EXPECTED_ALIASES) | set(EXPECTED_LITERALS)
    assert root == expected, (
        f"unexpected: {sorted(root - expected)}, "
        f"missing: {sorted(expected - root)}"
    )


@needs_clara
def test_every_alias_points_at_a_token_clara_or_the_scale_defines():
    """A Clara name Clara dropped, or a derico name derico.css never states, is a
    value nothing resolves."""
    clara = css_tools.declarations(CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS)
    own = {name for name in _derico_root() if name.startswith("--derico-")}
    missing = sorted(
        t for t in EXPECTED_ALIASES.values() if t not in clara and t not in own
    )
    assert not missing, f"neither Clara nor derico.css defines {missing}"


# --------------------------------------------------------------------------
# The frames: the hero flush, the band heading, the band's edges and run gap
# --------------------------------------------------------------------------

def _px(step, viewport, props):
    """A `clamp(<rem>, <rem> + <vw>, <rem>)` step in px at a viewport width."""
    value = css_tools.resolve(step, props)
    found = re.fullmatch(
        r"clamp\(\s*([\d.]+)rem\s*,\s*([\d.]+)rem\s*\+\s*([\d.]+)vw\s*,\s*([\d.]+)rem\s*\)",
        value,
    )
    assert found, f"{step} resolves to {value!r}"
    low, base, fluid, high = (float(n) for n in found.groups())
    return min(max(low * 16, base * 16 + fluid * viewport / 100), high * 16)


def _frame(selector_fragment):
    for selector, tokens in _frame_rules():
        if selector_fragment in selector:
            return tokens
    pytest.fail(f"no frame rule matches {selector_fragment!r}")


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


def test_a_grid_is_framed_on_the_section_step():
    """Every article grid in the mockup is a `.section`, padded on `xl`
    (`.sustainability-article .section`); Blicca frames a grid on the
    reading step. Unbanded only: the background rule outranks this one."""
    assert _frame(".block-column_group") == {
        "--aurora-space-block": "var(--plone-space-xl)"
    }


def test_a_colour_change_is_tighter_than_a_same_colour_run():
    """The colour edge separates two bands; inside a run only space does.

    So a band opens and closes on xl, and the gap after a block that shares
    its successor's background is 3xl — wider than the two xl edges either
    side of a colour change.
    """
    tokens = _frame('.block[class*="has--backgroundColor--"]')
    assert tokens == {
        "--aurora-space-block": "var(--plone-space-xl)",
        "--aurora-space-bleed": "var(--plone-space-xl)",
        "--aurora-space-continued": "var(--plone-space-3xl)",
    }


@needs_clara
def test_the_run_gap_is_never_narrower_than_a_colour_change():
    props = css_tools.declarations(CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS)
    props.update(_derico_root())
    for viewport in range(320, 2561, 20):
        edges = 2 * _px("--plone-space-xl", viewport, props)
        gap = _px("--plone-space-3xl", viewport, props)
        assert gap >= edges, f"at {viewport}px: run gap {gap} < colour change {edges}"


def test_a_heading_in_a_run_binds_to_what_follows_it():
    for level in ("h2", "h3", "h4"):
        assert _frame(f".block-{level}.is-background-continued") == {
            "--aurora-space-continued": "var(--plone-space-l)"
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


def test_a_promo_in_a_run_takes_the_band_s_gap():
    """No promo-specific run tokens: the band rule already opens the gap."""
    promo_run = [s for s, _ in _frame_rules() if ".block-promo.is-background" in s]
    assert not promo_run, promo_run


def test_an_unbanded_promo_gets_the_same_step_from_the_frame_token():
    """The other half of the claim: no background reads like one ground.

    Two promos on the white page stand on the same surface as two promos in
    one slot, so they get the same step. It has to come from
    `--aurora-space-frame` rather than from `--aurora-space-block`: Blicca
    reads the latter only for the block types it knows, and an add-on block
    is in none of those lists.
    """
    bare = [tokens for selector, tokens in _frame_rules() if selector == ".block-promo"]
    assert bare, "no frame rule keys on a bare `.block-promo`"
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
