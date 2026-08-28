"""The theme's central claim: derico overrides Clara only where it must.

`static/derico.css` is the whole theme. These tests are the guard that keeps it
that way — they fail when the sheet grows a component rule, when it re-states a
value Clara already has, when it names a token Clara does not define, and when
Clara drifts away from a value derico is currently relying on inheriting.

They parse text only: no Plone, no browser, no Sass.

Scope: these tests guard `static/derico.css`. Since the theme grew brand
blocks, that is no longer all the CSS the theme ships — each block's own
scope-wrapped sheet under `static-blocks/` is a different file with different
rules, and a green run here is a claim about the token layer, not about the
whole theme. The two places the block sheets do appear below are the corpus
for token usage, and the seam guard that keeps them off `--clara-*`.
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

BLOCK_SHEETS = css_tools.block_stylesheets()

needs_block_sheets = css_tools.needs_block_sheets

#: The one non-token rule `derico.css` is allowed to carry: the page chrome
#: above a brand block (derico.css §7). It styles the page AROUND a block,
#: which the block's own sheet cannot reach — `scope-wrap.ts` rewrites `body`
#: to `:where(:scope)`. Matched structurally rather than as a literal string,
#: so reformatting the sheet does not break the guard while any OTHER
#: component rule still does.
CHROME_PREFIX = (
    "body:has(.aurora-blocks-view > .block:first-child.block-derico-hero)"
)
CHROME_TARGETS = {
    ".element-breadcrumbs",
    ".element-contentheader",
    ".element-byline",
    "#section-byline",
}

#: Tokens `derico.css` publishes FOR the brand-block sheets rather than using
#: itself: Clara's private type tokens, re-exported under a `--derico-*` name
#: so a block sheet speaks one vocabulary and a Clara rename breaks one file
#: (hero ticket 06 §3). They read as declared-but-unused until a block sheet
#: exists to consume them, which is why they are exempted below and checked
#: by their own test instead.
PUBLISHED_TO_BLOCK_SHEETS = {
    "--derico-text-lede",
    "--derico-text-label",
    "--derico-font-display",
}


_normalise = css_tools.normalise_selector


def _is_chrome_suppression(selector):
    """True for the §7 rule, and for nothing that merely resembles it."""
    parts = [part.strip() for part in _normalise(selector).split(",")]
    if not parts or any(not part for part in parts):
        return False
    return all(
        part.startswith(CHROME_PREFIX)
        and part[len(CHROME_PREFIX) :].strip() in CHROME_TARGETS
        for part in parts
    )


def _block_sheet_text():
    return "\n".join(
        css_tools.strip_comments(path.read_text()) for path in BLOCK_SHEETS
    )


def _stylesheet_corpus():
    """Every stylesheet this package ships: the token layer plus the blocks."""
    return "\n".join([css_tools.strip_comments(DERICO), _block_sheet_text()])


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
    """No component rules, no element selectors — the customization contract.

    One exception, and it is not a loophole: the §7 chrome-suppression rule
    styles the page AROUND a brand block, which the block's own scope-wrapped
    sheet is structurally unable to reach. Every other rule is still a gap in
    Clara's token contract.
    """
    selectors = {
        _normalise(selector) for selector, _ in css_tools._blocks(DERICO)
    }
    allowed = {":root", '[data-bs-theme="dark"]'}
    offenders = sorted(
        selector
        for selector in selectors
        if selector not in allowed and not _is_chrome_suppression(selector)
    )
    assert not offenders, (
        f"derico.css must stay a token sheet; found {offenders}. "
        "A design change that needs a rule is a gap in Clara's token contract — "
        "fix it there, do not fork the component here. The one exception is "
        "the page chrome around a brand block, which no block sheet can reach."
    )


def test_sheet_declares_nothing_but_custom_properties():
    """...and the one rule that does paint may only hide, never style."""
    for selector, body in css_tools._blocks(DERICO):
        declarations = [
            declaration.strip()
            for declaration in css_tools.strip_comments(body).split(";")
            if declaration.strip()
        ]
        if _is_chrome_suppression(selector):
            assert declarations == ["display: none"], (
                "the chrome-suppression rule may only remove chrome; it "
                f"declares {declarations}. Anything else is a component rule "
                "wearing its selector."
            )
            continue
        for declaration in declarations:
            assert declaration.startswith("--"), (
                f"non-token declaration in derico.css: {declaration!r}"
            )


def test_the_chrome_rule_is_present_and_stays_narrow():
    """Exactly one chrome rule, admitted by a guard that has not widened.

    The two assertions are on CHROME_PREFIX rather than on the matched
    selector — asserting the latter would be circular, since nothing reaches
    them unless the prefix already matched. The prefix is the part that can
    quietly drift: loosen it and `_is_chrome_suppression` waves through a rule
    that also strips the editing canvas, or one that fires for a hero sitting
    anywhere on the page.
    """
    assert ".aurora-blocks-view" in CHROME_PREFIX, (
        "the chrome rule must key on the public blocks view, which "
        "@@aurora-edit does not emit — the canvas is a working surface, where "
        "the title and breadcrumbs orient the author (hero ticket 06 §1)"
    )
    assert ":first-child" in CHROME_PREFIX, (
        "the chrome only goes when the hero OPENS the page; a hero further "
        "down the page leaves the breadcrumbs and title alone"
    )
    matched = [
        selector
        for selector, _ in css_tools._blocks(DERICO)
        if _is_chrome_suppression(selector)
    ]
    assert len(matched) == 1, (
        f"expected exactly one chrome-suppression rule, found {len(matched)}"
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
    """A typo or a token Clara dropped would silently do nothing.

    Clara is no longer the only upstream this sheet writes to: Blicca
    publishes the `--aurora-block-*` palette hooks (derico.css §8), and those
    names are of course absent from Clara's bundle. They are exempted here and
    checked against Blicca's own published slot list by
    `test_aurora_block_backgrounds.py` — the exemption widens which upstream
    may own a name, not whether one has to.
    """
    clara = _clara_light()
    unknown = [
        name
        for name in (_derico_light() | _derico_dark())
        if not name.startswith(("--derico-", "--aurora-")) and name not in clara
    ]
    assert not unknown, (
        f"derico.css overrides tokens Clara does not define: {sorted(unknown)}"
    )


def test_every_derico_token_is_used():
    """The --derico-* ladder is vocabulary, not decoration.

    The corpus is every stylesheet the theme ships — the token layer plus the
    brand blocks' sheets — because since the blocks arrived, a token declared
    here may legitimately be read only over there. The four tokens published
    FOR those sheets are exempt and have their own test: they would read as
    dead until the first block is built.
    """
    corpus = _stylesheet_corpus()
    declared = {
        name for name in _derico_light() if name.startswith("--derico-")
    }
    for name in sorted(declared - PUBLISHED_TO_BLOCK_SHEETS):
        references = len(re.findall(rf"var\(\s*{re.escape(name)}\b", corpus))
        assert references >= 1, f"{name} is declared but never used"


def test_published_aliases_are_aliases_of_claras_own_tokens():
    """derico.css is the theme's one seam onto Clara, in both directions.

    Each published token must BE an alias — a bare `var(--clara-*)` — and not
    a value of its own. A value would fork Clara's type scale silently; an
    alias means a Clara rename breaks this file and nothing else.
    """
    light = _derico_light()
    for name in sorted(PUBLISHED_TO_BLOCK_SHEETS):
        assert name in light, (
            f"{name} is published for the block sheets but derico.css does "
            "not declare it"
        )
        assert re.fullmatch(r"var\(\s*--clara-[\w-]+\s*\)", light[name]), (
            f"{name} must alias a --clara-* token verbatim, not restate a "
            f"value; it declares {light[name]!r}"
        )


@needs_clara
def test_published_aliases_still_point_at_something_clara_defines():
    """A Clara rename must fail loudly here, not resolve to nothing in a block."""
    clara = _clara_light()
    light = _derico_light()
    missing = []
    for name in sorted(PUBLISHED_TO_BLOCK_SHEETS):
        target = re.findall(r"--clara-[\w-]+", light.get(name, ""))
        if not target or target[0] not in clara:
            missing.append(f"{name} -> {target[0] if target else '?'}")
    assert not missing, (
        "these aliases point at tokens Clara no longer defines: "
        + ", ".join(missing)
    )


@needs_block_sheets
def test_published_aliases_reach_a_block_sheet():
    """Published, not hoarded: an alias nobody reads is dead weight."""
    corpus = _block_sheet_text()
    for name in sorted(PUBLISHED_TO_BLOCK_SHEETS):
        references = len(re.findall(rf"var\(\s*{re.escape(name)}\b", corpus))
        assert references >= 1, (
            f"{name} is published for the block sheets and none of them reads "
            "it — either a block should use it, or it should not be published"
        )


@needs_block_sheets
def test_block_sheets_never_name_a_clara_token():
    """The reason the aliases exist (hero ticket 06 §3).

    A block sheet speaks `--derico-*` and `--plone-*` only. If it reached for
    `--clara-*` directly, a Clara rename would break every block sheet instead
    of this one file, and the seam would be a seam in name only.
    """
    leaked = {}
    for path in BLOCK_SHEETS:
        names = sorted(
            set(re.findall(r"--clara-[\w-]+", css_tools.strip_comments(path.read_text())))
        )
        if names:
            leaked[path.name] = names
    assert not leaked, (
        "block stylesheets must not name Clara's tokens directly; re-publish "
        f"them through derico.css instead: {leaked}"
    )


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
