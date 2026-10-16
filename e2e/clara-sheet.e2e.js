/* E2E: derico's compile of Clara styles every page the way Clara's own sheet does.
 *
 * `static/clara.min.css` leaves out the Bootstrap parts no derico page uses,
 * and all dark mode. This checks that where it can fail, in the browser: each
 * page is rendered with the compile and the computed style of every element
 * (and its ::before/::after) is recorded; then Clara's own sheet is added
 * beside the compile, the compile is switched off, and the styles are
 * recorded again. Clara's sheet is a superset, so nothing may move. A
 * difference is a rule the compile dropped that the page uses.
 *
 * At 1440 and 375 (every breakpoint variant is on at one and off at the
 * other) and with a dark OS preference, so a page that misses the light pin
 * shows up too.
 *
 * Prerequisites and environment: as hero-view.e2e.js, plus plonetheme.derico
 * at profile version 1024.
 *
 * Run: node clara-sheet.e2e.js
 */
const { chromium } = require('playwright-core');

const { PASSWORD, USER, buildFixture, removeFixture } = require('./hero-fixture');

const BASE = (
  process.env.DERICO_E2E_BASE ||
  process.env.AURORA_E2E_BASE ||
  'http://127.0.0.1:8081/Plone'
).replace(/\/+$/, '');
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM || process.env.AURORA_E2E_CHROMIUM;

const WIDTHS = [1440, 375];
const COMPILE = '++resource++plonetheme.derico/clara.min.css';
const CLARA_OWN = '++resource++plonetheme.clara/clara.min.css';

const failures = [];
function check(condition, message) {
  if (condition) {
    console.log(`  ok   ${message}`);
  } else {
    console.error(`  FAIL ${message}`);
    failures.push(message);
  }
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

/** Every element's computed style, then the same with Clara's own sheet:
 * the elements whose style differs, with the properties that do. */
async function compareWithClaraOwnSheet(page) {
  return page.evaluate(
    async ({ compile, claraOwn }) => {
      // The page's elements as they are now; the link added below is not one.
      const elements = Array.from(document.querySelectorAll('*'));
      const snapshot = () =>
        elements.map((element) =>
          [null, '::before', '::after'].map((pseudo) => {
            const style = getComputedStyle(element, pseudo);
            const values = {};
            for (const name of style) values[name] = style.getPropertyValue(name);
            return values;
          }),
        );
      const settle = () => new Promise((resolve) => setTimeout(resolve, 500));

      const link = document.querySelector('link[data-bundle="plonetheme-clara"]');
      if (!link || !link.href.endsWith(compile)) return { error: `no ${compile} link` };
      const before = snapshot();

      const own = link.cloneNode();
      own.href = link.href.replace(compile, claraOwn);
      await new Promise((resolve, reject) => {
        own.onload = resolve;
        own.onerror = () => reject(new Error(`${own.href} did not load`));
        link.after(own);
      });
      link.disabled = true;
      await settle();
      const after = snapshot();

      const label = (element) =>
        element.tagName.toLowerCase() +
        (element.id ? `#${element.id}` : '') +
        Array.from(element.classList, (name) => `.${name}`).join('');
      const differences = [];
      before.forEach((parts, index) =>
        parts.forEach((values, part) => {
          const changed = Object.keys(values).filter((name) => values[name] !== after[index][part][name]);
          if (changed.length) {
            differences.push({
              element: label(elements[index]) + ['', '::before', '::after'][part],
              properties: changed.slice(0, 4).map((name) => `${name}: ${values[name]} → ${after[index][part][name]}`),
            });
          }
        }),
      );
      return { elements: before.length, differences };
    },
    { compile: COMPILE, claraOwn: CLARA_OWN },
  );
}

async function checkPage(page, url, name) {
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  const result = await compareWithClaraOwnSheet(page);
  if (result.error) {
    check(false, `${name}: ${result.error}`);
    return;
  }
  const shown = result.differences
    .slice(0, 8)
    .map((difference) => `\n         ${difference.element}: ${difference.properties.join('; ')}`)
    .join('');
  check(
    result.differences.length === 0,
    `${name}: ${result.elements} elements style the same as under Clara's own sheet${shown}`,
  );
}

(async () => {
  const fixture = await buildFixture(BASE);
  const browser = await chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
  try {
    for (const width of WIDTHS) {
      console.log(`\n# ${width}px`);
      const viewport = { width, height: 900 };

      const anonymous = await browser.newContext({ viewport, colorScheme: 'dark' });
      const visitor = await anonymous.newPage();
      await checkPage(visitor, `${BASE}${fixture.heroPage}`, 'the hero page, anonymously');
      await checkPage(visitor, `${BASE}/login`, 'the login form');
      await anonymous.close();

      const administrator = await browser.newContext({ viewport, colorScheme: 'dark' });
      const admin = await administrator.newPage();
      await login(admin);
      for (const [path, name] of [
        [fixture.heroPage, 'the hero page, logged in'],
        [`${fixture.heroPage}/edit`, 'the edit form'],
        [`${fixture.folder}/folder_contents`, 'folder contents'],
        ['/@@search?SearchableText=hero', 'the search page'],
        ['/@@overview-controlpanel', 'site setup'],
        ['/@@resourceregistry-controlpanel', 'the resource registry'],
        ['/@@usergroup-userprefs', 'users and groups'],
      ]) {
        await checkPage(admin, `${BASE}${path}`, name);
      }
      await administrator.close();
    }
  } finally {
    await browser.close();
    if (!process.env.DERICO_E2E_KEEP) await removeFixture(BASE);
  }

  console.log(`\n${failures.length ? `FAILED (${failures.length})` : 'PASSED'} — clara-sheet.e2e.js`);
  process.exitCode = failures.length ? 1 : 0;
})();
