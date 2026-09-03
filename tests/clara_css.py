"""Read Clara's shipped bundle and resolve its effective token values.

The tests deliberately parse `clara.min.css` — the artifact the browser gets —
rather than Clara's Sass sources. What derico has to override is decided by
what actually lands in the page, not by how Clara chose to author it.

Cascade model, and why a plain document-order overlay is enough here:

* Clara declares its tokens in `@layer tokens`, its toolbar knobs in
  `@layer components`. Both use `:root` (specificity 0,1,0), and in the bundle
  the `tokens` blocks precede the `components` block, so document order and
  layer order agree — overlaying blocks in the order they appear yields the
  effective value.
* `[data-bs-theme=dark]` is also 0,1,0, so it never beats a *later* `:root`.
  That is a real property of the shipped cascade, not a simplification — see
  the dark-mode finding in README.md.
* derico.css is unlayered, so every declaration in it beats every layered
  Clara declaration regardless of file order.
"""

import math
import re
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
STATIC = PACKAGE / "src" / "plonetheme" / "derico" / "static"
DERICO_CSS = STATIC / "derico.css"
BLOCK_STATIC = PACKAGE / "src" / "plonetheme" / "derico" / "static-blocks"


def theme_stylesheets():
    """The theme's hand-written sheets other than the token layer.

    `snippets.css` today: derico's own markup, delivered as its own bundle
    precisely because derico.css is guarded to stay a token sheet. Globbed
    rather than listed, so the next one joins the corpus by existing — a sheet
    outside it could name a `--clara-*` token or read a token nothing else
    reads, and both guards would go on passing.
    """
    return sorted(path for path in STATIC.glob("*.css") if path != DERICO_CSS)


def block_stylesheets():
    """The brand blocks' scope-wrapped sheets, if `bundle-src` has built them.

    `static-blocks/` is build output served as `++plone++plonetheme.derico.blocks`
    (hero ticket 04 §3) and it is committed, so a normal checkout has it — but
    it does not exist at all until the first block entry point lands, and Vite
    empties it on every build. Callers treat "absent" as "no block sheets yet",
    never as an error.
    """
    if not BLOCK_STATIC.is_dir():
        return []
    return sorted(BLOCK_STATIC.glob("*.css"))


def clara_bundle_path():
    """Locate Clara's compiled bundle: installed package first, checkout second."""
    try:
        import plonetheme.clara as clara_package

        candidate = Path(clara_package.__file__).parent / "static" / "clara.min.css"
        if candidate.is_file():
            return candidate
    except ImportError:
        pass
    candidate = (
        PACKAGE
        / "sources"
        / "plonetheme.clara"
        / "src"
        / "plonetheme"
        / "clara"
        / "static"
        / "clara.min.css"
    )
    return candidate if candidate.is_file() else None


# --------------------------------------------------------------------------
# CSS parsing
# --------------------------------------------------------------------------

def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _blocks(css):
    """Yield (selector, body) for every top-level-ish rule, @layer/@media flattened.

    Good enough for token sheets: we only care about `:root`-shaped rules and
    their custom-property declarations, never about nesting semantics.
    """
    css = strip_comments(css)
    index = 0
    while True:
        brace = css.find("{", index)
        if brace == -1:
            return
        selector = css[index:brace].strip().strip("}").strip()
        selector = selector.rsplit("}", 1)[-1].strip()
        if selector.startswith(
            ("@layer", "@media", "@supports", "@scope", "@container")
        ):
            # descend into the at-rule body. `@container` was missing until
            # hero ticket 21: the hero's whole responsive half lives in
            # `@container (min-width: 56rem)` (ticket 06 §8 chose a container
            # query over a media query deliberately), so every rule at the wide
            # breakpoint was invisible to these tests — they read as covering
            # the sheet while covering only half of it.
            index = brace + 1
            continue
        depth, end = 0, None
        for position in range(brace, len(css)):
            if css[position] == "{":
                depth += 1
            elif css[position] == "}":
                depth -= 1
                if depth == 0:
                    end = position
                    break
        if end is None:
            return
        yield selector, css[brace + 1 : end]
        index = end + 1


def rules(css):
    """Every STYLE rule in `css` as (selector, body), at-rules flattened.

    The block sheets need this: `_blocks` was written for token sheets, where
    the only question is what `:root` declares, but a block's sheet is all
    ordinary rules and they arrive wrapped in the `@scope` that packaging adds.

    At-rules that are not style rules — `@keyframes` above all, whose `from`
    and `to` blocks have no selector to speak of — are dropped here rather than
    at each call site.
    """
    for selector, body in _blocks(css):
        if not selector.startswith("@"):
            yield selector, body


def normalise_selector(selector):
    """One selector, whitespace-collapsed, for comparing against a literal."""
    return re.sub(r"\s+", " ", selector).strip()


BLOCK_SHEETS = block_stylesheets()

needs_block_sheets = pytest.mark.skipif(
    not BLOCK_SHEETS,
    reason="no brand-block stylesheet is built yet (bundle-src/ output)",
)


def declarations(css, selectors):
    """Custom properties declared by `selectors`, in cascade (document) order."""
    wanted = {re.sub(r"\s+", "", s) for s in selectors}
    found = {}
    for selector, body in _blocks(css):
        parts = {re.sub(r"\s+", "", p) for p in selector.split(",")}
        if not parts & wanted:
            continue
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;}]+)", body):
            found[name] = value.strip()
    return found


ROOT_SELECTORS = (":root", '[data-bs-theme="light"]', "[data-bs-theme=light]")
DARK_SELECTORS = ('[data-bs-theme="dark"]', "[data-bs-theme=dark]")


def resolve(name, props, seen=None):
    """Follow var() indirection to a literal, honouring the fallback argument."""
    seen = set() if seen is None else seen
    if name in seen or name not in props:
        return None
    seen = seen | {name}
    value = props[name].strip()
    match = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,\s*(.+?)\s*)?\)", value, re.DOTALL)
    if not match:
        return value
    resolved = resolve(match.group(1), props, seen)
    if resolved is not None:
        return resolved
    fallback = match.group(2)
    return fallback.strip() if fallback else None


# --------------------------------------------------------------------------
# Colour: oklch()/hex -> sRGB hex, and WCAG contrast
# --------------------------------------------------------------------------

_OKLAB_TO_LMS = (
    (1.0, 0.3963377773761749, 0.2158037573099136),
    (1.0, -0.1055613458156586, -0.0638541728258133),
    (1.0, -0.0894841775298119, -1.2914855480194092),
)
_LMS_TO_LINEAR_RGB = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _gamma(value):
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def oklch_to_hex(lightness, chroma, hue):
    radians = math.radians(hue)
    lab = (lightness, chroma * math.cos(radians), chroma * math.sin(radians))
    lms = [sum(row[i] * lab[i] for i in range(3)) ** 3 for row in _OKLAB_TO_LMS]
    linear = [sum(row[i] * lms[i] for i in range(3)) for row in _LMS_TO_LINEAR_RGB]
    srgb = [min(1.0, max(0.0, _gamma(channel))) for channel in linear]
    return "#" + "".join(f"{round(channel * 255):02x}" for channel in srgb)


def to_hex(value):
    """Normalise a colour literal to #rrggbb, or None if it is not a colour."""
    if value is None:
        return None
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return value
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(channel * 2 for channel in value[1:])
    match = re.fullmatch(
        r"oklch\(\s*([\d.]+)%?\s+([\d.]+)\s+([\d.]+)\s*\)", value
    )
    if match:
        lightness = float(match.group(1))
        if "%" in value.split()[0]:
            lightness /= 100
        return oklch_to_hex(lightness, float(match.group(2)), float(match.group(3)))
    return None


def luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)
