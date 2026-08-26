/* Shared fixture for the Derico Hero browser tests (hero ticket 10).
 *
 * Builds, over plone.restapi, everything the hero needs to be looked at on a
 * real site: the two crops it takes as content, the two pages its links point
 * at, and two Articles carrying an API-authored hero — one with the mockup's
 * own copy, one whose headline holds a compound long enough to force the
 * break rung ticket 15 added.
 *
 * Authoring the block through the API rather than through the editor is
 * deliberate on both counts: it is the state an ordinary editor finds on a
 * page they may not insert into (contract §7 — the gate is guidance, not
 * security), and it is the only way the published view can be measured
 * without a round trip through the canvas.
 *
 * The fixture is published, so the view tests browse it anonymously: no
 * toolbar, and `--plone-toolbar-width` — which the full-bleed breakout
 * subtracts — is out of the picture. The editor tests log in and therefore
 * see a hero narrowed by exactly that toolbar (ticket 07's table).
 *
 * Prerequisites: plone.restapi, plonetheme.derico installed at profile
 * version 1001 or later, and a content type carrying the blocks behaviour
 * (`Article` here — this site's `Document` has none).
 */
const fs = require('fs');
const path = require('path');

const USER = process.env.DERICO_E2E_USER || process.env.AURORA_E2E_USER || 'admin';
const PASSWORD =
  process.env.DERICO_E2E_PASSWORD || process.env.AURORA_E2E_PASSWORD || 'admin';
const AUTH = 'Basic ' + Buffer.from(`${USER}:${PASSWORD}`).toString('base64');

const PAGE_TYPE =
  process.env.DERICO_E2E_PAGE_TYPE || process.env.AURORA_E2E_PAGE_TYPE || 'Article';

const FOLDER_ID = 'derico-hero-e2e';
const HERO_PAGE_ID = 'hero-page';
const LONG_PAGE_ID = 'hero-long-headline';
const EMPTY_PAGE_ID = 'hero-empty-page';

const HERO_PAGE_PATH = `/${FOLDER_ID}/${HERO_PAGE_ID}`;
const LONG_PAGE_PATH = `/${FOLDER_ID}/${LONG_PAGE_ID}`;
const EMPTY_PAGE_PATH = `/${FOLDER_ID}/${EMPTY_PAGE_ID}`;

/* The ordinary editor of contract §7: may edit the page, may not insert a
 * brand block. Created by the fixture because the claim ticket 03's design
 * makes is about this exact user, and an instance is unlikely to have one. */
const EDITOR_USER = 'derico-hero-e2e-editor';
const EDITOR_PASSWORD = 'derico-hero-e2e-editor-pw';

/* The design source, as `docs/design/derico.de/site` serves it. The real
 * photograph matters: the contrast checks read text against the pixels the
 * wash sits on, and a flat placeholder would make them pass for free. */
const DESIGN_ROOT = path.resolve(__dirname, '../docs/design/derico.de/site');
const WIDE_FILE = 'hero-managed-forest-wide-2400.jpg';
const PORTRAIT_FILE = 'hero-managed-forest-portrait-1080.jpg';

/* The mockup's own homepage copy (`site/de/index.html`), verbatim. Anything
 * else would make "matches the mockup" a comparison of two different texts. */
const COPY = {
  kicker: 'Nachhaltige Lösungen, seit über 20 Jahren',
  headline: 'Anwendungen, die bleiben.',
  lede:
    'Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem ' +
    'JavaScript und Open Source. Wartbarkeit, offene Standards und klare ' +
    'Entscheidungen sichern ihren Wert über viele Jahre.',
  cta_label: 'Erstgespräch vereinbaren',
  link_label: 'Alle Leistungen',
  legend: [
    { title: 'schneller Prototyp', subtitle: 'in Wochen bedienbar' },
    { title: 'erste Anwendung', subtitle: 'trägt die tägliche Arbeit' },
    { title: 'erfahrener Begleiter', subtitle: 'wächst mit den Anforderungen' },
    { title: 'mit der Zeit gegangen', subtitle: 'offen, aktuell, migrierbar' },
  ],
};

/* The break rung's exercise. 30 characters with no break opportunity: longer
 * than the 320 shell at any rung of the headline ramp, so it is `min-width: 0`
 * plus `overflow-wrap: break-word` or nothing (ticket 15). */
const LONG_HEADLINE = 'Geschäftsanwendungsentwicklung für Bestandskunden';

const SOMERSAULT_BLOCK_ID = '__somersault__';
const SOMERSAULT_BLOCK_TYPE = '__somersault__';

class Site {
  constructor(base) {
    this.base = base.replace(/\/+$/, '');
  }

  async request(method, path, body) {
    const response = await fetch(`${this.base}${path}`, {
      method,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        Authorization: AUTH,
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!response.ok && ![404, 423].includes(response.status)) {
      const detail = (await response.text()).replace(/\s+/g, ' ').slice(0, 300);
      throw new Error(`${method} ${this.base}${path} -> ${response.status} ${detail}`);
    }
    return response;
  }

  async json(method, path, body) {
    const response = await this.request(method, path, body);
    return response.status === 204 ? null : response.json();
  }

  /* Types differ: an Image may carry no workflow at all, or one whose initial
   * state is already public, so ask what is on offer rather than assume a
   * `publish` transition exists. */
  async publish(path) {
    const workflow = await this.json('GET', `${path}/@workflow`);
    const transitions = (workflow.transitions || []).map((transition) =>
      transition['@id'].replace(/^.*\//, ''),
    );
    if (transitions.includes('publish')) {
      await this.json('POST', `${path}/@workflow/publish`);
    }
  }
}

function upload(filename) {
  return {
    data: fs.readFileSync(path.join(DESIGN_ROOT, 'assets/images', filename)).toString('base64'),
    encoding: 'base64',
    filename,
    'content-type': 'image/jpeg',
  };
}

/* A reference as the hero stores it: the bare `@id`, one element, nothing
 * else (ticket 02 — `derico_reference` trims the object browser's pick so a
 * rename survives and no stale brain metadata is persisted). */
function reference(url) {
  return [{ '@id': url }];
}

function heroNode(urls, overrides = {}) {
  return {
    type: 'ploneBlock',
    '@type': 'derico-hero',
    /* Materialised, exactly as the editor materialises it at insert
     * (ticket 11): `plate.py` reads an explicit width and stamps
     * `has--block-width--full`, which is where the viewport breakout lives.
     * A node authored without it renders `default` — 11's accepted limit. */
    blockWidth: 'full',
    children: [{ text: '' }],
    kicker: COPY.kicker,
    headline: COPY.headline,
    lede: COPY.lede,
    cta_label: COPY.cta_label,
    cta_href: reference(urls.contact),
    link_label: COPY.link_label,
    link_href: reference(urls.services),
    image_wide: reference(urls.wide),
    image_portrait: reference(urls.portrait),
    legend: COPY.legend,
    ...overrides,
  };
}

function somersault(nodes) {
  return {
    blocks: {
      [SOMERSAULT_BLOCK_ID]: { '@type': SOMERSAULT_BLOCK_TYPE, value: nodes },
    },
    blocks_layout: { items: [SOMERSAULT_BLOCK_ID] },
  };
}

async function removeFixture(base) {
  const site = new Site(base);
  for (const id of [FOLDER_ID]) {
    const response = await site.request('DELETE', `/${id}`);
    if (response.status === 423) {
      /* an aborted @@aurora-edit session leaves a WebDAV lock behind */
      await site.request('DELETE', `/${id}/@lock`, { force: true });
      await site.request('DELETE', `/${id}`);
    }
  }
}

/** The ordinary editor: Editor role on the fixture folder, nothing above it. */
async function ensureEditorUser(base) {
  const site = new Site(base);
  const existing = await site.request('GET', `/@users/${EDITOR_USER}`);
  if (existing.status === 404) {
    await site.json('POST', '/@users', {
      username: EDITOR_USER,
      email: `${EDITOR_USER}@example.invalid`,
      password: EDITOR_PASSWORD,
      fullname: 'Derico hero e2e editor',
      roles: ['Member'],
      sendPasswordReset: false,
    });
  }
  await site.json('POST', `/${FOLDER_ID}/@sharing`, {
    entries: [{ id: EDITOR_USER, type: 'user', roles: { Editor: true, Reader: true } }],
  });
  return { username: EDITOR_USER, password: EDITOR_PASSWORD };
}

/**
 * Build the whole fixture and return the paths the tests navigate to.
 * Idempotent: the folder is removed first, so a crashed run leaves nothing
 * behind that changes the next one.
 */
async function buildFixture(base) {
  const site = new Site(base);
  await removeFixture(base);

  await site.json('POST', '/', {
    '@type': 'Folder',
    id: FOLDER_ID,
    title: 'Derico hero e2e',
  });

  const wide = await site.json('POST', `/${FOLDER_ID}`, {
    '@type': 'Image',
    id: 'hero-wide',
    title: 'Hero, wide crop',
    image: upload(WIDE_FILE),
  });
  const portrait = await site.json('POST', `/${FOLDER_ID}`, {
    '@type': 'Image',
    id: 'hero-portrait',
    title: 'Hero, portrait crop',
    image: upload(PORTRAIT_FILE),
  });
  const contact = await site.json('POST', `/${FOLDER_ID}`, {
    '@type': 'Document',
    id: 'kontakt',
    title: 'Kontakt',
  });
  const services = await site.json('POST', `/${FOLDER_ID}`, {
    '@type': 'Document',
    id: 'leistungen',
    title: 'Leistungen',
  });

  const urls = {
    wide: wide['@id'],
    portrait: portrait['@id'],
    contact: contact['@id'],
    services: services['@id'],
  };

  await site.json('POST', `/${FOLDER_ID}`, {
    '@type': PAGE_TYPE,
    id: HERO_PAGE_ID,
    title: 'Derico Hero',
    ...somersault([heroNode(urls)]),
  });
  await site.json('POST', `/${FOLDER_ID}`, {
    '@type': PAGE_TYPE,
    id: LONG_PAGE_ID,
    title: 'Derico Hero, long headline',
    ...somersault([heroNode(urls, { headline: LONG_HEADLINE })]),
  });
  /* No hero: the page an ordinary editor and the insert-gate tests start
   * from, and the one the editor half authors into. */
  await site.json('POST', `/${FOLDER_ID}`, {
    '@type': PAGE_TYPE,
    id: EMPTY_PAGE_ID,
    title: 'Derico Hero, empty page',
  });

  for (const path of [
    `/${FOLDER_ID}`,
    `/${FOLDER_ID}/hero-wide`,
    `/${FOLDER_ID}/hero-portrait`,
    `/${FOLDER_ID}/kontakt`,
    `/${FOLDER_ID}/leistungen`,
    HERO_PAGE_PATH,
    LONG_PAGE_PATH,
    EMPTY_PAGE_PATH,
  ]) {
    await site.publish(path);
  }

  return {
    folder: `/${FOLDER_ID}`,
    heroPage: HERO_PAGE_PATH,
    longPage: LONG_PAGE_PATH,
    emptyPage: EMPTY_PAGE_PATH,
    urls,
  };
}

/** Read a page's hero node back, as the server serialized it. */
async function heroNodeOf(base, pagePath) {
  const site = new Site(base);
  const data = await site.json('GET', pagePath);
  const block = (data.blocks || {})[SOMERSAULT_BLOCK_ID] || {};
  return (block.value || []).find((node) => node['@type'] === 'derico-hero');
}

module.exports = {
  AUTH,
  COPY,
  EDITOR_PASSWORD,
  EDITOR_USER,
  DESIGN_ROOT,
  LONG_HEADLINE,
  PAGE_TYPE,
  PASSWORD,
  SOMERSAULT_BLOCK_ID,
  Site,
  USER,
  buildFixture,
  ensureEditorUser,
  heroNodeOf,
  removeFixture,
};
