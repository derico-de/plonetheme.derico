"""WCAG contrast guard for the Jahresringe ladder as it lands in Clara's roles.

Ratios are measured on the resolved sRGB values the browser gets, not derived
from the design's OKLCH coordinates — DESIGN.md §2, "Measure, Don't Derive".
"""

import pytest

from . import clara_css as css_tools


CLARA_PATH = css_tools.clara_bundle_path()
needs_clara = pytest.mark.skipif(
    CLARA_PATH is None, reason="plonetheme.clara's compiled bundle is not available"
)
DERICO = css_tools.DERICO_CSS.read_text()


def _effective(selectors_extra=()):
    clara = css_tools.declarations(
        CLARA_PATH.read_text(), css_tools.ROOT_SELECTORS
    )
    clara.update(css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS))
    for selectors in selectors_extra:
        clara.update(css_tools.declarations(DERICO, selectors))
    return clara


def _ratio(props, foreground, background):
    fg = css_tools.to_hex(css_tools.resolve(foreground, props))
    bg = css_tools.to_hex(css_tools.resolve(background, props))
    assert fg, f"{foreground} does not resolve to a colour"
    assert bg, f"{background} does not resolve to a colour"
    return css_tools.contrast(fg, bg), fg, bg


#: (foreground, background, minimum). 4.5 = normal text, 3.0 = UI geometry and
#: large display type.
LIGHT_PAIRS = [
    # body and secondary text on every ground Clara paints
    ("--clara-ink", "--clara-ground", 4.5),
    ("--clara-ink", "--clara-surface", 4.5),
    ("--clara-ink", "--clara-band", 4.5),
    ("--clara-ink", "--clara-band-soft", 4.5),
    ("--clara-ink-soft", "--clara-ground", 4.5),
    ("--clara-ink-soft", "--clara-surface", 4.5),
    ("--clara-ink-soft", "--clara-band", 4.5),
    # the contact band's lede, which is ink-soft on the accent slot — the one
    # ground pairing that had no reader until the band arrived
    ("--clara-ink-soft", "--clara-band-soft", 4.5),
    # links. NOT tested against --clara-band: the strong cyan band takes ink
    # text and quiet ink links by design (DESIGN.md §5, "Quiet link"), and
    # Clara paints no link on it once --clara-footer-ground moves to ground.
    ("--plone-color-link", "--clara-ground", 4.5),
    ("--plone-color-link", "--clara-surface", 4.5),
    ("--plone-color-link", "--clara-band-soft", 4.5),
    ("--plone-color-link-hover", "--clara-ground", 4.5),
    ("--plone-color-link-hover", "--clara-band-soft", 4.5),
    # the copper CTA: fill against its ground, label against the fill
    ("--clara-amber", "--clara-ground", 3.0),
    ("--clara-amber", "--clara-band", 3.0),
    # the contact band's call to action stands on the accent slot
    ("--clara-amber", "--clara-band-soft", 3.0),
    ("--clara-on-amber", "--clara-amber", 4.5),
    ("--clara-on-amber", "--clara-amber-hover", 4.5),
    # cyan controls
    ("--plone-color-on-primary", "--plone-color-primary", 4.5),
    ("--plone-color-on-primary", "--plone-color-primary-hover", 4.5),
    ("--plone-color-primary", "--clara-ground", 3.0),
    # toolbar chrome
    ("--plone-toolbar-text-color", "--plone-toolbar-bg", 4.5),
    ("--plone-link-color-on-dark", "--plone-toolbar-bg", 4.5),
    # hairlines and structural rules as graphical objects
    ("--clara-band-rule", "--clara-ground", 3.0),
    # semantic states on their own tinted surfaces
    ("--plone-color-success", "--plone-color-success-surface", 4.5),
    ("--plone-color-danger", "--plone-color-danger-surface", 4.5),
    ("--plone-color-warning-text", "--plone-color-warning-surface", 4.5),
    ("--plone-color-info-text", "--plone-color-info-surface", 4.5),
    # state fills against the page
    ("--plone-color-success", "--clara-ground", 4.5),
    ("--plone-color-danger", "--clara-ground", 4.5),
    ("--plone-color-on-warning", "--plone-color-warning", 4.5),
]


@needs_clara
@pytest.mark.parametrize(("foreground", "background", "minimum"), LIGHT_PAIRS)
def test_light_mode_contrast(foreground, background, minimum):
    props = _effective()
    ratio, fg, bg = _ratio(props, foreground, background)
    assert ratio >= minimum, (
        f"{foreground} {fg} on {background} {bg} is {ratio:.2f}:1, needs {minimum}:1"
    )


#: Dark chrome only appears where Plone's toolbar switch is used; derico flips
#: the identity roles so nothing renders Plone-blue there. Clara's own dark
#: ground is --plone-gray-900.
DARK_PAIRS = [
    ("--plone-color-primary", "--plone-gray-900", 4.5),
    ("--plone-color-link", "--plone-gray-900", 4.5),
    ("--plone-color-link-hover", "--plone-gray-900", 4.5),
    ("--clara-amber-text", "--plone-gray-900", 4.5),
    ("--plone-color-info-text", "--plone-color-info-surface", 4.5),
]


@needs_clara
@pytest.mark.parametrize(("foreground", "background", "minimum"), DARK_PAIRS)
def test_dark_mode_contrast(foreground, background, minimum):
    props = _effective(selectors_extra=(css_tools.DARK_SELECTORS,))
    ratio, fg, bg = _ratio(props, foreground, background)
    assert ratio >= minimum, (
        f"[dark] {foreground} {fg} on {background} {bg} is {ratio:.2f}:1, "
        f"needs {minimum}:1"
    )


@needs_clara
def test_the_brand_cyan_is_never_asked_to_be_normal_text():
    """#039fba is identity and geometry: 3.06:1 on the ground, not AA text.

    The guard is that --plone-color-link resolves to the darker functional step
    rather than to the anchor (DESIGN.md §2, "The Lightness Ceilings").
    """
    props = _effective()
    link = css_tools.to_hex(css_tools.resolve("--plone-color-link", props))
    brand = css_tools.to_hex(css_tools.resolve("--clara-brand", props))
    assert link != brand
    ground = css_tools.to_hex(css_tools.resolve("--clara-ground", props))
    assert css_tools.contrast(link, ground) >= 4.5
    assert 3.0 <= css_tools.contrast(brand, ground) < 4.5
