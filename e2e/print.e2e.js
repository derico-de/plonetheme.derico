/* E2E: the print sheet on a real page.
 *
 * tests/test_print.py pins what static/print.css SAYS; this file checks what
 * the browser DOES with it, under `emulateMedia({ media: 'print' })`, on the
 * hero fixture page and on a page of this file's own: one paragraph on
 * Blicca's Dark slot carrying an external link and an internal one. Four
 * things only a rendering can answer:
 *
 * - the sheet does not leak to the screen — the bundle loads with
 *   `media="all"`, so the header is visible on screen and gone in print;
 * - the hero's action row loses to the theme in print, although the block's
 *   own scoped sheet places it (specificity, not load order — see the
 *   sheet's header);
 * - the Dark slot prints ink on ground: the wrapper's inline
 *   `var(--aurora-block-fg-dark)` resolves through the re-pointed token on
 *   `.aurora-blocks-view`;
 * - a link prints in the running ink, underlined, with its address after it.
 *
 * Browsed ANONYMOUSLY, like hero-view.e2e.js: the toolbar is Clara's chrome
 * and out of scope here.
 *
 * Prerequisites and environment: as hero-view.e2e.js (a running Plone with
 * plonetheme.derico at profile version 1013+, plone.restapi; no editor).
 *
 * Run: node print.e2e.js
 */
const { chromium } = require('playwright-core');

const {
  PAGE_TYPE,
  SOMERSAULT_BLOCK_ID,
  Site,
  buildFixture,
  removeFixture,
} = require('./hero-fixture');

const BASE = (
  process.env.DERICO_E2E_BASE ||
  process.env.AURORA_E2E_BASE ||
  'http://127.0.0.1:8081/Plone'
).replace(/\/+$/, '');
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM || process.env.AURORA_E2E_CHROMIUM;

const PRINT_PAGE_ID = 'print-page';
const EXTERNAL = 'https://example.org/somewhere';

/* The two tokens the sheet paints with, resolved IN the page rather than
 * copied here as literals: Chromium reports an oklch()-authored colour in
 * oklch(), and a probe element painted with the same `var()` reports it
 * the same way, whatever the serialisation. */
const INK = 'var(--derico-ink)';
const GROUND = 'var(--derico-ground)';

const failures = [];
function check(condition, message) {
  if (condition) {
    console.log(`  ok   ${message}`);
  } else {
    console.error(`  FAIL ${message}`);
    failures.push(message);
  }
}

/** A page with one paragraph on the Dark slot: an external link, then an
 * internal one (the fixture's own contact page). */
async function buildPrintPage(base, fixture) {
  const site = new Site(base);
  const path = `${fixture.folder}/${PRINT_PAGE_ID}`;
  await site.json('POST', fixture.folder, {
    '@type': PAGE_TYPE,
    id: PRINT_PAGE_ID,
    title: 'Print sheet',
    blocks: {
      /* the somersault block's @type is the same string as its id */
      [SOMERSAULT_BLOCK_ID]: {
        '@type': SOMERSAULT_BLOCK_ID,
        value: [
          {
            type: 'p',
            backgroundColor: 'dark',
            children: [
              { text: 'Read ' },
              { type: 'a', url: EXTERNAL, children: [{ text: 'elsewhere' }] },
              { text: ' or ' },
              { type: 'a', url: fixture.urls.contact, children: [{ text: 'here' }] },
              { text: '.' },
            ],
          },
        ],
      },
    },
    blocks_layout: { items: [SOMERSAULT_BLOCK_ID] },
  });
  await site.publish(path);
  return path;
}
const resolveColor = (page, value) =>
  page.evaluate((value) => {
    const probe = document.createElement('span');
    probe.style.color = value;
    document.body.append(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();
    return resolved;
  }, value);

const style = (page, selector, property, pseudo = null) =>
  page.evaluate(
    ([selector, property, pseudo]) => {
      const element = document.querySelector(selector);
      if (!element) return null;
      return getComputedStyle(element, pseudo).getPropertyValue(property);
    },
    [selector, property, pseudo],
  );

(async () => {
  const fixture = await buildFixture(BASE);
  const printPage = await buildPrintPage(BASE, fixture);
  const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(String(error)));

  try {
    const ink = async () => resolveColor(page, INK);
    const ground = async () => resolveColor(page, GROUND);

    /* -- the hero page: chrome, action row, and no leak to the screen ----- */
    console.log('\n# hero page');
    await page.goto(`${BASE}${fixture.heroPage}`, { waitUntil: 'networkidle' });

    await page.emulateMedia({ media: 'screen' });
    check((await style(page, '.element-logo', 'display')) !== 'none', 'on screen the logo is visible');
    check(
      (await style(page, '.derico-hero .action-row', 'display')) === 'flex',
      'on screen the hero shows its action row',
    );

    /* Two widths: the wide header, and the narrow one — where header.css
     * re-displays the navigation and the search that Clara's print block
     * hides, and which is what a sheet of paper gets (A4 lays out at 794px). */
    for (const width of [1440, 794]) {
      await page.setViewportSize({ width, height: 900 });
      await page.emulateMedia({ media: 'print' });
      /* Every one of these is on every page of the site, so `null` — the
       * element absent — is a failure, not a pass. */
      for (const element of [
        '.element-logo',
        '.element-globalnav',
        '.element-searchbox',
        '.element-portalfooter',
        '.element-footerblocks',
      ]) {
        const display = await style(page, element, 'display');
        check(display === 'none', `in print at ${width}px ${element} is gone (${display})`);
      }
    }
    check(
      (await style(page, '.derico-hero .action-row', 'display')) === 'none',
      'in print the hero action row is gone',
    );
    check((await style(page, 'body', 'color')) === (await ink()), 'in print the body is ink');
    check(
      (await style(page, 'body', 'background-color')) === (await ground()),
      'in print the body is on ground',
    );

    /* -- the dark slot and the links ------------------------------------- */
    console.log('\n# print page');
    await page.goto(`${BASE}${printPage}`, { waitUntil: 'networkidle' });

    await page.emulateMedia({ media: 'screen' });
    /* Blicca paints the band on the wrapper's `::before`, bled to the
     * viewport; the foreground is set on the wrapper itself. */
    const band = () =>
      style(page, '.block.has--backgroundColor--dark', 'background-color', '::before');
    const screenBand = await band();
    check(
      screenBand !== null && screenBand !== (await ground()),
      `on screen the dark slot paints its band (${screenBand})`,
    );
    check((await style(page, '.element-breadcrumbs', 'display')) !== 'none', 'on screen the breadcrumbs are visible');

    await page.emulateMedia({ media: 'print' });
    check(
      (await style(page, '.element-breadcrumbs', 'display')) === 'none',
      'in print the breadcrumbs are gone',
    );
    const m = await page.evaluate(() => {
      const probe = document.createElement('div');
      probe.style.paddingBlock = 'var(--plone-space-m)';
      document.body.append(probe);
      const value = getComputedStyle(probe).paddingBlockStart;
      probe.remove();
      return value;
    });
    check(
      (await style(page, '.element-contentheader', 'padding-block-start')) === m &&
        (await style(page, '.element-contentheader', 'padding-block-end')) === m,
      `in print the content header is framed by the m step (${m})`,
    );
    check(
      (await style(page, '.block.has--backgroundColor--dark', 'padding-block-start')) === m,
      'in print the dark band closes up to the m step',
    );
    check((await band()) === (await ground()), 'in print the dark slot is on ground');
    check(
      (await style(page, '.block.has--backgroundColor--dark p', 'color')) === (await ink()),
      "in print the dark slot's text is ink",
    );
    const external = `.block.has--backgroundColor--dark a[href="${EXTERNAL}"]`;
    check(
      (await style(page, external, 'color')) === (await ink()),
      'in print a link is in the running ink',
    );
    check(
      /underline/.test(await style(page, external, 'text-decoration-line')),
      'in print a link is underlined',
    );
    check(
      (await style(page, external, 'content', '::after')) === `" (${EXTERNAL})"`,
      'in print an external link prints its address',
    );
    const internal = `.block.has--backgroundColor--dark a[href="${fixture.urls.contact}"]`;
    check(
      (await style(page, internal, 'content', '::after')) === `" (${fixture.urls.contact})"`,
      'in print an internal link prints its address too (Plone writes it absolute)',
    );

    check(pageErrors.length === 0, `no uncaught page errors:\n${pageErrors.join('\n')}`);
  } finally {
    await browser.close();
    if (!process.env.DERICO_E2E_KEEP) await removeFixture(BASE);
  }

  console.log(`\n${failures.length ? `FAILED (${failures.length})` : 'PASSED'} — print.e2e.js`);
  process.exitCode = failures.length ? 1 : 0;
})();
