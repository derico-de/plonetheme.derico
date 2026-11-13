"""derico's values for Blicca's `backgroundColor` palette.

The `backgroundColor` style field is a contract split across three packages:
Blicca names the slots and reads an `--aurora-block-*` custom property per
slot, the theme supplies the values, and the author picks a slot by name in
the block's settings. Nothing in that chain fails loudly on its own — an
unfilled slot silently paints Blicca's generic slate, a slot filled under a
name Blicca never publishes silently paints nothing at all. These tests are
where it fails instead.

Blicca's half is read from the package rather than restated:
`blocks_view.css` is the sheet that styles the built-in slots on both surfaces,
so a renamed or added slot shows up here as a failure rather than as a picker
entry that does not paint.
"""

import re
from pathlib import Path

import pytest

from . import clara_css as css_tools


DERICO = css_tools.DERICO_CSS.read_text()

try:
    import plone.blicca.auroraeditor as blicca
except ImportError:  # pragma: no cover - the theme's floor makes this unlikely
    blicca = None

needs_blicca = pytest.mark.skipif(
    blicca is None, reason="plone.blicca.auroraeditor is not importable"
)

CLARA_PATH = css_tools.clara_bundle_path()
needs_clara = pytest.mark.skipif(
    CLARA_PATH is None, reason="plonetheme.clara's compiled bundle is not available"
)


def _derico_light():
    return css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS)


def _effective():
    """Clara's tokens as derico leaves them, so a var() chain resolves."""
    props = css_tools.declarations(CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS)
    props.update(_derico_light())
    return props


def _blicca_hooks():
    """Every `--aurora-block-*` name Blicca's palette reads and leaves to a theme."""
    sheet = Path(blicca.__file__).parent / "browser/rendering/static/blocks_view.css"
    rules = "".join(re.findall(r"\.has--backgroundColor--[\w-]+\s*\{[^}]*\}", sheet.read_text()))
    named = set(re.findall(r"--aurora-block-[\w-]+", rules))
    return named - set(re.findall(r"(--aurora-block-[\w-]+)\s*:", rules))


# --------------------------------------------------------------------------
# The names: exactly the hooks Blicca reads, no more and no fewer
# --------------------------------------------------------------------------


@needs_blicca
def test_the_theme_fills_every_hook_blicca_reads():
    """An unfilled hook falls back to Blicca's generic slate, silently."""
    declared = {name for name in _derico_light() if name.startswith("--aurora-block-")}
    missing = sorted(_blicca_hooks() - declared)
    assert not missing, (
        f"derico.css leaves {missing} unset, so those slots paint Blicca's "
        "generic slate fallback rather than a brand colour"
    )


@needs_blicca
def test_the_theme_invents_no_hook_blicca_does_not_read():
    """A name Blicca never reads is a value nothing in the picker can choose."""
    declared = {name for name in _derico_light() if name.startswith("--aurora-block-")}
    unknown = sorted(declared - _blicca_hooks())
    assert not unknown, (
        f"derico.css declares {unknown}, which Blicca's palette never reads — "
        "a fourth slot has to be registered in Blicca's block_backgrounds first"
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
    # what the dark slot hands the text styles: the exit section's lightened
    # copper, soft ink and rule
    "--aurora-block-accent-dark": "--derico-copper-light",
    "--aurora-block-fg-soft-dark": "--derico-ground-soft",
    "--aurora-block-rule-dark": "--derico-rule-light",
    # what Blicca paints behind code, callouts and table headers on the dark slot
    "--aurora-block-inset-dark": "--derico-brand-deeper",
}


@pytest.mark.parametrize(("hook", "target"), sorted(EXPECTED_ALIASES.items()))
def test_each_slot_aliases_a_ladder_step_rather_than_restating_a_value(hook, target):
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
    # a kicker, a byline or a list marker, and a lede or a definition, on
    # the dark slot; the rule between rows as a graphical object
    ("--aurora-block-accent-dark", "--aurora-block-bg-dark", 4.5),
    ("--aurora-block-fg-soft-dark", "--aurora-block-bg-dark", 4.5),
    ("--aurora-block-rule-dark", "--aurora-block-bg-dark", 3.0),
    # the same inks on the insets inside the dark slot
    ("--aurora-block-fg-dark", "--aurora-block-inset-dark", 4.5),
    ("--aurora-block-accent-dark", "--aurora-block-inset-dark", 4.5),
    ("--aurora-block-fg-soft-dark", "--aurora-block-inset-dark", 4.5),
    ("--aurora-block-rule-dark", "--aurora-block-inset-dark", 3.0),
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
        f"{foreground} {fg} on {background} {bg} is {ratio:.2f}:1, needs {minimum}:1"
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


# --------------------------------------------------------------------------
# Copper: registered by the theme, styled by the theme
# --------------------------------------------------------------------------

COPPER = ".has--backgroundColor--copper"
BACKGROUNDS_CSS = (css_tools.STATIC / "backgrounds.css").read_text()

#: (foreground, background, minimum) on the copper band. Blicca's light insets go
#: darker here, so the one ink is measured on them too; the Promo CTA inverts.
COPPER_PAIRS = [
    ("--block-foreground", "--block-background", 4.5),
    ("--aurora-text-accent-color", "--block-background", 4.5),
    ("--aurora-text-soft-color", "--block-background", 4.5),
    ("--aurora-text-strong-color", "--block-background", 4.5),
    ("--block-foreground", "--aurora-code-background", 4.5),
    ("--block-foreground", "--aurora-callout-background", 4.5),
    ("--block-foreground", "--aurora-table-header-background", 4.5),
    ("--aurora-divider", "--block-background", 3.0),
    ("--aurora-quote-border", "--block-background", 3.0),
    ("--aurora-table-border", "--block-background", 3.0),
    ("--aurora-toggle-chevron", "--block-background", 3.0),
    ("--derico-copper-text", "--block-foreground", 4.5),
    ("--derico-copper-text", "--derico-copper-surface", 4.5),
]


def _copper():
    return css_tools.declarations(BACKGROUNDS_CSS, [COPPER])


def test_copper_paints_the_brand_copper():
    declared = _copper()
    assert declared["--block-background"] == "var(--derico-copper)"
    assert declared["--block-foreground"] == "var(--derico-on-copper)"


def test_copper_cta_inverts_the_band():
    button = ".block.has--backgroundColor--copper .promo .promo-cta-button"
    assert css_tools.values_for(BACKGROUNDS_CSS, button, "color") == ["var(--derico-copper-text)"]
    assert css_tools.values_for(BACKGROUNDS_CSS, button, "background") == [
        "var(--block-foreground)"
    ]
    assert css_tools.values_for(BACKGROUNDS_CSS, f"{button}:hover", "background") == [
        "var(--derico-copper-surface)"
    ]


@needs_clara
def test_copper_canvas_link_token_is_the_foreground():
    link = css_tools.declarations(BACKGROUNDS_CSS, [f"{COPPER} .slate-a"])
    red, green, blue = (int(part) for part in link["--bs-primary-rgb"].split(","))
    props = {**_effective(), **_copper()}
    foreground = css_tools.to_hex(css_tools.resolve("--block-foreground", props))
    assert f"#{red:02x}{green:02x}{blue:02x}" == foreground.lower()


@needs_clara
@pytest.mark.parametrize(("foreground", "background", "minimum"), COPPER_PAIRS)
def test_copper_contrast(foreground, background, minimum):
    props = {**_effective(), **_copper()}
    fg = css_tools.to_hex(css_tools.resolve(foreground, props))
    bg = css_tools.to_hex(css_tools.resolve(background, props))
    ratio = css_tools.contrast(fg, bg)
    assert ratio >= minimum, (
        f"{foreground} {fg} on {background} {bg} is {ratio:.2f}:1, needs {minimum}:1"
    )
