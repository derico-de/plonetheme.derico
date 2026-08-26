# What the hero's own photograph does to the rings disc

Measured while resolving [ticket 20](../issues/20-ring-stroke-non-text-contrast.md).

## Why this was measured

Ticket 20 inherited a two-column table from ticket 18: each ring stroke against
"a bright photograph" and against the same photograph under the 0.72 wash. Both
columns are hypotheticals. The question that decides how the fix is tested is a
different one — **what does the photograph the block actually ships with do?** —
and nobody had asked it.

The expectation going in was that the fixture forest is uniformly dark, that the
strokes therefore pass over it, and that demonstrating any fix would need a
synthetic bright image added to the e2e. That expectation was wrong.

## The inks

| | value | relative luminance |
| --- | --- | --- |
| `--derico-hero-ring` (copper) | `oklch(0.82 0.13 65)` | `Y = 0.5365` |
| `--derico-hero-ring-now` (brand cyan) | `#039fba` = `oklch(0.64705 0.1142 215.55)` | `Y = 0.2836` |
| `--derico-hero-ground` | `oklch(0.18 0.035 215)` | `Y = 0.0062` |
| `--derico-hero-ink` | `oklch(0.99 0.004 215)` | `Y = 0.9714` |

Backdrop luminance admitting 3:1 — the WCAG 1.4.11 threshold:

| stroke | passes when the backdrop is |
| --- | --- |
| copper | `Y ≤ 0.1455`. The bright side would need `Y ≥ 1.7095`, which does not exist. |
| cyan | `Y ≤ 0.0612` **or** `Y ≥ 0.9508` |

So copper can only ever pass over a *dark* backdrop, and cyan fails across
almost the whole range — ticket 18's `3.15` was measured against pure white,
which no photograph is.

Ground beats both: **ground vs copper 10.43**, **ground vs cyan 5.93**. A light
halo is arithmetically dead — copper against `--derico-hero-ink` is **1.74**.
A translucent ground halo would need `α ≥ 0.6252` (copper) and `α ≥ 0.7796`
(cyan) over a white photograph.

## The photograph

`docs/design/derico.de/site/assets/images/hero-managed-forest-wide-2400.jpg`,
2400x1200 — the design source's image and the e2e fixture's upload. Per-pixel
relative luminance, sampled every 2px:

| region | median | p95 | p99 | max | fails copper 3:1 | fails cyan 3:1 |
| --- | --- | --- | --- | --- | --- | --- |
| whole image | 0.0153 | 0.219 | 0.567 | 0.998 | 7.37% | 16.25% |
| right half | 0.0126 | 0.166 | 0.439 | 0.881 | 5.65% | 13.28% |
| rings band | 0.0116 | 0.103 | 0.340 | 0.815 | 3.28% | **10.27%** |

"Rings band" is `x ∈ [0.55, 0.95]`, `y ∈ [0.05, 0.95]` of the image — the part
the disc sits over at wide. The forest *is* dark at the median; the canopy gaps
are not.

**Two conclusions.** The disc fails 1.4.11 over the shipped design photograph
today, present tense, not only over a future bright upload. And the existing
fixture can demonstrate the fix — no synthetic bright image is needed.

**The honest limit**: this is the share of the *band*, not of pixels adjacent to
a stroke. Ticket 10's lesson — report the share, not the worst pixel — applies
to this number too. Measuring along the stroke paths belongs to the build.

## Method

Headless Chromium via the e2e checkout's `playwright-core`, image drawn to a
canvas and read back, so the numbers come from the same decoder the browser
uses. Serve the image directory first — Playwright blocks `file://`.

```sh
cd docs/design/derico.de/site/assets/images && python3 -m http.server 8791 &
node measure-forest.mjs 8791
```

```js
import { chromium } from '<repo>/e2e/node_modules/playwright-core/index.mjs';

const PORT = process.argv[2];
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium' });
const page = await browser.newPage();
await page.goto(`http://127.0.0.1:${PORT}/`);

const out = await page.evaluate(async (port) => {
  const image = new Image();
  image.src = `http://127.0.0.1:${port}/hero-managed-forest-wide-2400.jpg`;
  await image.decode();
  const c = document.createElement('canvas');
  c.width = image.width; c.height = image.height;
  const ctx = c.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(image, 0, 0);
  const { data } = ctx.getImageData(0, 0, c.width, c.height);

  const ch = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const ratio = (a, b) => { const [hi, lo] = a > b ? [a, b] : [b, a]; return (hi + 0.05) / (lo + 0.05); };
  const COPPER = 0.5365, CYAN = 0.2836;

  const regions = {
    whole: [0, 0, c.width, c.height],
    rightHalf: [Math.floor(c.width / 2), 0, c.width, c.height],
    ringsBand: [Math.floor(c.width * 0.55), Math.floor(c.height * 0.05),
                Math.floor(c.width * 0.95), Math.floor(c.height * 0.95)],
  };
  const result = {};
  for (const [name, [x0, y0, x1, y1]] of Object.entries(regions)) {
    const ys = [];
    for (let y = y0; y < y1; y += 2) for (let x = x0; x < x1; x += 2) {
      const i = (y * c.width + x) * 4;
      ys.push(0.2126 * ch(data[i]) + 0.7152 * ch(data[i + 1]) + 0.0722 * ch(data[i + 2]));
    }
    ys.sort((a, b) => a - b);
    const q = (p) => ys[Math.min(ys.length - 1, Math.floor(p * ys.length))];
    result[name] = {
      n: ys.length, min: +q(0).toFixed(4), p50: +q(0.5).toFixed(4),
      p95: +q(0.95).toFixed(4), p99: +q(0.99).toFixed(4), max: +q(0.9999).toFixed(4),
      copperFailPct: +(100 * ys.filter((y) => ratio(COPPER, y) < 3).length / ys.length).toFixed(2),
      cyanFailPct: +(100 * ys.filter((y) => ratio(CYAN, y) < 3).length / ys.length).toFixed(2),
    };
  }
  return result;
}, PORT);

console.log(JSON.stringify(out, null, 2));
await browser.close();
```
