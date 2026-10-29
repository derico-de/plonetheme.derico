/* E2E: the header keeps room for the shop's mini-cart.
 *
 * Builds a Shop with a cart page in the language folder, so
 * derico.blicca.shopblocks renders its `.shop-mini-cart` viewlet, and measures
 * the bar at the widths the theme promises: the cart fits beside the logo,
 * the navigation or menu, the language switch and the search toggle, at the
 * search toggle's size, with the badge in the copper accent. Below 64rem the
 * language switch lives in the opened menu.
 *
 * Browsed anonymously and logged in (basic auth; the toolbar narrows the
 * layout, which the bar's container query follows).
 *
 * Prerequisites: plone.restapi, plonetheme.derico and derico.blicca.shopblocks
 * (its viewlet registered) on a site with a language folder; DERICO_E2E_LANG
 * names it (default `de`).
 *
 * Run: node header-minicart.e2e.js
 */
const assert = require('assert');
const { chromium } = require('playwright-core');

const { AUTH, Site } = require('./hero-fixture');

const BASE = (process.env.DERICO_E2E_BASE || 'http://127.0.0.1:8081/Plone').replace(/\/+$/, '');
const LANG = process.env.DERICO_E2E_LANG || 'de';
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM;

const SHOP = 'derico-cart-e2e-shop';
const CART = 'derico-cart-e2e-cart';
const WIDTHS = [1400, 1024, 768, 390];

async function removeFixture(site) {
  for (const id of [SHOP, CART]) await site.request('DELETE', `/${LANG}/${id}`);
}

async function buildFixture(site) {
  await removeFixture(site);
  await site.json('POST', `/${LANG}`, {
    '@type': 'Document',
    id: CART,
    title: 'Cart',
    exclude_from_nav: true,
  });
  const cart = await site.json('GET', `/${LANG}/${CART}`);
  await site.json('POST', `/${LANG}`, {
    '@type': 'Shop',
    id: SHOP,
    title: 'Shop',
    cart_page: cart.UID,
    exclude_from_nav: true,
  });
  await site.publish(`/${LANG}/${CART}`);
  await site.publish(`/${LANG}/${SHOP}`);
}

const measure = () => {
  const box = (selector) => {
    const element = document.querySelector(selector);
    if (!element) return null;
    const rect = element.getBoundingClientRect();
    if (getComputedStyle(element).display === 'none' || !rect.width) return null;
    return { left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom };
  };
  const parts = {
    logo: box('#portal-logo img'),
    cart: box('.shop-mini-cart-link'),
    search: box('.searchbox-toggle'),
    language: box('.element-language'),
    login: box('.element-anontools a'),
    menu: box('.globalnav-toggle'),
  };
  const links = [...document.querySelectorAll('#portal-globalnav > .nav-item > .nav-link')]
    .map((link) => link.getBoundingClientRect())
    .filter((rect) => rect.width);
  const nav = document.querySelector('#portal-globalnav');
  if (links.length && getComputedStyle(nav).display !== 'none') {
    parts.navigation = {
      left: Math.min(...links.map((r) => r.left)),
      right: Math.max(...links.map((r) => r.right)),
      top: Math.min(...links.map((r) => r.top)),
      bottom: Math.max(...links.map((r) => r.bottom)),
    };
  }
  const names = Object.keys(parts).filter((name) => parts[name]);
  const overlaps = [];
  names.forEach((a, index) => {
    names.slice(index + 1).forEach((b) => {
      const p = parts[a];
      const q = parts[b];
      const across = p.left < q.right - 0.5 && q.left < p.right - 0.5;
      const down = p.top < q.bottom - 0.5 && q.top < p.bottom - 0.5;
      if (across && down) overlaps.push(`${a} x ${b}`);
    });
  });
  const size = (part) => part && [part.right - part.left, part.bottom - part.top];
  const badge = document.querySelector('.shop-mini-cart-badge');
  const probe = document.createElement('i');
  probe.style.backgroundColor = 'var(--derico-copper)';
  document.body.append(probe);
  const copper = getComputedStyle(probe).backgroundColor;
  probe.remove();
  return {
    overlaps,
    names,
    cart: size(parts.cart),
    search: size(parts.search),
    badge: badge && {
      hidden: badge.hidden,
      text: badge.textContent,
      background: getComputedStyle(badge).backgroundColor,
    },
    copper,
    overflow: document.documentElement.scrollWidth - innerWidth,
  };
};

async function run() {
  const site = new Site(BASE);
  await buildFixture(site);
  const browser = await chromium.launch({ executablePath: EXECUTABLE, headless: true });
  try {
    for (const login of [false, true]) {
      const context = await browser.newContext({
        extraHTTPHeaders: login ? { Authorization: AUTH } : {},
      });
      for (const count of [null, '12-0']) {
        await context.clearCookies();
        if (count) await context.addCookies([{ name: 'shop_hint', value: count, url: BASE }]);
        const page = await context.newPage();
        for (const width of WIDTHS) {
          const label = `${login ? 'logged in' : 'anonymous'}, ${count ? 'badge' : 'no badge'}, ${width}px`;
          await page.setViewportSize({ width, height: 600 });
          await page.goto(`${BASE}/${LANG}`, { waitUntil: 'networkidle' });
          const m = await page.evaluate(measure);
          assert.deepStrictEqual(m.overlaps, [], `${label}: overlap ${m.overlaps}`);
          assert.ok(m.names.includes('cart'), `${label}: no cart`);
          assert.deepStrictEqual(m.cart, m.search, `${label}: cart is not the search toggle's size`);
          assert.strictEqual(m.overflow, 0, `${label}: horizontal scroll`);
          assert.strictEqual(m.badge.hidden, !count, `${label}: badge visibility`);
          if (count) {
            assert.strictEqual(m.badge.text, '12', `${label}: badge text`);
            assert.strictEqual(m.badge.background, m.copper, `${label}: badge is not copper`);
          }
          if (m.names.includes('menu')) {
            assert.ok(!m.names.includes('language'), `${label}: language switch is on the bar`);
            await page.click('.globalnav-toggle');
            const open = await page.evaluate(measure);
            assert.ok(open.names.includes('language'), `${label}: language switch not in the menu`);
            await page.click('.globalnav-toggle');
          }
        }
        await page.close();
      }
      await context.close();
    }
    console.log('header-minicart: ok');
  } finally {
    await browser.close();
    await removeFixture(site);
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
