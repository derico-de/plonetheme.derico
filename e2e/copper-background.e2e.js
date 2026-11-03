/* E2E: the copper block background on a real page.
 *
 * tests/test_aurora_block_backgrounds.py pins what the sheet SAYS and measures
 * its contrast; this file checks what the browser DOES with it, on the
 * published page and on the `@@aurora-edit` canvas, the two surfaces Blicca
 * paints a band on:
 *
 * - the band paints the brand copper on the block's `::before`;
 * - text, links, text styles, quotes and a Promo on it take the foreground,
 *   where `--derico-copper-text` on copper would fail;
 * - the Promo CTA keeps its button shape, in ink rather than copper;
 * - it prints ink on ground, like the Dark slot;
 * - the sidebar's Background select offers Copper after the built-ins.
 *
 * Prerequisites and environment: as hero-view.e2e.js (a running Plone with
 * plonetheme.derico at profile version 1025+, plone.restapi and
 * derico.blicca.promoblock), and the mockup editor bundle for the canvas.
 *
 * Run: node copper-background.e2e.js
 */
const { chromium } = require('playwright-core');

const {
  PAGE_TYPE,
  PASSWORD,
  SOMERSAULT_BLOCK_ID,
  Site,
  USER,
  buildFixture,
  removeFixture,
} = require('./hero-fixture');

const BASE = (
  process.env.DERICO_E2E_BASE ||
  process.env.AURORA_E2E_BASE ||
  'http://127.0.0.1:8081/Plone'
).replace(/\/+$/, '');
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM || process.env.AURORA_E2E_CHROMIUM;

const COPPER_PAGE_ID = 'copper-page';
const BAND = '.block.has--backgroundColor--copper';
const OFFERED = 'none=None,grey=Grey,accent=Accent,dark=Dark,copper=Copper';

const failures = [];
function check(condition, message) {
  if (condition) {
    console.log(`  ok   ${message}`);
  } else {
    console.error(`  FAIL ${message}`);
    failures.push(message);
  }
}

const onCopper = (node) => ({ backgroundColor: 'copper', ...node });
const paragraph = (text, textStyle) =>
  onCopper({ type: 'p', ...(textStyle && { textStyle }), children: [{ text }] });

/** One block of everything that names a colour of its own. */
async function buildCopperPage(base, fixture) {
  const site = new Site(base);
  const path = `${fixture.folder}/${COPPER_PAGE_ID}`;
  await site.json('POST', fixture.folder, {
    '@type': PAGE_TYPE,
    id: COPPER_PAGE_ID,
    title: 'Copper background',
    blocks: {
      [SOMERSAULT_BLOCK_ID]: {
        '@type': SOMERSAULT_BLOCK_ID,
        value: [
          onCopper({ type: 'h2', children: [{ text: 'A heading' }] }),
          onCopper({
            type: 'p',
            children: [
              { text: 'A paragraph with ' },
              { type: 'a', url: fixture.urls.contact, children: [{ text: 'a link' }] },
              { text: '.' },
            ],
          }),
          paragraph('A kicker', 'kicker'),
          paragraph('A lede', 'lede'),
          paragraph('A term', 'term'),
          paragraph('Muted', 'muted'),
          onCopper({ type: 'blockquote', textStyle: 'statement', children: [{ text: 'A quote' }] }),
          onCopper({
            type: 'ploneBlock',
            '@type': 'promo',
            children: [{ text: '' }],
            head_title: 'Promo kicker',
            title: 'Promo title',
            description: 'Promo description',
            cta_primary_label: 'Promo action',
            cta_primary_link: fixture.urls.contact,
            cta_primary_variant: 'button',
          }),
        ],
      },
    },
    blocks_layout: { items: [SOMERSAULT_BLOCK_ID] },
  });
  await site.publish(path);
  return path;
}

/* A colour as the pixel it paints: the canvas link's colour is authored in
 * rgb and the tokens in oklch(), so their computed strings never compare. */
const pixel = (page, value) =>
  page.evaluate((value) => {
    const probe = document.createElement('span');
    probe.style.color = value;
    document.body.append(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();
    const context = document.createElement('canvas').getContext('2d');
    context.fillStyle = resolved;
    context.fillRect(0, 0, 1, 1);
    return [...context.getImageData(0, 0, 1, 1).data].join();
  }, value);

const painted = async (page, selector, property, pseudo = null) => {
  const value = await page.evaluate(
    ([selector, property, pseudo]) => {
      const element = document.querySelector(selector);
      if (!element) return null;
      return getComputedStyle(element, pseudo).getPropertyValue(property);
    },
    [selector, property, pseudo],
  );
  return value === null ? null : pixel(page, value);
};

const style = (page, selector, property) =>
  page.evaluate(
    ([selector, property]) => {
      const element = document.querySelector(selector);
      return element && getComputedStyle(element).getPropertyValue(property);
    },
    [selector, property],
  );

/** Everything on the band that must read in `ink`. */
async function checkInk(page, surface, ink, inkName) {
  for (const [name, selector] of [
    ['heading', `h2${BAND}, ${BAND} h2`],
    ['link', `${BAND} a`],
    ['kicker', `${BAND}.has--textStyle--kicker`],
    ['lede', `${BAND}.has--textStyle--lede`],
    ['term', `${BAND}.has--textStyle--term`],
    ['muted text', `${BAND}.has--textStyle--muted`],
    ['quote', `${BAND}.block-blockquote`],
    ['Promo kicker', `${BAND} .promo-kicker`],
    ['Promo title', `${BAND} .promo-title`],
    ['Promo description', `${BAND} .promo-description`],
  ]) {
    const color = await painted(page, selector, 'color');
    check(color === ink, `${surface}: the ${name} is ${inkName} (${color})`);
  }
}

async function checkScreen(page, surface) {
  const copper = await pixel(page, 'var(--derico-copper)');
  const foreground = await pixel(page, 'var(--derico-on-copper)');
  const ink = await pixel(page, 'var(--derico-ink)');
  const deep = await pixel(page, 'var(--derico-brand-deep)');

  check(
    (await painted(page, BAND, 'background-color', '::before')) === copper,
    `${surface}: the band paints the brand copper`,
  );
  await checkInk(page, surface, foreground, 'the foreground');
  check(
    /underline/.test(await style(page, `${BAND} a`, 'text-decoration-line')),
    `${surface}: a link is underlined, its colour no longer tells it apart`,
  );
  check(
    (await painted(page, `${BAND}.block-blockquote`, 'border-block-start-color')) === foreground,
    `${surface}: the quote's rule is the foreground`,
  );

  const button = `${BAND} .promo-cta-button`;
  check(
    (await painted(page, button, 'background-color')) === ink,
    `${surface}: the Promo CTA is an ink button on the copper`,
  );
  check(
    (await painted(page, button, 'color')) === foreground,
    `${surface}: the Promo CTA's label is the foreground`,
  );
  await page.locator(button).hover();
  await page.waitForTimeout(400);
  check(
    (await painted(page, button, 'background-color')) === deep,
    `${surface}: hovered, the Promo CTA turns brand-deep`,
  );
  check(
    (await painted(page, button, 'color')) === foreground,
    `${surface}: hovered, its label stays the foreground`,
  );
  await page.mouse.move(0, 0);
}

async function login(page) {
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' });
  await page.fill('input[name="__ac_name"]', USER);
  await page.fill('input[name="__ac_password"]', PASSWORD);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
    page.click('button[name="buttons.login"], input[name="buttons.login"]'),
  ]);
}

(async () => {
  const fixture = await buildFixture(BASE);
  const copperPage = await buildCopperPage(BASE, fixture);
  const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(String(error)));

  try {
    console.log('\n# published page');
    await page.goto(`${BASE}${copperPage}`, { waitUntil: 'networkidle' });
    await checkScreen(page, 'published');

    console.log('\n# in print');
    await page.emulateMedia({ media: 'print' });
    const ground = await pixel(page, 'var(--derico-ground)');
    check(
      (await painted(page, BAND, 'background-color', '::before')) === ground,
      'in print the band is on ground',
    );
    await checkInk(page, 'in print', await pixel(page, 'var(--derico-ink)'), 'ink');
    await page.emulateMedia({ media: 'screen' });

    console.log('\n# canvas');
    await login(page);
    await page.goto(`${BASE}${copperPage}/@@aurora-edit`, { waitUntil: 'domcontentloaded' });
    await page.waitForSelector(`[data-slate-editor] ${BAND} .promo-cta-button`, { timeout: 90000 });
    await page.waitForTimeout(1500);
    await checkScreen(page, 'canvas');
    check(
      (await painted(page, `${BAND} .slate-a`, 'text-decoration-color')) ===
        (await pixel(page, 'var(--derico-on-copper)')),
      "canvas: a link's underline is the foreground",
    );

    await page.locator(`[data-slate-editor] ${BAND}[data-block-type="p"]`).first().click();
    await page.waitForSelector('#sidebar select[name="backgroundColor"] option[value="copper"]', {
      state: 'attached',
      timeout: 10000,
    });
    const offered = await page.evaluate(() =>
      [...document.querySelectorAll('#sidebar select[name="backgroundColor"] option')].map(
        (option) => `${option.value}=${option.textContent.trim()}`,
      ),
    );
    check(offered.join() === OFFERED, `sidebar: the Background select offers ${offered.join()}`);

    check(pageErrors.length === 0, `no uncaught page errors:\n${pageErrors.join('\n')}`);
  } finally {
    await browser.close();
    if (!process.env.DERICO_E2E_KEEP) await removeFixture(BASE);
  }

  console.log(`\n${failures.length ? `FAILED (${failures.length})` : 'PASSED'} — copper-background.e2e.js`);
  process.exitCode = failures.length ? 1 : 0;
})();
