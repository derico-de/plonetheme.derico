"""The theme's central claim: derico overrides Clara only where it must.

`static/derico.css` is the whole theme. These tests are the guard that keeps it
that way — they fail when the sheet grows a component rule, when it re-states a
value Clara already has, when it names a token Clara does not define, and when
Clara drifts away from a value derico is currently relying on inheriting.

They parse text only: no Plone, no browser, no Sass.
"""

import re

import pytest

from . import clara_css as css_tools


DERICO = css_tools.DERICO_CSS.read_text()
CLARA_PATH = css_tools.clara_bundle_path()

needs_clara = pytest.mark.skipif(
    CLARA_PATH is None,
    reason="plonetheme.clara's compiled bundle is not available",
)
CLARA = CLARA_PATH.read_text() if CLARA_PATH else ""


def _derico_light():
    return css_tools.declarations(DERICO, css_tools.ROOT_SELECTORS)


def _derico_dark():
    return css_tools.declarations(DERICO, css_tools.DARK_SELECTORS)


def _clara_light():
    return css_tools.declarations(CLARA, css_tools.ROOT_SELECTORS)


def _effective_light():
    """Clara's tokens as derico leaves them: Clara's :root cascade, then ours."""
    props = _clara_light()
    props.update(_derico_light())
    return props


# --------------------------------------------------------------------------
# 1. Shape: a token sheet, and nothing else
# --------------------------------------------------------------------------

def test_sheet_declares_only_root_level_selectors():
    """No component rules, no element selectors — the customization contract."""
    selectors = {
        re.sub(r"\s+", " ", selector).strip()
        for selector, _ in css_tools._blocks(DERICO)
    }
    allowed = {":root", '[data-bs-theme="dark"]'}
    assert selectors <= allowed, (
        f"derico.css must stay a token sheet; found {sorted(selectors - allowed)}. "
        "A design change that needs a rule is a gap in Clara's token contract — "
        "fix it there, do not fork the component here."
    )


def test_sheet_declares_nothing_but_custom_properties():
    for _, body in css_tools._blocks(DERICO):
        for declaration in css_tools.strip_comments(body).split(";"):
            declaration = declaration.strip()
            if declaration:
                assert declaration.startswith("--"), (
                    f"non-token declaration in derico.css: {declaration!r}"
                )


def test_sheet_ships_no_second_stylesheet_machinery():
    """Clara owns @layer, Bootstrap and the fonts; derico must not restate them."""
    body = css_tools.strip_comments(DERICO)
    for forbidden in ("@layer", "@import", "@font-face", "!important"):
        assert forbidden not in body, f"derico.css must not use {forbidden}"


# --------------------------------------------------------------------------
# 2. Every override lands on something real
# --------------------------------------------------------------------------

@needs_clara
def test_every_override_targets_a_token_clara_defines():
    """A typo or a token Clara dropped would silently do nothing."""
    clara = _clara_light()
    unknown = [
        name
        for name in (_derico_light() | _derico_dark())
        if not name.startswith("--derico-") and name not in clara
    ]
    assert not unknown, (
        f"derico.css overrides tokens Clara does not define: {sorted(unknown)}"
    )


def test_every_derico_token_is_used():
    """The --derico-* ladder is vocabulary, not decoration."""
    body = css_tools.strip_comments(DERICO)
    declared = {
        name for name in _derico_light() if name.startswith("--derico-")
    }
    for name in sorted(declared):
        references = len(re.findall(rf"var\(\s*{re.escape(name)}\b", body))
        assert references >= 1, f"{name} is declared but never used"


# --------------------------------------------------------------------------
# 3. Nothing is overridden that did not need overriding
# --------------------------------------------------------------------------

@needs_clara
def test_no_override_restates_claras_own_value():
    """The core minimality claim.

    Resolve both sides to sRGB and compare. An override that lands on the value
    Clara already had is noise — it makes the sheet look like it is doing more
    work than it is, and it hides real drift when Clara moves.
    """
    clara = _clara_light()
    effective = _effective_light()
    redundant = []
    for name in _derico_light():
        if name.startswith("--derico-") or name not in clara:
            continue
        before = css_tools.to_hex(css_tools.resolve(name, clara))
        after = css_tools.to_hex(css_tools.resolve(name, effective))
        if before is not None and before == after:
            redundant.append(f"{name} (Clara already resolves to {before})")
    assert not redundant, "redundant overrides in derico.css: " + ", ".join(redundant)


@needs_clara
@pytest.mark.parametrize(
    "token",
    [
        # type — Clara's scale is already the Jahresringe scale, down to the
        # 15px label floor and the flat 1rem body
        "--plone-text-base",
        "--plone-font-body",
        "--clara-font-display",
        "--clara-text-label",
        "--clara-text-nav",
        "--clara-text-lede",
        "--clara-text-title",
        "--clara-text-heading",
        "--clara-text-display",
        "--plone-leading-body",
        # geometry
        "--plone-measure",
        "--plone-radius-m",
        "--plone-radius-pill",
        # the short end of the space scale
        "--plone-space-s",
        "--plone-space-m",
        "--plone-space-l",
        # the error family: the Jahresringe red IS Clara's red
        "--clara-error",
    ],
)
def test_token_is_deliberately_not_overridden(token):
    assert token not in _derico_light(), (
        f"{token} is overridden but was documented as inherited — "
        "update derico.css's header comment and this list together"
    )


@needs_clara
@pytest.mark.parametrize(
    ("token", "expected"),
    [
        # The design source of record is
        # docs/design/derico.de/site/assets/site.css. These are
        # its values. Clara currently ships them verbatim, which is *why* derico
        # inherits them. If Clara retunes any of these, this test fails and the
        # token has to move into derico.css.
        ("--plone-text-base", "1rem"),
        ("--clara-text-label", "0.9375rem"),
        ("--clara-text-nav", "1.18125rem"),
        ("--clara-text-lede", "clamp(1.125rem, 1.06rem + 0.35vw, 1.35rem)"),
        ("--clara-text-title", "clamp(1.35rem, 1.2rem + 0.7vw, 1.75rem)"),
        ("--clara-text-heading", "clamp(2rem, 1.45rem + 2.3vw, 3.5rem)"),
        ("--clara-text-display", "clamp(2.75rem, 1.85rem + 4vw, 5rem)"),
        ("--plone-leading-body", "1.65"),
        ("--plone-measure", "76rem"),
        ("--plone-radius-m", "0.625rem"),
        ("--plone-space-s", "clamp(1.00rem, 0.96rem + 0.22vw, 1.25rem)"),
        ("--plone-space-m", "clamp(1.50rem, 1.43rem + 0.33vw, 1.88rem)"),
        ("--plone-space-l", "clamp(2.00rem, 1.91rem + 0.43vw, 2.50rem)"),
    ],
)
def test_inherited_value_still_matches_the_design(token, expected):
    actual = css_tools.resolve(token, _clara_light())
    assert actual is not None, f"{token} is gone from Clara"
    normalise = lambda text: re.sub(r"\s+", "", text)  # noqa: E731
    assert normalise(actual) == normalise(expected), (
        f"Clara moved {token} to {actual!r}; the Jahresringe design says "
        f"{expected!r}. derico must now override it."
    )


@needs_clara
def test_error_family_needs_no_override():
    """oklch(0.45 0.18 28) — the design's red — resolves to Clara's exact red."""
    clara_error = css_tools.to_hex(css_tools.resolve("--clara-error", _clara_light()))
    assert clara_error == css_tools.oklch_to_hex(0.45, 0.18, 28)


# --------------------------------------------------------------------------
# 4. Nothing that DID need overriding was missed
# --------------------------------------------------------------------------

@needs_clara
def test_no_plone_blue_survives_in_the_token_layer():
    """Every token derico's site resolves to must be off Clara's blue ladder.

    Catches the case where Clara pins a token to a literal blue instead of to a
    role — the ladder cannot reach those, and they have to be listed explicitly
    in derico.css (--plone-link-color-on-dark and --plone-state-published are
    the two that exist today).
    """
    klarsicht_blues = {
        "#0083be",
        "#006293",
        "#005c88",
        "#083148",
        "#65addc",
        "#8abfe2",
        "#ddeefa",
        "#b7ddf8",
        "#e5f4fb",
        "#eef6fc",
    }
    effective = _effective_light()
    leaked = {}
    for name in effective:
        # the --plone-blue-* primitive ramp is Clara's raw scale; it is not a
        # role and nothing derico's site paints with reads it directly
        if name.startswith("--plone-blue-"):
            continue
        value = css_tools.to_hex(css_tools.resolve(name, effective))
        if value in klarsicht_blues:
            leaked[name] = value
    assert not leaked, (
        "Clara's blue ladder still reaches these roles: "
        + ", ".join(f"{k}={v}" for k, v in sorted(leaked.items()))
    )


@needs_clara
def test_accent_role_is_copper_everywhere():
    effective = _effective_light()
    copper = css_tools.oklch_to_hex(0.57, 0.18, 50)
    copper_text = css_tools.oklch_to_hex(0.49, 0.18, 55)
    assert css_tools.to_hex(css_tools.resolve("--plone-color-accent", effective)) == copper
    assert (
        css_tools.to_hex(css_tools.resolve("--plone-color-accent-strong", effective))
        == copper_text
    )
    # Clara's amber hooks are what its components actually paint with
    assert css_tools.to_hex(css_tools.resolve("--clara-amber", effective)) == copper


@needs_clara
def test_cta_outline_is_the_copper_fill_not_klarsichts_ink():
    """The one deviation that used to need a component rule, now a token.

    Klarsicht rings its amber pill with an ink hairline; the Jahresringe button
    spec draws no border. Clara grew `--clara-button-border-color` for it, so
    derico closes the gap with one declaration instead of forking
    `.clara-button`. The border BOX stays (forced-colors, metrics) — the colour
    is the fill, so no outline reads.
    """
    effective = _effective_light()
    outline = css_tools.to_hex(
        css_tools.resolve("--clara-button-border-color", effective)
    )
    fill = css_tools.to_hex(css_tools.resolve("--clara-amber", effective))
    ink = css_tools.to_hex(css_tools.resolve("--clara-ink", effective))
    assert outline == fill, "the CTA outline must vanish into the copper fill"
    assert outline != ink, "Klarsicht's ink hairline is not part of Jahresringe"


@needs_clara
def test_primary_role_is_the_exact_brand_cyan():
    effective = _effective_light()
    assert css_tools.to_hex(
        css_tools.resolve("--plone-color-primary", effective)
    ) == "#039fba"


# --------------------------------------------------------------------------
# 5. Bootstrap's compile-time colour math must not outlive the token layer
# --------------------------------------------------------------------------

#: Bootstrap's component mixins bake `$primary` into a literal hex at Sass
#: compile time — `.pagination`'s active fill, `.nav-pills`, `.progress-bar`,
#: `.list-group`, `.dropdown-item.active`, the outline buttons, and the
#: form-control checked/indeterminate/thumb properties, several of which have
#: no `--bs-*` knob at all. No `:root` override can reach a literal, so before
#: Clara's bridge covered them a derico page rendered 13 Plone-blue spots
#: (measured live, 2026-07-28).
#:
#: The fix landed in Clara — `_clara-bridge.scss` §3 — not here, because every
#: theme on Clara hit the same wall (its architecture doc, principle 1). This
#: test is derico's stake in that fix: it fails if a rebuild of Clara ever
#: drops one of them again.
COMPILE_TIME_BLUE = {
    ".pagination": "--bs-pagination-active-bg",
    ".nav-pills": "--bs-nav-pills-link-active-bg",
    ".progress,.progress-stacked": "--bs-progress-bar-bg",
    ".list-group": "--bs-list-group-active-bg",
    ".dropdown-menu": "--bs-dropdown-link-active-bg",
    ".dropdown-menu-dark": "--bs-dropdown-link-active-bg",
    ".btn-outline-primary": "--bs-btn-color",
    ".btn-outline-info": "--bs-btn-color",
    ".form-check-input:checked": "background-color",
    ".form-check-input[type=checkbox]:indeterminate": "background-color",
    ".form-range::-webkit-slider-thumb": "background-color",
    ".form-range::-moz-range-thumb": "background-color",
}

KLARSICHT_BLUE = re.compile(r"#(0083be|65addc|006293|005c88|ddeefa|8abfe2)\b", re.I)


def _effective_declaration(css, selector, prop):
    """Last declaration of `prop` under `selector`, in document order.

    Layer order and document order agree in Clara's bundle (`bootstrap` is
    compiled in before the `components` layer that holds the bridge), so
    last-wins is a faithful model of the cascade for these rules.
    """
    wanted = {re.sub(r"\s+", "", part) for part in selector.split(",")}
    value = None
    for found_selector, body in css_tools._blocks(css):
        parts = {re.sub(r"\s+", "", part) for part in found_selector.split(",")}
        if not wanted & parts:
            continue
        for name, declared in re.findall(r"((?:--)?[a-zA-Z][\w-]*)\s*:\s*([^;}]+)", body):
            if name == prop:
                value = declared.strip()
    return value


@needs_clara
@pytest.mark.parametrize(("selector", "prop"), sorted(COMPILE_TIME_BLUE.items()))
def test_compile_time_blue_is_overridden_by_the_token_bridge(selector, prop):
    value = _effective_declaration(CLARA, selector, prop)
    assert value is not None, f"{selector} no longer declares {prop}"
    assert not KLARSICHT_BLUE.search(value), (
        f"{selector} {{{prop}: {value}}} is still Bootstrap's compiled Plone "
        "blue — Clara's bridge lost the rebind, and no token override can "
        "reach it. Fix plonetheme.clara/theme/scss/_clara-bridge.scss §3."
    )
    assert "var(--plone-" in value, (
        f"{selector} {{{prop}: {value}}} is a literal; it must read a token"
    )


@needs_clara
def test_focus_ring_is_derived_from_the_primary_token():
    """Bootstrap compiled `rgba($primary, .25)`; the bridge re-derives it."""
    value = _effective_declaration(CLARA, ":root", "--bs-focus-ring-color")
    assert value and "var(--plone-color-primary)" in value
