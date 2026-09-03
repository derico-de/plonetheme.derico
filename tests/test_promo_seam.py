"""derico's values for the Promo block's theme seam (derico.css §9).

The seam is a contract split across two packages, and like `backgroundColor`'s
palette it fails silently in both directions. `derico.blicca.promoblock`
publishes nineteen `--promo-*` properties and **declares none of them**: every
default lives at its point of use as `var(--promo-x, <literal>)` (the block's
ADR 0002). So a theme that misspells a name, or that keeps setting one the
block has dropped, gets no error at all — it gets the literal default, which is
a promo that quietly is not derico's.

Blicca's half of §8 is read from the package rather than restated; the block's
half is read the same way, out of the built stylesheet it ships. That file is
the set of names the block actually consumes — the README's property table is
the block's own published contract and its own lockstep test
(`bundle-src/test/seam-lockstep.test.ts`) already holds the two together, so
restating the table here would fork it.

The theme's side of the same lockstep is the last test in section 1: **only
derico.css may declare a `--promo-*` property**. Ticket 16 asked for tokens and
no rules and had to say "caught at review" — the block's lockstep test cannot
see this repository. It is caught here instead.
"""

import re

import pytest

from . import clara_css as css_tools


DERICO = css_tools.DERICO_CSS.read_text()

try:
    import derico.blicca.promoblock as promoblock_package
except ImportError:  # pragma: no cover - the theme's dependency makes this unlikely
    promoblock_package = None

PROMO_CSS = None
if promoblock_package is not None:
    from pathlib import Path

    candidate = Path(promoblock_package.__file__).parent / "static" / "promo-block.css"
    if candidate.is_file():
        PROMO_CSS = candidate

needs_promo_block = pytest.mark.skipif(
    PROMO_CSS is None,
    reason="derico.blicca.promoblock's built stylesheet is not available",
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


def _declared():
    """Every `--promo-*` property derico.css sets on :root."""
    return {
        name: value
        for name, value in _derico_light().items()
        if name.startswith("--promo-")
    }


def _block_hooks():
    """Every `--promo-*` name the block's own stylesheet reads.

    Comments are stripped first: the sheet documents the seam in prose and
    names `--promo-x` as its placeholder, which is not a property.
    """
    text = css_tools.strip_comments(PROMO_CSS.read_text())
    return set(re.findall(r"var\(\s*(--promo-[\w-]+)", text))


# --------------------------------------------------------------------------
# 1. The names, and where they are allowed to be declared
# --------------------------------------------------------------------------

@needs_promo_block
def test_every_property_the_theme_sets_is_one_the_block_reads():
    """A name the block does not read paints nothing, and says nothing."""
    unknown = sorted(set(_declared()) - _block_hooks())
    assert not unknown, (
        f"derico.css §9 declares {unknown}, which the Promo block's stylesheet "
        "never reads — either the property was renamed upstream or this is a "
        "typo; both paint the block's literal default instead"
    )


@needs_promo_block
def test_the_block_still_reads_every_property_the_theme_sets():
    """The other direction: the seam narrowing must fail loudly, not quietly.

    Removing a property is breaking under the block's own growth policy, so a
    theme that goes on setting a dropped name is a theme that silently lost a
    value it chose. Same assertion as above read backwards, and both are cheap;
    what earns the second one its place is that the first passes vacuously if
    the theme ever declares nothing at all.
    """
    declared = set(_declared())
    assert declared, "derico.css §9 declares no --promo-* property at all"
    assert declared <= _block_hooks()


def test_only_the_token_layer_declares_a_promo_property():
    """The theme's half of the block's lockstep test (ticket 16).

    The seam is tokens, never rules: the block's sheet is `@scope`-wrapped and
    beats an unlayered theme rule at equal specificity, so a theme that reaches
    for a rule has to escalate — and a `--promo-*` set on `.promo` itself would
    shadow the inherited value, which is the one failure ADR 0002 exists to
    prevent. The block's own lockstep test covers its stylesheet and cannot see
    this repository; this is the half that can.
    """
    leaked = {}
    for path in css_tools.theme_stylesheets() + css_tools.block_stylesheets():
        names = sorted(
            set(
                re.findall(
                    r"(--promo-[\w-]+)\s*:", css_tools.strip_comments(path.read_text())
                )
            )
        )
        if names:
            leaked[path.name] = names
    assert not leaked, (
        "only derico.css may declare the Promo block's seam properties, and "
        f"only on :root; found {leaked}"
    )


def test_the_token_layer_declares_them_only_where_they_inherit_in():
    """`:root`, never a block selector — the other half of the same claim.

    Per RULE, not per name: comparing the set of names declared anywhere
    against the set declared on `:root` cannot see a SECOND declaration of a
    name §9 already sets, which is the likely shape of the mistake — someone
    re-tuning one property for one context by adding `.promo { … }` below.
    """
    root = {re.sub(r"\s+", "", selector) for selector in css_tools.ROOT_SELECTORS}
    stray = {}
    for selector, body in css_tools._blocks(DERICO):
        parts = {re.sub(r"\s+", "", part) for part in selector.split(",")}
        if parts & root:
            continue
        names = sorted(set(re.findall(r"(--promo-[\w-]+)\s*:", body)))
        if names:
            stray[css_tools.normalise_selector(selector)] = names
    assert not stray, (
        f"derico.css declares {stray} outside :root. A --promo-* set anywhere "
        "the block can see it shadows the theme's inherited value (ADR 0002)"
    )


# --------------------------------------------------------------------------
# 2. The values: the design's own steps, never a second copy of one
# --------------------------------------------------------------------------

#: property -> the ladder step it must alias verbatim. `--clara-text-title` is
#: named directly rather than re-published as a `--derico-text-*` alias first:
#: §3's aliases exist for the sheets that may not name a Clara token, and
#: derico.css is the one that may. `--plone-radius-pill` is Clara's radius
#: scale, which derico inherits untouched (test_override_minimality).
EXPECTED_ALIASES = {
    "--promo-kicker-size": "--derico-text-label",
    "--promo-kicker-color": "--derico-copper-text",
    "--promo-title-size": "--clara-text-title",
    "--promo-cta-bg": "--derico-copper",
    "--promo-cta-fg": "--derico-on-copper",
    "--promo-cta-hover-bg": "--derico-copper-hover",
    "--promo-cta-radius": "--plone-radius-pill",
}


@pytest.mark.parametrize(("prop", "target"), sorted(EXPECTED_ALIASES.items()))
def test_each_property_aliases_a_ladder_step_rather_than_restating_a_value(
    prop, target
):
    """A literal here would fork the brand palette where nobody looks."""
    declared = _declared()
    assert prop in declared, f"derico.css §9 does not declare {prop}"
    assert re.fullmatch(rf"var\(\s*{re.escape(target)}\s*\)", declared[prop]), (
        f"{prop} must alias {target} verbatim; it declares {declared[prop]!r}"
    )


@needs_clara
def test_the_title_step_is_the_design_s_component_heading_not_its_section_one():
    """Why `--clara-text-title` and not `--derico-text-heading` (ticket 16).

    The design source of record puts every component heading on the title step
    and reserves the heading step for page and section headings — `.page-hero
    h1`, `.section-heading`, `.contact-band h2`. The promo is a block an author
    drops on a page, so it is dressed as a card. Reproducing the contact band's
    scale needs a size that varies with `blockWidth`, which the seam does not
    publish; that is ticket 20, not a value here.
    """
    props = _effective()
    title = css_tools.resolve("--promo-title-size", props)
    heading = css_tools.resolve("--clara-text-heading", props)
    assert title is not None, "--promo-title-size does not resolve"
    assert title != heading, (
        "the promo's title is on the design's SECTION heading step; that scale "
        "belongs to the page's own headings, and a card wearing it towers over "
        "its own copy (measured on /Plone/promo-band-probe, ticket 16)"
    )


#: The two properties ticket 16's own mapping table listed and the design
#: declined, each with the line that decided it. Pinned rather than merely
#: omitted, because the table is the obvious place a later reader looks.
DECLINED = {
    "--promo-description-size": (
        "the design's card copy is body text — `.mega-intro p` states no size "
        "at all — and `--text-lede` is the SECTION lede (`.lede`, "
        "`.contact-band-lede`). The block's 1rem default is already right"
    ),
    "--promo-link-color": (
        "the design's `.quiet-link` is ink, which is what the block's "
        "`currentColor` default already resolves to inside a promo. Setting it "
        "to a brand step would also tint the whole card: the property paints "
        "`.promo-cardlink`, the anchor that WRAPS the block, where "
        "`currentColor` is what stops the UA link colour reaching every child"
    ),
}


@pytest.mark.parametrize(("prop", "reason"), sorted(DECLINED.items()))
def test_the_declined_properties_stay_declined(prop, reason):
    assert prop not in _declared(), f"{prop} is set, but {reason}"


# --------------------------------------------------------------------------
# 3. Contrast, measured on the resolved sRGB values, never derived from OKLCH
# --------------------------------------------------------------------------

#: (foreground, background, minimum) for the ink the seam introduces and the
#: fill it introduces, on every ground an author can drop a promo onto. 4.5 =
#: normal text, 3.0 = a graphical object.
#:
#: The dark slot is absent from the fill rows on purpose, and its own test
#: below says why. It IS present as a text row: on that slot Blicca flattens
#: every colour under the band to `--aurora-block-fg-dark` at (0,3,0), so the
#: button's label is the band's foreground however `--promo-cta-fg` is set
#: (the block's README, "Two documented interactions"; ticket 13 asked for the
#: copper to be measured against THAT ink). It lands at the same 4.60:1,
#: because both inks are near-white — the caveat is real and costs nothing.
PROMO_PAIRS = [
    # the button's label on its fill, and on the fill it hovers to
    ("--derico-on-copper", "--derico-copper", 4.5),
    ("--derico-on-copper", "--derico-copper-hover", 4.5),
    # the same label as the dark slot actually renders it
    ("--aurora-block-fg-dark", "--derico-copper", 4.5),
    ("--aurora-block-fg-dark", "--derico-copper-hover", 4.5),
    # the button as a graphical object against every light ground
    ("--derico-copper", "--derico-ground", 3.0),
    ("--derico-copper", "--aurora-block-bg-grey", 3.0),
    ("--derico-copper", "--aurora-block-bg-accent", 3.0),
    ("--derico-copper-hover", "--derico-ground", 3.0),
    # the kicker, which is ordinary text and gets no help from a fill
    ("--derico-copper-text", "--derico-ground", 4.5),
    ("--derico-copper-text", "--aurora-block-bg-grey", 4.5),
    ("--derico-copper-text", "--aurora-block-bg-accent", 4.5),
]


@needs_clara
@pytest.mark.parametrize(("foreground", "background", "minimum"), PROMO_PAIRS)
def test_promo_contrast(foreground, background, minimum):
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
def test_the_copper_button_does_not_outline_itself_against_the_dark_slot():
    """The one measurement that fails, stated as a measurement (ticket 16).

    A copper pill on the deep-petrol band is 2.24:1 fill-against-ground, under
    the 3:1 a graphical object wants. It ships anyway, and this test is where
    that is admitted rather than left out of the table above:

    * the control is identified by its label, which clears AA on the fill at
      4.60:1 — it is not a shape the reader has to find an edge for;
    * the theme's existing tables make the same call. `--clara-amber` is held
      to 3:1 against the page, the grey slot and the accent slot, and against
      the dark slot by nothing — a copper button on petrol predates the promo;
    * the alternative is `--promo-cta-border`, which is one global property for
      one slot: a near-white ring on every promo button everywhere, to fix the
      one ground where the band already frames it.

    Written inverted so it fails if the situation changes — if copper lightens
    or the dark slot lifts far enough to clear 3:1, the omission above is no
    longer a choice and the row can simply join `PROMO_PAIRS`.
    """
    props = _effective()
    fill = css_tools.to_hex(css_tools.resolve("--derico-copper", props))
    band = css_tools.to_hex(css_tools.resolve("--aurora-block-bg-dark", props))
    label = css_tools.to_hex(css_tools.resolve("--aurora-block-fg-dark", props))
    assert css_tools.contrast(label, fill) >= 4.5, (
        "the label is what identifies the button on the dark slot; if it stops "
        "clearing AA the button has nothing left"
    )
    assert css_tools.contrast(fill, band) < 3.0, (
        "the copper fill now clears 3:1 against the dark slot; add "
        "('--derico-copper', '--aurora-block-bg-dark', 3.0) to PROMO_PAIRS and "
        "delete this test"
    )
