"""derico's values for Blicca's `backgroundColor` palette (derico.css §8).

The `backgroundColor` style field is a contract split across three packages:
Blicca names the slots and reads an `--aurora-block-*` custom property per
slot, the theme supplies the values, and the author picks a slot by name in
the block's settings. Nothing in that chain fails loudly on its own — an
unfilled slot silently paints Blicca's generic slate, a slot filled under a
name Blicca never publishes silently paints nothing at all. These tests are
where it fails instead.

Blicca's half is read from the package rather than restated: `plate.py`'s
BLOCK_BACKGROUND_VARS is the server renderer's own table, so a renamed or
added slot shows up here as a failure rather than as a picker entry that
does not paint.
"""

import re

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


def _derico_light():
    return css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS)


def _effective():
    """Clara's tokens as derico leaves them, so a var() chain resolves."""
    props = css_tools.declarations(
        CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS
    )
    props.update(_derico_light())
    return props


def _blicca_hooks():
    """Every `--aurora-block-*` name Blicca's palette actually reads."""
    hooks = set()
    for declarations in blicca_plate.BLOCK_BACKGROUND_VARS.values():
        for value in declarations.values():
            hooks.update(re.findall(r"--aurora-block-[\w-]+", value))
    return hooks


# --------------------------------------------------------------------------
# The names: exactly the hooks Blicca reads, no more and no fewer
# --------------------------------------------------------------------------

@needs_blicca
def test_the_theme_fills_every_hook_blicca_reads():
    """An unfilled hook falls back to Blicca's generic slate, silently."""
    declared = {
        name for name in _derico_light() if name.startswith("--aurora-block-")
    }
    missing = sorted(_blicca_hooks() - declared)
    assert not missing, (
        f"derico.css leaves {missing} unset, so those slots paint Blicca's "
        "generic slate fallback rather than a brand colour"
    )


@needs_blicca
def test_the_theme_invents_no_hook_blicca_does_not_read():
    """A name Blicca never reads is a value nothing in the picker can choose."""
    declared = {
        name for name in _derico_light() if name.startswith("--aurora-block-")
    }
    unknown = sorted(declared - _blicca_hooks())
    assert not unknown, (
        f"derico.css declares {unknown}, which Blicca's palette never reads — "
        "a fourth slot has to be added to BLICCA_BLOCK_BACKGROUNDS first"
    )


# --------------------------------------------------------------------------
# The values: the design's own section grounds, not new colours
# --------------------------------------------------------------------------

#: hook -> the `--derico-*` step the ladder already uses for that treatment.
#: The two light slots are the quiet and softer cyan tints; the deep petrol
#: is the ladder's dark ground, the step the toolbar sits on. --band, the
#: committed cyan the design bands a section with, is deliberately absent —
#: see `test_the_committed_band_is_not_offered_as_a_slot`.
EXPECTED_ALIASES = {
    "--aurora-block-bg-grey": "--derico-surface",
    "--aurora-block-bg-accent": "--derico-band-soft",
    "--aurora-block-bg-dark": "--derico-brand-deep",
    "--aurora-block-fg-dark": "--derico-ground",
}


@pytest.mark.parametrize(("hook", "target"), sorted(EXPECTED_ALIASES.items()))
def test_each_slot_aliases_a_ladder_step_rather_than_restating_a_value(
    hook, target
):
    """A literal here would fork the brand palette where nobody looks."""
    light = _derico_light()
    assert hook in light, f"derico.css does not declare {hook}"
    assert re.fullmatch(rf"var\(\s*{re.escape(target)}\s*\)", light[hook]), (
        f"{hook} must alias {target} verbatim; it declares {light[hook]!r}"
    )


# --------------------------------------------------------------------------
# Contrast, measured on the resolved sRGB values, never derived from OKLCH
# --------------------------------------------------------------------------

#: (foreground, background, minimum) for every slot an author can pick. Body
#: text lands on a block background as ordinary copy, so 4.5:1 throughout.
#: The two light slots carry Clara's ink; the dark slot hands its subtree
#: `--aurora-block-fg-dark` through Blicca's `color: inherit` rule.
SLOT_PAIRS = [
    ("--clara-ink", "--aurora-block-bg-grey", 4.5),
    ("--clara-ink", "--aurora-block-bg-accent", 4.5),
    ("--clara-ink-soft", "--aurora-block-bg-grey", 4.5),
    ("--clara-ink-soft", "--aurora-block-bg-accent", 4.5),
    ("--aurora-block-fg-dark", "--aurora-block-bg-dark", 4.5),
    # Links, on every light slot. This is the pair that decided the accent
    # value: the theme's own table tests links on --clara-band-soft and
    # deliberately does not test them on --clara-band, and a picker slot has
    # no say over what an author puts on it.
    ("--plone-color-link", "--aurora-block-bg-grey", 4.5),
    ("--plone-color-link", "--aurora-block-bg-accent", 4.5),
    ("--plone-color-link-hover", "--aurora-block-bg-grey", 4.5),
    ("--plone-color-link-hover", "--aurora-block-bg-accent", 4.5),
    # the copper CTA as a graphical object on each light slot
    ("--clara-amber", "--aurora-block-bg-grey", 3.0),
    ("--clara-amber", "--aurora-block-bg-accent", 3.0),
]


@needs_clara
@pytest.mark.parametrize(("foreground", "background", "minimum"), SLOT_PAIRS)
def test_slot_contrast(foreground, background, minimum):
    props = _effective()
    fg = css_tools.to_hex(css_tools.resolve(foreground, props))
    bg = css_tools.to_hex(css_tools.resolve(background, props))
    assert fg, f"{foreground} does not resolve to a colour"
    assert bg, f"{background} does not resolve to a colour"
    ratio = css_tools.contrast(fg, bg)
    assert ratio >= minimum, (
        f"{foreground} {fg} on {background} {bg} is {ratio:.2f}:1, "
        f"needs {minimum}:1"
    )


@needs_clara
def test_the_committed_band_is_not_offered_as_a_slot():
    """The reason the accent slot is the soft step, stated as a measurement.

    --band is the design's signature section ground and it is a fine one —
    for a section whose content the designer chose. As a slot in a picker it
    would take arbitrary author content, and an ordinary link on it misses AA.
    If Clara's link step ever darkens far enough to clear it, this test fails
    and the choice is worth revisiting.
    """
    props = _effective()
    band = css_tools.to_hex(css_tools.resolve("--derico-band", props))
    link = css_tools.to_hex(css_tools.resolve("--plone-color-link", props))
    assert css_tools.contrast(link, band) < 4.5, (
        "a link now clears AA on the committed band; the accent slot could "
        "carry the design's full-strength cyan after all"
    )
