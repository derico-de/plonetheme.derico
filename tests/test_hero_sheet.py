"""The Derico Hero's stylesheet, pinned on the artifact that actually ships.

Hero ticket 15 settled that the headline's guarantee — text never clips, down
to a 320 viewport — is a LAYOUT rule and not a type rule, and expressed it as
four rungs. Ticket 07 settled two more properties by measurement. All six are
one-line declarations that read as inert housekeeping, which is exactly what
makes them easy to delete: none of them changes anything visible until the
viewport is narrow, the stacking context is contested, or the canvas inherits
the Plate editable's `pre-wrap`. So they are pinned here.

Deliberately declaration-level, never rendering-level. Rung 4 (`hyphens`) is a
labelled enhancement that is a NO-OP in this container's Chromium — it ships no
hyphenation dictionaries, and `de` and `en` probes both failed to hyphenate —
so asserting a wrap would assert the absence of a dictionary. Ticket 15 §4 is
explicit: a test may assert the declaration, never the rendering.

The subject is `static-blocks/*.css`, the built and committed artifact, not
`bundle-src/src/hero/hero.css` — the sheet the browser gets is the one worth
guarding, and it is what `css_tools.block_stylesheets()` globs.
"""

import re

from . import clara_css as css_tools


BLOCK_SHEETS = css_tools.BLOCK_SHEETS
needs_block_sheets = css_tools.needs_block_sheets

ROOT = ".derico-hero"


def _style_rules():
    """(selector-part, properties) for every style rule in every block sheet."""
    for path in BLOCK_SHEETS:
        for selector, body in css_tools.rules(path.read_text()):
            properties = {
                name.strip(): value.strip()
                for name, value in re.findall(r"([-\w]+)\s*:\s*([^;{}]+)", body)
            }
            for part in selector.split(","):
                part = css_tools.normalise_selector(part)
                if part:
                    yield part, properties


def _declares(property_name, value=None):
    """Selector parts declaring `property_name` (optionally with `value`)."""
    return {
        selector
        for selector, properties in _style_rules()
        if property_name in properties
        and (value is None or properties[property_name] == value)
    }


def _values_for(selector, property_name):
    """EVERY value `selector` gives `property_name`, in document order.

    A list rather than a merge: `_blocks` flattens at-rules, so a `@media`
    override arrives under the same selector as the base rule. Merging would
    let a responsive override quietly satisfy an assertion about the base — or
    hide a bad one behind a good one. Asserting over every value avoids
    ranking rules this parser cannot rank.
    """
    return [
        properties[property_name]
        for part, properties in _style_rules()
        if part == selector and property_name in properties
    ]


@needs_block_sheets
def test_no_rule_paints_on_auroras_wrapper_stamp():
    """Hero ticket 08, corrected from 07 by measuring both surfaces.

    Aurora stamps `block-<@type>` on the block WRAPPER, which is the full-bleed
    box on the public view but only the column-width box in the canvas — so a
    hero painted on it clips its own breakout in the editor. The component owns
    `.derico-hero` and both halves emit it; the wrapper stamp is the theme
    layer's to use (`derico.css` §7 hides the chrome above a leading hero with
    it), never a block sheet's.
    """
    offenders = sorted(
        selector
        for selector, _ in _style_rules()
        if "block-derico-hero" in selector
    )
    assert not offenders, (
        "a block sheet may not paint on Aurora's wrapper stamp — the hero "
        f"carries its own `{ROOT}` root on both surfaces: " + ", ".join(offenders)
    )


@needs_block_sheets
def test_every_selector_stays_inside_the_blocks_namespace():
    """The sheet is scope-wrapped, not scoped to the block.

    Packaging wraps the file in `@scope (.aurora-editor, .aurora-editor-portal,
    .aurora-blocks-view)`, which is three whole surfaces — so a bare `h1` here
    would restyle every page the editor renders. Every selector must name a
    class of this block's own: `.derico-hero` for the component (the sidebar
    widgets and the authoring hint live outside it, under `.derico-hero-widget`
    and `.derico-hero-incomplete`, and are namespaced for the same reason).
    """
    strays = sorted(
        selector
        for selector, _ in _style_rules()
        if not re.search(r"\.derico-hero[\w-]*\b", selector)
    )
    assert not strays, (
        "these selectors escape the block's namespace and would style the "
        "whole editor surface: " + ", ".join(strays)
    )


@needs_block_sheets
def test_rung_one_floors_every_grid_and_flex_item():
    """THE guarantee (ticket 15 §1).

    A grid or flex item floors at `min-content`, so without `min-width: 0` the
    copy cell grows to its longest word — measured at 320px inside a 288px
    shell at a 320 viewport — and the hero's `overflow: hidden` clips it. Rung
    2 cannot stand in for this: `overflow-wrap` does not feed intrinsic sizing.
    """
    floored = _declares("min-width", "0")
    for container in ("home-hero__grid", "action-row", "ring-legend"):
        assert f"{ROOT} .{container} > *" in floored, (
            f".{container}'s children are not floored at `min-width: 0`; the "
            "copy cell will grow to its longest word and be clipped"
        )


@needs_block_sheets
def test_rung_two_breaks_a_word_that_cannot_fit():
    """Every text element that can receive an unfittable word (ticket 15 §2)."""
    breaking = _declares("overflow-wrap", "break-word")
    for selector in (
        "h1",
        ".kicker",
        ".lede",
        ".ring-legend dt",
        ".ring-legend dd",
        ".action-row > *",
    ):
        assert f"{ROOT} {selector}" in breaking, (
            f"{selector} does not break an unfittable word"
        )


@needs_block_sheets
def test_rung_three_ramps_the_headline_against_its_container():
    """`cqi`, not `vw` (ticket 15 §3).

    The hero is viewport-minus-toolbar for every logged-in user on BOTH
    surfaces — measured 1220 at a 1440 viewport on the public view too — so a
    `vw` ramp sizes the headline against a box the page does not have, which
    is the 320 clipping defect in miniature.
    """
    ramps = _values_for(f"{ROOT} h1", "font-size")
    assert ramps, "the headline declares no font-size at all"
    for ramp in ramps:
        assert ramp.startswith("clamp("), (
            f"the headline must ramp, and it declares {ramp!r}"
        )
        assert "cqi" in ramp, f"the ramp must be container-relative: {ramp!r}"
        assert "vw" not in ramp, (
            f"a `vw` ramp sizes against a box the page does not have: {ramp!r}"
        )


@needs_block_sheets
def test_rung_three_states_the_clamp_rather_than_redefining_the_alias():
    """`--derico-text-display` is not the hero's to redefine (ticket 15 §3).

    It meant "Clara's display size" and Clara's own consumers read it, so the
    hero states one design's voice locally instead. That decision is why the
    alias is no longer published at all — `derico.css` §3 publishes three.
    """
    for selector, properties in _style_rules():
        assert "--derico-text-display" not in properties, (
            f"{selector} redefines an alias that belongs to the type layer"
        )


@needs_block_sheets
def test_rung_four_labels_the_enhancement():
    """Declaration only — never a rendering claim (ticket 15 §4)."""
    assert _declares("hyphens", "auto"), (
        "rung 4 is gone; it is a no-op in this container's Chromium but it is "
        "the difference between a break and a syllable break where a "
        "dictionary exists"
    )


@needs_block_sheets
def test_the_hero_owns_a_stacking_context():
    """Ticket 07, measured in the live canvas.

    `container-type: inline-size` does NOT supply a stacking context, and
    without one the `z-index: -2` hero media falls behind the hero's own opaque
    ground and the photograph disappears.
    """
    assert ROOT in _declares("isolation", "isolate"), (
        "the hero must isolate; without a stacking context the z-index: -2 "
        "media falls behind the hero's own ground and the photograph vanishes"
    )


@needs_block_sheets
def test_the_hero_states_how_it_wraps():
    """Ticket 07/08: parity comes from stating the value, not from which value.

    The Plate editable computes `white-space: pre-wrap` and it inherits into
    the canvas, so a hero that says nothing wraps its headline differently in
    the editor than on the page.
    """
    assert ROOT in _declares("white-space", "normal"), (
        "the hero must state `white-space`, or the canvas inherits the Plate "
        "editable's `pre-wrap` and wraps differently from the public view"
    )
