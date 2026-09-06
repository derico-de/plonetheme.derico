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


@needs_block_sheets
def test_the_hero_takes_its_body_type_from_the_public_ladder():
    """Ticket 17/22 — the seam, and why it is not a hardcoded family.

    `--plone-font-body` and `--plone-leading-body` already carry the mockup's
    exact values on Clara's `:root`, so the hero names them instead of
    restating them. A hardcoded `"Source Sans 3"` passes every visual check
    while silently dropping the theme seam, and the leading is easy to drop on
    its own — 1.6 against 1.65 is the legend's whole 291-against-330 height gap
    that ticket 10 measured.
    """
    for prop, token in (
        ("font-family", "var(--plone-font-body)"),
        ("line-height", "var(--plone-leading-body)"),
    ):
        assert token in _values_for(ROOT, prop), (
            f"the hero must name {token}; it declares "
            f"{_values_for(ROOT, prop) or 'nothing'}"
        )


@needs_block_sheets
def test_the_hero_never_hardcodes_its_type():
    """The other half of the seam: naming the token is not enough if a later
    rule restates the family in literal form."""
    offenders = sorted(
        f"{selector} {{ {name}: {value} }}"
        for selector, properties in _style_rules()
        for name, value in properties.items()
        if name in ("font-family", "font")
        and ("source sans" in value.lower() or '"' in value.replace("'", '"'))
    )
    assert not offenders, (
        "a block sheet must reach the family through the token ladder, never "
        "by name: " + ", ".join(offenders)
    )


#: (ink selector, halo selector). Each ring class carries its own width, so a
#: halo stated only for the default stroke would leave `.ring-now`'s 4 under a
#: 6.5 halo -- still a halo, but not the one the geometry was chosen for.
RING_PAIRS = [
    (f"{ROOT} .rings-disc circle", f"{ROOT} .rings-disc .ring-halo circle"),
    (f"{ROOT} .rings-disc .ring-thin", f"{ROOT} .rings-disc .ring-halo .ring-thin"),
    (f"{ROOT} .rings-disc .ring-now", f"{ROOT} .rings-disc .ring-halo .ring-now"),
]

#: A FLOOR the sheet must clear, not a mirror of what it declares (ticket 20).
#: 3 = 1.5px a side, under the 2px the halo ships; the sheet may thicken the
#: halo freely and only thinning past this is a regression. Ticket 18's
#: "never hardcode the CSS value" is the opposite construction and does not
#: apply: a test carrying its own copy of 6.5 would stay green when the halo
#: is softened, which is exactly what this catches.
MINIMUM_HALO_SURROUND = 3.0


@needs_block_sheets
def test_the_halo_is_wider_than_every_stroke_it_surrounds():
    """Ticket 20/23. A halo the same width as its ink is invisible."""
    for ink_selector, halo_selector in RING_PAIRS:
        ink = _values_for(ink_selector, "stroke-width")
        halo = _values_for(halo_selector, "stroke-width")
        assert ink, f"{ink_selector} states no stroke-width"
        assert halo, f"{halo_selector} states no stroke-width"
        surround = float(halo[-1]) - float(ink[-1])
        assert surround >= MINIMUM_HALO_SURROUND, (
            f"{halo_selector} surrounds its ink by {surround}px, under the "
            f"{MINIMUM_HALO_SURROUND}px floor — at 1px a side the antialiasing "
            "on a curved stroke leaves the effective adjacent colour a blend "
            "of halo and photograph"
        )


@needs_block_sheets
def test_the_halo_is_painted_in_the_ground_and_nothing_else():
    """The halo's whole job is to BE the adjacent colour, so it has to be the
    one opaque value the contrast test reads."""
    strokes = _values_for(f"{ROOT} .rings-disc .ring-halo circle", "stroke")
    assert strokes == ["var(--derico-hero-ground)"], (
        "the halo must be painted in the ground the contrast guarantee is "
        f"computed against; it declares {strokes or 'nothing'}"
    )


#: How far the legend's longest label reaches from the card's left edge. The
#: labels are fixed-size strings (`--derico-text-label` is not fluid), so this
#: is a LENGTH and not a share: measured 257px for "wächst mit den
#: Anforderungen" at 900, 1024, 1440 and 1920 alike, while the same ink is 66%
#: of the card at 900 and 43% at 1440. That gap is the whole argument for an
#: absolute stop, and it is why this is stated in rem.
LEGEND_INK_REACH_REM = 16.0


@needs_block_sheets
def test_the_legend_holds_its_ground_under_every_label():
    """The ground leaves at the right, which is a composition change; what the
    contrast guarantee needs is that it is still THERE, at full strength,
    everywhere the labels are. So this asserts the plateau rather than a flat
    fill — the first stop is the legend's ground token, held past the longest
    label's reach, and the card ends at nothing rather than at an edge.
    """
    grounds = _values_for(f"{ROOT} .ring-legend", "background")
    assert len(grounds) == 1, f"the legend states {len(grounds)} backgrounds"
    ground = re.sub(r"\s+", " ", grounds[0])
    assert ground.startswith("linear-gradient(90deg,"), (
        f"the legend's ground must fade across the card, not down it: {ground!r}"
    )
    plateau = re.search(
        r"var\(--derico-hero-legend-ground\)\s+0\s+([\d.]+)rem", ground
    )
    assert plateau, (
        "the first stop must be the legend ground itself — the value the "
        f"contrast guarantee is computed for — held for a stated length: {ground!r}"
    )
    assert float(plateau.group(1)) >= LEGEND_INK_REACH_REM, (
        f"the ground leaves at {plateau.group(1)}rem, inside the "
        f"{LEGEND_INK_REACH_REM}rem the labels reach — the is-now cyan would "
        "be back on the bare photograph, which is the one place it cannot go"
    )
    assert ground.rstrip(")").endswith("transparent 100%"), (
        f"the ground must reach nothing at the card's right edge: {ground!r}"
    )


@needs_block_sheets
def test_the_legend_is_narrower_than_its_plateau_can_fade_across():
    """A cap, and the one relation that makes the fade visible at all.

    The legend inherited the rings figure's 34rem and spent the right half of
    it on empty card. Capping it is free — but cap it AT the plateau and the
    gradient has nowhere to run, so the card ends on a hard edge again and the
    radius removed above comes back as a straight one. The width must exceed
    the plateau, and this pins that relation rather than either number.
    """
    widths = _values_for(f"{ROOT} .ring-legend", "width")
    assert len(widths) == 1, f"the legend states {len(widths)} widths"
    cap = re.search(r"min\(\s*100%\s*,\s*([\d.]+)rem\s*\)", widths[0])
    assert cap, (
        "the legend's width must be a cap over 100%, so the narrow two-column "
        f"range where the column is already smaller is untouched: {widths[0]!r}"
    )
    ground = re.sub(r"\s+", " ", _values_for(f"{ROOT} .ring-legend", "background")[0])
    plateau = float(
        re.search(r"var\(--derico-hero-legend-ground\)\s+0\s+([\d.]+)rem", ground).group(1)
    )
    assert float(cap.group(1)) > plateau, (
        f"the card is capped at {cap.group(1)}rem but its ground is opaque to "
        f"{plateau}rem — there is nothing left to fade across"
    )


@needs_block_sheets
def test_the_legend_has_no_rounded_corner():
    """A band the photograph runs into, not a card floating on it. The radius
    and the fade are the same decision seen from two ends; keeping one without
    the other leaves a rounded corner on a shape with no other edge."""
    radii = _values_for(f"{ROOT} .ring-legend", "border-radius")
    assert radii == ["0"], (
        f"the legend must be square; it declares {radii or 'nothing'}"
    )


@needs_block_sheets
def test_the_scrim_cannot_hang_outside_the_hero():
    """Ticket 21, and a defect found by measurement rather than by reading.

    The scrim was first anchored to the copy column, inset past it by the
    plateau margin plus the feather. That hangs 72px outside the hero at a 320
    viewport — measured, the hero reporting 392 against a 320 client width —
    and `overflow: hidden` clips it visually while still reporting the overflow
    that ticket 15's guarantee is *stated in terms of*. Widening that guarantee
    to let a decorative box through would blind it to the headline overflow it
    exists for, so the scrim moved to the hero root instead, where there is
    nothing to hang over.
    """
    scrims = {
        selector
        for selector, properties in _style_rules()
        if properties.get("background") == "var(--derico-hero-copy-scrim)"
    }
    assert scrims, "nothing paints the copy scrim at all"
    for selector in scrims:
        assert selector == f"{ROOT}::before", (
            "the scrim must ride the hero root, where `inset: 0` cannot "
            f"overflow it: {selector}"
        )
    assert _values_for(f"{ROOT}::before", "inset") == ["0"], (
        "the scrim must be inset: 0 — any negative inset is scrollable "
        "overflow the hero will report"
    )


@needs_block_sheets
def test_the_wide_hero_darkens_with_one_layer_that_reaches_its_right_edge():
    """One backdrop, edge to edge, and why the seam was structural.

    Two translucent layers at different alphas butted together at 50% cannot be
    feathered into each other: the feather crossfades between two values that
    were never equal, so the join stays visible as a vertical edge through the
    photograph. The fix is not a softer boundary, it is one layer — so this
    asserts the wash is switched OFF at wide, and that nothing ends the scrim's
    plateau at the old column boundary. Vertically it does end, at the ground
    line below; that is the next test.
    """
    assert _values_for(f"{ROOT} .hero-wash", "display") == ["none"], (
        "the wash must be off at wide; two darkening layers is what puts a "
        "seam down the middle of the photograph"
    )
    wide = [
        mask
        for mask in _values_for(f"{ROOT}::before", "mask-image")
        if "90deg" in mask
    ]
    assert len(wide) == 1, f"expected one wide scrim mask, found {len(wide)}"
    assert "50%" not in wide[0], (
        "the wide plateau must run to the hero's right edge, not stop at the "
        f"old column boundary: {wide[0]!r}"
    )


#: The action row's bottom, as a share of the hero's height. Measured on the
#: design source across 896-1920, where it moves by a tenth of a point. The
#: plateau has to reach at least this far down: the row's `quiet-link` is white
#: text with no backing of its own, and it is one of the inks the copy scrim's
#: guarantee is computed for. A floor, not a mirror of what the sheet declares.
ACTION_ROW_BOTTOM = 78.4


@needs_block_sheets
def test_the_ground_line_ends_the_plateau_below_the_action_row():
    """The hero stands ON the forest floor: below the ground line the
    photograph carries no overlay at all.

    Two things have to hold at once and they pull in opposite directions. The
    cut has to be a SECOND mask layer composited with `intersect`, or it stops
    being a cut and becomes a replacement that hands the whole copy column back
    to the photograph. And its plateau has to clear the action row, or the last
    line of the copy loses the backing the contrast guarantee assumes.
    """
    wide = [
        mask
        for mask in _values_for(f"{ROOT}::before", "mask-image")
        if "90deg" in mask
    ]
    assert len(wide) == 1, f"expected one wide scrim mask, found {len(wide)}"
    assert _values_for(f"{ROOT}::before", "mask-composite") == ["intersect"], (
        "the ground line must be intersected with the column mask; any other "
        "composite makes it a replacement, not a cut"
    )

    angles = re.findall(r"linear-gradient\(\s*(\d+)deg", wide[0])
    assert len(angles) == 2, (
        f"the wide scrim is the column mask and the ground line: {wide[0]!r}"
    )
    ground = wide[0][wide[0].index("linear-gradient(" + angles[1] + "deg") :]
    assert 180 < int(angles[1]) < 200, (
        f"the ground line runs across the hero, dropping to the right; "
        f"{angles[1]}deg does not"
    )

    plateau = re.search(r"black\s+0\s+([\d.]+)%", ground)
    assert plateau, f"the ground line states no plateau: {ground!r}"
    assert float(plateau.group(1)) >= ACTION_ROW_BOTTOM - 0.5, (
        f"the plateau ends at {plateau.group(1)}% of the hero, above the "
        f"action row's {ACTION_ROW_BOTTOM}% — the quiet-link beside the button "
        "would lose the only backing it has"
    )


@needs_block_sheets
def test_the_wash_is_cut_away_from_the_copy_where_it_is_still_painted():
    """Ticket 21 §3, now single column only — the scrim is the ONLY layer.

    Stacking two translucent layers composites darker than either, which is the
    solid copy panel this design avoids and is not the alpha the guarantee was
    computed for. Two columns there is no second layer to stack (see above);
    single column the wash is the composition below the copy band, and it is
    cut to fully transparent across the band rather than merely softened over
    it. The stop is proportional because the copy's box is: measured on the
    design source it occupies the top 4.1% to at most 45.5% of the hero.
    """
    masks = _values_for(f"{ROOT} .hero-wash", "mask-image")
    assert len(masks) == 1, (
        "the wash is painted at one breakpoint and so states one mask; found "
        f"{len(masks)}"
    )
    assert "180deg" in masks[0], f"the cut is across the copy BAND: {masks[0]!r}"
    assert "transparent 0 50%" in masks[0], (
        "the wash must be cut to fully transparent across the copy, not "
        f"merely softened over it: {masks[0]!r}"
    )
    assert "black calc(50% + 5rem)" in masks[0], (
        f"the wash does not feather back on off the same stop: {masks[0]!r}"
    )


@needs_block_sheets
def test_the_scrim_is_the_heros_only_translucent_backdrop():
    """The value is one value, and nothing else in the block paints over the
    photograph at a second alpha. What made the seam was not the boundary, it
    was that there were two numbers; a test that only guards the boundary would
    stay green the moment a third layer is added somewhere else.
    """
    painted = {
        (selector, properties.get("background"))
        for selector, properties in _style_rules()
        if "hero-copy-scrim" in (properties.get("background") or "")
        or "hero-wash" in (properties.get("background") or "")
    }
    selectors = sorted(selector for selector, _value in painted)
    assert selectors == [f"{ROOT} .hero-wash", f"{ROOT}::before"], (
        "exactly two rules may paint a translucent backdrop — the scrim, and "
        f"the single-column wash it replaces at wide; found {selectors}"
    )


@needs_block_sheets
def test_the_scrim_starts_where_the_copy_starts_and_not_at_the_heros_edge():
    """The reveal, and the one number it must not be written as.

    21 painted the plateau from the hero's left edge, so it covered the shell's
    gutter as well and the photograph was invisible on the left whatever the
    author uploaded. The strip left of the copy is the reveal now — but only
    while the scrim's first opaque stop is the SAME inset the grid is laid out
    with. Write that stop as a percentage tuned at one width and it agrees with
    the text at that width only: the inset is 27px at a 900 hero and 192px at
    1600, which is 3% against 12%.

    So both readings of `--derico-hero-inset` are asserted here: that the mask
    states it, and that the grid's own width is the formula it is derived from.
    """
    wide = [
        mask
        for mask in _values_for(f"{ROOT}::before", "mask-image")
        if "90deg" in mask
    ]
    assert len(wide) == 1, f"expected one wide scrim mask, found {len(wide)}"
    assert "black var(--derico-hero-inset)" in wide[0], (
        "the scrim's plateau must begin at the copy's own inset, not at a "
        f"percentage: {wide[0]!r}"
    )
    widths = _values_for(f"{ROOT} .home-hero__grid", "width")
    assert widths == ["min(100% - var(--derico-hero-gutter), var(--plone-measure))"], (
        "the shell's width must read the same gutter token the inset is "
        f"derived from, or the two can drift; it declares {widths or 'nothing'}"
    )


