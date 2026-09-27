/* E2E: the Derico Hero's published page against the design source.
 *
 * Loads the mockup — `docs/design/derico.de/site/de/index.html`, served from
 * this repository over a throwaway origin — and the published Plone page side
 * by side in one browser, at 1440 / 900 / 375 / 320, and compares the boxes
 * the design fixes. The comparison is the point: "matches the mockup" is a
 * claim about two renderings, and a number copied into a test from a session
 * six weeks ago is not evidence about either.
 *
 * The page is browsed ANONYMOUSLY. The hero is `blockWidth: full` and the
 * breakout subtracts `--plone-toolbar-width`, so a logged-in measurement is
 * viewport-minus-toolbar (1220 at 1440) and would compare
 * a narrower hero against a full-width mockup.
 *
 * Prerequisites: a running Plone with plonetheme.derico installed at profile
 * version 1001+ and plone.restapi. The editor is never loaded, so the mockup
 * bundle is not needed.
 *
 * Environment: DERICO_E2E_BASE (default http://127.0.0.1:8081/Plone),
 * DERICO_E2E_USER / DERICO_E2E_PASSWORD, DERICO_E2E_CHROMIUM.
 *
 * Run: node hero-view.e2e.js
 */
const { chromium } = require('playwright-core');

const {
  MOCKUP,
  PLONE,
  contrastReport,
  measure,
  pictureOf,
  serveStatic,
} = require('./hero-measure');
const { DESIGN_ROOT, buildFixture, removeFixture } = require('./hero-fixture');

const BASE = (
  process.env.DERICO_E2E_BASE ||
  process.env.AURORA_E2E_BASE ||
  'http://127.0.0.1:8081/Plone'
).replace(/\/+$/, '');
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM || process.env.AURORA_E2E_CHROMIUM;

const VIEWPORTS = [1440, 900, 375, 320];

const TEXT_PARTS = [
  '.kicker',
  'h1',
  '.lede',
  '.button',
  '.quiet-link',
  '.ring-legend dt',
  '.ring-legend dd',
  '.ring-legend b',
];

/* `.ring-markers li` is deliberately NOT here: the numerals sit on an opaque
 * chip, never the photograph. Their contrast is pinned by
 * `test_the_marker_chips_carry_their_own_backdrop`. */

/* The share of a glyph's own pixels allowed to miss AA before the miss counts
 * as a contrast defect rather than as a speckle in a photograph. Measured:
 * the genuine failures sit at 44-87% of the glyph area, the speckles at 0.1%,
 * and nothing observed lands between 2% and 11%. */
const SPECKLE = 0.02;

/* No contrast exceptions: the legend card and copy scrim give every glyph a
 * declared ground. This proves glyphs SIT on it; the value test proves the
 * ground is strong enough. */

const failures = [];
function check(condition, message) {
  if (condition) {
    console.log(`  ok   ${message}`);
  } else {
    console.error(`  FAIL ${message}`);
    failures.push(message);
  }
}
function report(message) {
  console.log(`  note ${message}`);
}

const near = (a, b, tolerance = 1) =>
  typeof a === 'number' && typeof b === 'number' && Math.abs(a - b) <= tolerance;

(async () => {
  const fixture = await buildFixture(BASE);
  const design = await serveStatic(DESIGN_ROOT);
  const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
  /* A fresh context with no storage state: the published page has to be
   * readable by an anonymous visitor, and a leftover session would hide a
   * workflow mistake in the fixture. */
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push((error.stack || String(error)).slice(0, 400)));

  const mockupUrl = `${design.url}/de/index.html`;
  const heroUrl = `${BASE}${fixture.heroPage}`;

  try {
    for (const width of VIEWPORTS) {
      console.log(`\n# ${width}px`);
      await page.setViewportSize({ width, height: 900 });

      await page.goto(mockupUrl, { waitUntil: 'networkidle' });
      await page.waitForTimeout(300);
      const design_ = await measure(page, MOCKUP);

      await page.goto(heroUrl, { waitUntil: 'networkidle' });
      await page.waitForTimeout(300);
      const plone = await measure(page, PLONE);

      check(!!plone.parts.hero, 'the published page renders the hero');
      if (!plone.parts.hero) continue;

      /* -- the breakout ------------------------------------------------- */
      check(
        near(plone.parts.hero.width, width) && near(plone.parts.hero.left, 0),
        `the hero is full-bleed: ${plone.parts.hero.width} wide at ${plone.parts.hero.left}`,
      );
      check(
        plone.parts.hero.scrollWidth === plone.parts.hero.clientWidth,
        `the hero does not overflow itself (${plone.parts.hero.scrollWidth}/${plone.parts.hero.clientWidth})`,
      );
      check(
        plone.document.scrollWidth <= plone.document.clientWidth,
        `the page has no horizontal scroll (${plone.document.scrollWidth}/${plone.document.clientWidth})`,
      );

      /* -- the layout the container query decides ----------------------- */
      check(
        plone.columns === design_.columns,
        `the copy/figure grid has the mockup's ${design_.columns} column(s)`,
      );
      const tracks = (value) => (value || '').trim().split(/\s+/).map(parseFloat);
      const ploneTracks = tracks(plone.gridTemplateColumns);
      const designTracks = tracks(design_.gridTemplateColumns);
      check(
        ploneTracks.length === designTracks.length &&
          ploneTracks.every((track, index) => near(track, designTracks[index])),
        `the grid tracks match the mockup (${plone.gridTemplateColumns} vs ${design_.gridTemplateColumns})`,
      );

      /* -- the type scale ----------------------------------------------- */
      for (const part of ['kicker', 'headline', 'lede', 'legendCaption', 'legendTitle', 'marker']) {
        check(
          near(
            plone.parts[part] && plone.parts[part].fontSize,
            design_.parts[part] && design_.parts[part].fontSize,
            0.1,
          ),
          `${part} is set at the mockup's size (${plone.parts[part] && plone.parts[part].fontSize}px)`,
        );
      }
      check(
        plone.minFontSize >= 15,
        `no text under 15px — the smallest is ${plone.minFontSize}px on ${
          plone.smallestText[0] && plone.smallestText[0].tag
        }`,
      );

      /* -- the rings ---------------------------------------------------- */
      for (const part of ['stage', 'disc']) {
        check(
          near(plone.parts[part].width, design_.parts[part].width) &&
            near(plone.parts[part].height, design_.parts[part].height),
          `the ${part} matches the mockup (${plone.parts[part].width}x${plone.parts[part].height} vs ${design_.parts[part].width}x${design_.parts[part].height})`,
        );
      }
      check(
        near(plone.parts.marker.width, 28) && near(plone.parts.marker.height, 28),
        `the ring markers stay 28px (${plone.parts.marker.width}x${plone.parts.marker.height})`,
      );

      /* -- the body type ---------------------------------------------- */
      /* Blicca's `.aurora-blocks-view` Tailwind stack would win without the
       * hero's own declaration; `hero-editor.e2e.js` asserts the same pair. */
      const bodyType = await page.evaluate(() => {
        const style = getComputedStyle(document.querySelector('.derico-hero'));
        const size = parseFloat(style.fontSize);
        return {
          family: style.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
          leading: Math.round((parseFloat(style.lineHeight) / size) * 100) / 100,
          page: getComputedStyle(document.body).fontFamily.split(',')[0].replace(/["']/g, '').trim(),
        };
      });
      check(
        bodyType.family === 'Source Sans 3',
        `the hero's body family is the theme's (${bodyType.family})`,
      );
      check(
        Math.abs(bodyType.leading - 1.65) <= 0.02,
        `the hero's leading is the design's 1.65 (${bodyType.leading})`,
      );
      check(
        bodyType.family === bodyType.page,
        `the hero and the page agree on the family (${bodyType.family} vs ${bodyType.page})`,
      );

      /* -- the picture, once -------------------------------------------- */
      if (width === 1440) {
        const picture = await pictureOf(page, PLONE);
        check(!!picture, 'the hero renders a <picture>');
        if (picture) {
          check(picture.ariaHidden === 'true', 'the photograph is aria-hidden (it is decorative)');
          check(
            picture.sources.length === 2 &&
              picture.sources[0].media === '(max-width: 55.99rem)' &&
              picture.sources[1].media === null,
            `portrait sources come first, wide second: ${JSON.stringify(picture.sources.map((source) => source.media))}`,
          );
          check(
            picture.sources.every((source) => source.sizes === '100vw'),
            'both sourcesets are sized 100vw',
          );
          check(
            picture.sources.every((source) => /\d+w(,|$)/.test((source.srcset || '').trim())),
            'both sourcesets carry width descriptors',
          );
          check(picture.img.alt === '', 'the img has an empty alt');
          check(
            picture.img.fetchpriority === 'high' && picture.img.loading === null,
            `the img is eager and high priority (fetchpriority=${picture.img.fetchpriority}, loading=${picture.img.loading})`,
          );
          check(
            picture.img.renderedWidth === width,
            `the photograph fills the hero (${picture.img.renderedWidth}px)`,
          );
        }
      }

      /* -- the ring halo ------------------------------------------------ */
      /* Pairing, order and surround, read off computed styles: a photograph
       * can't tell a halo from a dark leaf. `vector-effect` keeps the 2px
       * constant across widths. */
      const halo = await page.evaluate(() => {
        const disc = document.querySelector('.derico-hero .rings-disc');
        const group = (name) => disc.querySelector(`.${name}`);
        const key = (c) => ['cx', 'cy', 'r', 'class'].map((a) => c.getAttribute(a)).join('|');
        const list = (g) => Array.from(g.querySelectorAll('circle'));
        const haloGroup = group('ring-halo');
        const inkGroup = group('ring-ink');
        if (!haloGroup || !inkGroup) return null;
        const ground = getComputedStyle(
          document.querySelector('.derico-hero'),
        ).getPropertyValue('--derico-hero-ground').trim();
        const paint = (c) => {
          const style = getComputedStyle(c);
          return {
            width: parseFloat(style.strokeWidth),
            stroke: style.stroke,
            vectorEffect: style.vectorEffect,
          };
        };
        const swatch = document.createElement('span');
        swatch.style.color = ground;
        document.body.appendChild(swatch);
        const groundComputed = getComputedStyle(swatch).color;
        swatch.remove();
        return {
          haloFirst: !!(
            haloGroup.compareDocumentPosition(inkGroup) & Node.DOCUMENT_POSITION_FOLLOWING
          ),
          sameTransform:
            haloGroup.getAttribute('transform') === inkGroup.getAttribute('transform'),
          keys: { halo: list(haloGroup).map(key), ink: list(inkGroup).map(key) },
          pairs: list(haloGroup).map((c, i) => ({
            halo: paint(c),
            ink: paint(list(inkGroup)[i]),
          })),
          groundComputed,
        };
      });
      check(!!halo, 'the rings disc carries a halo group and an ink group');
      if (halo) {
        check(halo.haloFirst, 'the halo paints beneath the ink, not over it');
        check(halo.sameTransform, 'both groups carry the same transform');
        check(
          halo.keys.halo.length === 8 &&
            JSON.stringify(halo.keys.halo) === JSON.stringify(halo.keys.ink),
          `every stroke is paired with a halo at the same geometry (${halo.keys.halo.length} vs ${halo.keys.ink.length})`,
        );
        const thin = halo.pairs.filter((pair) => pair.halo.width - pair.ink.width < 3);
        check(
          thin.length === 0,
          `every halo surrounds its ink by at least 3px (${thin.length} too thin)`,
        );
        check(
          halo.pairs.every((pair) => pair.halo.stroke === halo.groundComputed),
          `the halo is painted in the ground (${halo.pairs[0] && halo.pairs[0].halo.stroke} vs ${halo.groundComputed})`,
        );
        check(
          halo.pairs.every((pair) => pair.halo.vectorEffect === 'non-scaling-stroke'),
          'the halo is a non-scaling stroke, so 2px a side holds at every size',
        );
      }

      /* -- contrast over the photograph ---------------------------------- */
      if (width === 1440 || width === 375) {
        const contrast = await contrastReport(page, PLONE, TEXT_PARTS);
        for (const entry of contrast) {
          const label = `${entry.selector} "${entry.text}" worst ${entry.contrast}, median ${entry.median}, ${Math.round(
            entry.belowShare * 100,
          )}% of the glyph area under ${entry.required}`;
          check(entry.belowShare !== null && entry.belowShare <= SPECKLE, label);
        }
      }
    }

    check(pageErrors.length === 0, `no uncaught page errors:\n${pageErrors.join('\n')}`);
  } finally {
    await browser.close();
    await design.close();
    if (!process.env.DERICO_E2E_KEEP) await removeFixture(BASE);
  }

  console.log(`\n${failures.length ? `FAILED (${failures.length})` : 'PASSED'} — hero-view.e2e.js`);
  process.exitCode = failures.length ? 1 : 0;
})();
