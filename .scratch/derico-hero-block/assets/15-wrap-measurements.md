# Ticket 15 — wrap and overflow measurements

Measured 2026-08-25 against the **design source** served over HTTP
(`docs/design/derico.de/site/de/index.html`), headless Chromium 151, no Plone
instance running. Line boxes read with a `Range` walked character by character,
so `lines` below is what the browser actually laid out, not an inference.

Two headlines: the shipped one, and `Geschäftsanwendungen, die bleiben.` as a
long-compound stress case an author could plausibly type.

## 1. The overflow is a grid blowout

`.home-hero__grid > div` (the copy cell) is a grid item, so its automatic
minimum size is `min-content` — the longest word. It does not stay inside the
shell:

| viewport | shell | copy cell, shipped headline | copy cell, compound |
|---|---|---|---|
| 320 | 288 | **320** | **383** |

The cell is the thing that sticks out past the shell; the hero's
`overflow: hidden` then cuts it. `min-width: 0` on the cell pins it to the
column exactly (228 / 288 measured) in every configuration below.

The mockup already does this at ≥56rem — `grid-template-columns: minmax(0,
1.02fr) minmax(24rem, 0.98fr)` — and only there. The single-column range
never got it.

## 2. `overflow-wrap: break-word` alone does not fix it

`break-word` changes line breaking but does **not** feed intrinsic sizing, so
the cell still blows out. `overflow-wrap: anywhere` does feed intrinsic sizing
and is therefore itself a pin.

Copy column forced to the width shown; `over` is the widest line minus that
width (positive = past the column).

| headline | col | config | cell | over | lines |
|---|---|---|---|---|---|
| shipped | 228 | `normal` (mockup) | 320 | +92 | `Anwendungen,` / `die bleiben.` |
| shipped | 228 | `break-word` | **320** | +92 | `Anwendungen,` / `die bleiben.` |
| shipped | 228 | `min-width:0` + `normal` | 228 | +92 | `Anwendungen,` / `die` / `bleiben.` |
| shipped | 228 | `min-width:0` + `break-word` | 228 | −26 | `Anwendu` / `ngen, die` / `bleiben.` |
| shipped | 228 | `anywhere` (no pin) | 228 | −26 | `Anwendu` / `ngen, die` / `bleiben.` |
| compound | 288 | `normal` (mockup) | 383 | +229 | `Geschäftsanwendungen,` / `die bleiben.` |
| compound | 288 | `break-word` | **383** | +83 | `Geschäftsanwend` / `ungen, die` / `bleiben.` |
| compound | 288 | `min-width:0` + `break-word` | 288 | −26 | `Geschäftsan` / `wendungen,` / `die bleiben.` |
| compound | 288 | `anywhere` (no pin) | 288 | −26 | `Geschäftsan` / `wendungen,` / `die bleiben.` |

`anywhere` and `min-width:0` + `break-word` produced **identical** wraps in all
8 cases.

## 3. `hyphens: auto` is a no-op in this Chromium

A 120px box, 20px serif, `hyphens: auto`, four probes — every one stayed on a
single line and overflowed:

| lang | word | height | width in a 120px box |
|---|---|---|---|
| `de` | Anwendungsentwicklung | 23 (one line) | 204 |
| `en` | Anwendungsentwicklung | 23 (one line) | 204 |
| `en` | extraordinarily | 23 (one line) | 120 |
| `de` | Silbentrennung | 23 (one line) | 122 |

No hyphenation dictionaries in the container. Nothing here can assert
hyphenation *renders*; a test can only assert the declaration is present.

## 4. A lower size floor helps the shipped headline, not the compound

`over` against the column shown, `overflow-wrap: normal`:

| headline | col | 2.75rem (44px) | 2.4rem (38.4px) | 2.0rem (32px) |
|---|---|---|---|---|
| shipped | 288 (320 view) | +32 | **−9** | −55 |
| shipped | 228 (320 canvas) | +92 | +51 | +5 |
| compound | 288 | +229 | +163 | +88 |

So *a size of* 2.4rem clears the shipped headline at a 320 public view with 9px
to spare, and nothing plausible clears the compound — which is why size is a
voice rung, never the guarantee.

**Correction — lowering the clamp's floor does not produce that size.** The
table above forces `font-size` directly. `clamp(2.4rem, 1.85rem + 4vw, 5rem)`
at a 320 viewport returns its *middle* term, 42.4px, because the middle term is
already above the floor there; only below ~315px does the floor bind at all.
The old 2.75rem floor did bind (44px). So lowering the floor alone moves 320
from 44px to 42.4px, the word still needs 308px in a 288px column, and the
headline still falls to rung 2. Measured after applying it: `Anwendunge` /
`n, die bleiben.`

Fitting at 320 therefore requires a new **slope**, not a new floor — see §7.

`Anwendungen,` measured in the 288px column:

| size | word | fits 288 |
|---|---|---|
| 36.8px | 268 | yes |
| 38.4px (2.4rem) | 279 | yes, 9px slack |
| 39.6px | 288 | exactly |
| 41px | 298 | no |
| 42.4px | 308 | no |
| 44px (today) | 320 | no |

## 5. Desktop is untouched by any of it

At a 1440 viewport, copy column 590, `14.5ch` = 590, `--text-display` capped at
5rem = 80px. All five configurations — baseline, `hyphens`, `break-word`,
`hyphens`+`break-word`, and `text-wrap: wrap` + both — produced the **same**
two lines:

```
Anwendungen,   582px
die bleiben.   442px
```

582 in a 590 box: **8px** of slack.

This corrects ticket 07, which attributed the canvas's differing 1440 wrap
(`Anwendungen` / `, die bleiben.`) to `overflow-wrap: break-word`. Break-word
does not change the desktop wrap; the co-inherited `white-space: pre-wrap`
does. That is what makes the break-word rung safe at desktop.

## 6. The hero box is not the viewport whenever a toolbar is present

From ticket 07's table: `.block.block-derico-hero.has--block-width--full`
measures **1220 @220** on the public view and 1134.9 @262.5 in the canvas at a
1440 viewport — the `@220` is the Plone toolbar. So a `vw`-based type ramp
sizes the headline against a box the page does not have, for every logged-in
user, on both surfaces. Hence `cqi`.

## 7. Choosing the ramp

Computed px per viewport for the candidates:

| ramp | 320 | 375 | 500 | 768 | 1024 | 1220 | 1440 |
|---|---|---|---|---|---|---|---|
| today `1.85rem + 4vw`, floor 2.75 | 44 | 44.6 | 49.6 | 60.3 | 70.6 | 78.4 | 80 |
| A — floor 2.4 only | 42.4 | 44.6 | 49.6 | 60.3 | 70.6 | 78.4 | 80 |
| B — `1.5rem + 4vw`, floor 2.4 | 38.4 | 39 | 44 | 54.7 | 65 | 72.8 | 80 |
| **C — `1.4rem + 5vw`, floor 2.4** | **38.4** | 41.2 | 47.4 | **60.8** | 73.6 | **80** | 80 |

**C chosen.** A does not fit at 320. B buys the fit by shrinking the whole
mid-range ~9% — 768 loses 5.6px — paying at every width for a defect at one.
C tracks today's ramp where the design is usually seen (60.8 against 60.3 at
768), runs 4% larger at 1024, and reaches the 5rem cap at a **1152px** box
rather than 1260 — which under `cqi` means a logged-in editor's 1220px hero
gets the full 80px instead of 78.4.

## 8. The design source after the fix

`docs/design/.../assets/site.css`, verified in the same browser:

| viewport | size | copy cell | hero overflow | doc overflow | headline |
|---|---|---|---|---|---|
| 320 | 38.4px | 288 (was 320) | **0** | **0** | `Anwendungen,` / `die bleiben.` |
| 320, compound | 38.4px | 288 (was 383) | **0** | **0** | `Geschäftsanwe` / `ndungen, die` / `bleiben.` |
| 1440 | 80px | 590 | 0 | 0 | `Anwendungen,` / `die bleiben.` — **unchanged** |

The shipped headline keeps the mockup's own two-line composition at 320 with no
break and no clip; the invented compound falls to rung 2, which is the ladder
working as designed.
