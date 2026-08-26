/* E2E: the Derico Hero's published page against the design source (ticket 10).
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
 * viewport-minus-toolbar (1220 at 1440 — ticket 07's table) and would compare
 * a narrower hero against a full-width mockup.
 *
 * Two things this file measures and reports but does NOT assert, because both
 * are open decisions rather than regressions:
 *
 * - the hero's body font falls through to Blicca's `.aurora-blocks-view`
 *   stack instead of the theme's own (ticket 17);
 * - the ring legend misses WCAG AA over the brightest part of the photograph
 *   — in the design source as much as here (ticket 18). The named exceptions
 *   below are exactly those cases; everything else must hold AA, so a NEW
 *   contrast failure still fails this test.
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

/* `.ring-markers li` is deliberately NOT here, and its removal is a finding
 * rather than a convenience. This probe exists to catch text sitting on a
 * PHOTOGRAPH; the marker numerals never do. They are ground-coloured glyphs on
 * an opaque copper chip with a 2px ground border, so their whole backdrop is
 * element-painted — and what the probe was actually reporting was the glyph's
 * antialiased edge overlapping that border, ground on ground, at a worst-pixel
 * ratio of 1.02. Measured: 2% of the glyph area before the hero took the
 * theme's body type (ticket 22) and 3% after, either side of a SPECKLE
 * threshold whose stated basis was that "nothing observed lands between 2% and
 * 11%". Nothing about the contrast changed; the glyph shape did.
 *
 * Raising SPECKLE would have bought this by blunting the guard for every
 * element that IS over the photograph. The chips belong to the value test
 * instead, where their real question — is ground legible on copper, and on the
 * is-now cyan — is answered exactly and at every width at once:
 * `test_the_marker_chips_carry_their_own_backdrop`. Their geometry is still
 * pinned here (28x28, nothing under 15px). */

/* The share of a glyph's own pixels allowed to miss AA before the miss counts
 * as a contrast defect rather than as a speckle in a photograph. Measured:
 * the genuine failures sit at 44-87% of the glyph area, the speckles at 0.1%,
 * and nothing observed lands between 2% and 11%. */
const SPECKLE = 0.02;

/* Ticket 18's named exceptions are GONE, and their deletion is ticket 21's
 * acceptance criterion. They recorded three inherited failures — the is-now
 * row at every width, and the whole legend at 375 where it crossed the
 * brightest part of the photograph. All three were the same defect: text with
 * nothing but the photograph behind it. The legend card and the copy scrim
 * give every glyph a ground the sheet declares, so there is no longer a case
 * to except, and this file's job becomes proving that every glyph actually
 * SITS on the ground the value test proved strong enough.
 *
 * That is why the two tests are not redundant. The value test cannot see a
 * layout change that moves text off its backdrop; this one cannot see a colour
 * that was never strong enough. */

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

      /* -- the body type, now asserted: ticket 17/22 -------------------- */
      /* Ticket 10 found this by measuring the legend 291 tall against the
       * design's 330 and working backwards. Blicca states a Tailwind sans
       * stack on `.aurora-blocks-view`, so without the hero's own declaration
       * the published page renders in the browser's generic sans while the
       * canvas — which gets its stack from Aurora's scoped preflight — does
       * not. Hence both halves: family AND leading, and the same pair asserted
       * in the canvas by `hero-editor.e2e.js`, since parity is the whole
       * justification for putting this in the block sheet. */
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

      /* -- the ring halo: ticket 20/23 ----------------------------------- */
      /* The value test proves the halo's colour is strong enough; this proves
       * the halo is WHERE the stroke is. Pairing, order and surround, read off
       * computed styles rather than pixels — a photograph cannot tell a halo
       * from a dark leaf behind it. `vector-effect` is asserted as a
       * DECLARATION (ticket 15's posture): it is what keeps the 2px a side
       * constant at 375 as well as 1440, and reading it back is the only way
       * to see it without measuring a rendered stroke. */
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
