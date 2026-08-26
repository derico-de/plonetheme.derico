"""The hero's contrast guarantees, read off the sheet that actually ships.

Tickets 18, 20 and 21. Three structural guarantees, one test each:

* the **legend card** — an opaque ground under the `<dl>`, because the is-now
  cyan is unreachable by any translucent treatment;
* the **ring halo** — an opaque ground stroke under each ring, because no ink
  passes 3:1 over an arbitrary photograph;
* the **copy scrim** — a near-opaque plateau under the copy column.

All three work by making the ink's *adjacent colour* something the sheet
declares rather than something the author uploads. That is why these are
arithmetic and not screenshots, and why only the scrim needs a photograph in
the sum at all: it is the one layer that is translucent.

Values are read from the built artifact, never restated here. Ticket 18's rule:
a test carrying its own copy of `0.926` stays green after somebody softens the
CSS, which is the one regression it exists to catch. Where a bare number does
appear it is a WCAG threshold or a *floor* the sheet must clear — the opposite
construction, and deliberately so (ticket 20's answer, "a floor, not a mirror").
"""

import re

from . import clara_css as css_tools


BLOCK_SHEETS = css_tools.BLOCK_SHEETS
needs_block_sheets = css_tools.needs_block_sheets

#: The worst photograph for any dark backdrop: it composites lightest there,
#: which is where a light ink has least room. Ticket 20 measured the shipped
#: forest at a 0.0116 median in the rings band with canopy gaps up to 0.815, so
#: this is the bound, not the fixture.
WHITE = "#ffffff"


def _properties():
    """Every custom property in play, block sheets layered over the theme."""
    props = css_tools.declarations(
        css_tools.DERICO_CSS.read_text(), css_tools.ROOT_SELECTORS
    )
    for path in BLOCK_SHEETS:
        for _selector, body in css_tools.rules(path.read_text()):
            for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;{}]+)", body):
                props[name] = value.strip()
    return props


def _split_alpha(value):
    """`oklch(l c h / a)` -> ("oklch(l c h)", a). Alpha defaults to 1."""
    match = re.fullmatch(
        r"(oklch\(\s*[\d.]+%?\s+[\d.]+\s+[\d.]+\s*)/\s*([\d.]+)\s*\)",
        value.strip(),
    )
    if not match:
        return value, 1.0
    return match.group(1).rstrip() + ")", float(match.group(2))


def _channels(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return [int(hex_colour[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def _over(colour, alpha, backdrop):
    """Composite `colour` at `alpha` onto `backdrop`, in sRGB as a browser does."""
    top, bottom = _channels(colour), _channels(backdrop)
    return "#{:02x}{:02x}{:02x}".format(
        *(round(255 * (alpha * top[i] + (1 - alpha) * bottom[i])) for i in range(3))
    )


def _colour(name, props):
    resolved = css_tools.to_hex(css_tools.resolve(name, props))
    assert resolved, f"{name} does not resolve to a colour"
    return resolved


def _backdrop(name, props, over=None):
    """A declared backdrop as the browser paints it, composited if translucent."""
    raw = css_tools.resolve(name, props)
    assert raw, f"{name} is not declared in any sheet that ships"
    base, alpha = _split_alpha(raw)
    hex_base = css_tools.to_hex(base)
    assert hex_base, f"{name} does not resolve to a colour: {raw!r}"
    if alpha >= 1.0:
        return hex_base, alpha
    assert over, f"{name} is translucent and needs a backdrop to composite over"
    return _over(hex_base, alpha, over), alpha


def _check(pairs, backdrop, label):
    props = _properties()
    failures = []
    for ink_name, minimum, role in pairs:
        ink = _colour(ink_name, props)
        ratio = css_tools.contrast(ink, backdrop)
        if ratio < minimum:
            failures.append(
                f"{role} ({ink_name} {ink}) is {ratio:.2f}:1 on {backdrop}, "
                f"needs {minimum}:1"
            )
    assert not failures, f"{label} does not carry its ink:\n  " + "\n  ".join(failures)


# --------------------------------------------------------------------------
# The legend card (ticket 18 §2)
# --------------------------------------------------------------------------

#: (token, WCAG minimum, what wears it). 4.5 = normal text, 3.0 = a hairline
#: read as a graphical object.
LEGEND_INK = [
    ("--derico-hero-ring-now", 4.5, "the is-now row's title and numeral"),
    ("--derico-hero-ring", 4.5, "every other title and numeral"),
    ("--derico-hero-ink-soft", 4.5, "the subtitles"),
    ("--derico-hero-rule", 3.0, "the rule between rows"),
]


@needs_block_sheets
def test_the_legend_card_carries_every_colour_the_legend_wears():
    """Why the card is opaque, in one assertion.

    The is-now cyan needs a wash alpha of 0.983 to clear 4.5:1 translucently —
    so nothing short of a ground reaches it, and once there IS a ground every
    other colour passes with room. That is the whole reason ticket 18 changed
    no colours: the card bought the contrast the palette could not.
    """
    props = _properties()
    ground, alpha = _backdrop("--derico-hero-ground", props)
    assert alpha == 1.0, (
        "the legend card must be OPAQUE — a translucent card puts the "
        "photograph back under the is-now cyan, which is the one ink no "
        "translucent treatment can rescue"
    )
    _check(LEGEND_INK, ground, "the legend card")


# --------------------------------------------------------------------------
# The ring halo (ticket 20)
# --------------------------------------------------------------------------

#: Both ring inks, against 1.4.11's 3:1 for a meaningful non-text graphic.
RING_INK = [
    ("--derico-hero-ring", 3.0, "the copper rings"),
    ("--derico-hero-ring-now", 3.0, "the is-now ring"),
]


@needs_block_sheets
def test_the_ring_halo_carries_both_ring_inks():
    """1.4.11 for the rings disc, and it needs no photograph in the sum.

    That is the point of an opaque halo: the stroke's adjacent colour stops
    being the upload and becomes a value this sheet declares. Over a bare
    photograph neither ink can be rescued at all — copper (Y 0.5365) needs a
    backdrop at Y <= 0.1455 and its bright side would need Y >= 1.71, which
    does not exist.
    """
    props = _properties()
    halo, alpha = _backdrop("--derico-hero-ground", props)
    assert alpha == 1.0, "a translucent halo lets the photograph back in"
    _check(RING_INK, halo, "the ring halo")


# --------------------------------------------------------------------------
# The copy scrim (ticket 18 §3, built by 21)
# --------------------------------------------------------------------------

#: The copy column's inks. The headline is large text, so 3:1; `quiet-link`
#: takes the copper on hover, which is the binding case for the plateau.
COPY_INK = [
    ("--derico-hero-copper", 4.5, "the kicker, and quiet-link on hover"),
    ("--derico-hero-ink-soft", 4.5, "the lede"),
    ("--derico-hero-ink", 4.5, "the quiet link"),
    ("--derico-hero-ink", 3.0, "the headline (large text)"),
]


@needs_block_sheets
def test_the_copy_scrim_carries_every_copy_ink_over_the_worst_photograph():
    """The one guarantee with a photograph in the sum, taken at its worst.

    The scrim is translucent by design, so the composite depends on the upload.
    A dark scrim composites lightest over white, and every ink here is lighter
    than the scrim, so white is the worst case rather than an arbitrary one.
    """
    props = _properties()
    scrim, alpha = _backdrop("--derico-hero-copy-scrim", props, over=WHITE)
    assert alpha < 1.0, (
        "an opaque scrim is the solid copy panel this design avoids "
        "(ticket 18 §3); if it has become opaque, the mask is doing nothing"
    )
    _check(COPY_INK, scrim, "the copy scrim")


@needs_block_sheets
def test_the_scrim_would_go_red_if_it_were_softened():
    """Non-vacuity: prove the assertion above can fail (ticket 19's lesson).

    A guarantee that would hold at any alpha is not a guarantee. This derives
    the floor the sheet must clear rather than restating what it declares —
    the plateau may be raised freely, and only lowering past the floor is a
    regression.
    """
    props = _properties()
    raw = css_tools.resolve("--derico-hero-copy-scrim", props)
    base, alpha = _split_alpha(raw)
    hex_base = css_tools.to_hex(base)

    floor = 0.0
    for ink_name, minimum, _role in COPY_INK:
        ink = _colour(ink_name, props)
        low, high = 0.0, 1.0
        for _ in range(60):
            middle = (low + high) / 2
            if css_tools.contrast(ink, _over(hex_base, middle, WHITE)) >= minimum:
                high = middle
            else:
                low = middle
        floor = max(floor, high)

    assert 0.0 < floor < 1.0, (
        "the floor is degenerate, so the guarantee above is vacuous"
    )
    assert alpha >= floor, (
        f"the plateau is {alpha}, below the {floor:.4f} its own inks need over "
        "a white photograph"
    )
    # And the assertion is live: one step under the floor must fail.
    softened = _over(hex_base, floor - 0.01, WHITE)
    assert any(
        css_tools.contrast(_colour(ink, props), softened) < minimum
        for ink, minimum, _role in COPY_INK
    ), "softening past the floor changes nothing, so this test guards nothing"


# --------------------------------------------------------------------------
# The marker chips (ticket 20 §6)
# --------------------------------------------------------------------------

#: (ink, backdrop, minimum, role). The chips are the one text in the hero whose
#: backdrop is entirely element-painted, which is why they are asserted here as
#: values rather than sampled as pixels in `hero-view.e2e.js`.
MARKER_PAIRS = [
    ("--derico-hero-ground", "--derico-hero-ring", 4.5, "a numeral on its chip"),
    (
        "--derico-hero-ground",
        "--derico-hero-ring-now",
        4.5,
        "the is-now numeral on its chip",
    ),
    ("--derico-hero-ring", "--derico-hero-ground", 3.0, "the chip against its border"),
    (
        "--derico-hero-ring-now",
        "--derico-hero-ground",
        3.0,
        "the is-now chip against its border",
    ),
]


@needs_block_sheets
def test_the_marker_chips_carry_their_own_backdrop():
    """Ticket 20 §6, on the record rather than by luck.

    The ticket claimed the chips were "unaffected" because they carry their own
    backdrop — but that is a claim about the numerals (1.4.3) standing in for a
    claim about the chip's silhouette over the photograph (1.4.11). The two
    happen to agree, because the chip is two-tone: an opaque copper fill inside
    a ground border, so whichever way the photograph goes, one of the pair is
    the adjacent colour. That is the same construction as the ring halo, and
    the chips are where it was already in the block. Both halves asserted here.
    """
    props = _properties()
    failures = []
    for ink_name, ground_name, minimum, role in MARKER_PAIRS:
        ink, ground = _colour(ink_name, props), _colour(ground_name, props)
        ratio = css_tools.contrast(ink, ground)
        if ratio < minimum:
            failures.append(
                f"{role} ({ink_name} on {ground_name}) is {ratio:.2f}:1, "
                f"needs {minimum}:1"
            )
    assert not failures, "the marker chips do not carry their ink:\n  " + "\n  ".join(
        failures
    )
