/* E2E: the Derico Hero in `@@aurora-edit` (hero ticket 10).
 *
 * Four claims, in the order the ticket makes them:
 *
 * 1. A site administrator finds the block in the slash menu, inserts it, fills
 *    every field it offers — text, both crops, both links, the four legend
 *    rows — and the values survive a save and a reload.
 * 2. An ordinary editor does NOT find it in the slash menu, and a page that
 *    already carries a hero still RENDERS it for them rather than showing an
 *    unknown-block placeholder. This is the specific claim ticket 03's design
 *    makes, and the one most likely to be subtly wrong: the bundle loads for
 *    everyone and only the menu is filtered.
 * 3. Exactly one React is on the page — the duplicate-instance failure the
 *    import map exists to prevent (ticket 04 §1, ticket 08). A block bundle
 *    that shipped its own React would fail inside Plate, so the evidence is
 *    both structural (nothing but the entry and its sheet under the block's
 *    resource directory) and behavioural (the block mounted, and hooks ran).
 * 4. `<html lang>` on the editor matches the content language, and nothing
 *    clips at 320 or 375 on the canvas — the two checks ticket 15 handed
 *    over as unverified assumptions.
 *
 * Prerequisites: a running Plone with plonetheme.derico installed at profile
 * version 1001+, plone.restapi, and the mockup bundle (pat-auroraeditor,
 * pat-contentbrowser) reachable from the edit page.
 *
 * Environment: DERICO_E2E_BASE (default http://127.0.0.1:8081/Plone),
 * DERICO_E2E_USER / DERICO_E2E_PASSWORD (default admin/admin),
 * DERICO_E2E_CHROMIUM (a chromium executable), DERICO_E2E_PAGE_TYPE.
 *
 * Run: node hero-editor.e2e.js
 */
const { chromium } = require('playwright-core');

const {
  COPY,
  EDITOR_PASSWORD,
  EDITOR_USER,
  PASSWORD,
  USER,
  buildFixture,
  ensureEditorUser,
  heroNodeOf,
  removeFixture,
} = require('./hero-fixture');

const BASE = (
  process.env.DERICO_E2E_BASE ||
  process.env.AURORA_E2E_BASE ||
  'http://127.0.0.1:8081/Plone'
).replace(/\/+$/, '');
const EXECUTABLE = process.env.DERICO_E2E_CHROMIUM || process.env.AURORA_E2E_CHROMIUM;

/* The block's own resource directory. Everything the browser fetches from it
 * is the block; a React under this prefix would be a second copy. */
const BLOCK_RESOURCE = '++plone++plonetheme.derico.blocks/';

/* Deliberately NOT `COPY.kicker`. A fresh insert now arrives carrying the
 * mockup's copy, so authoring a field with the value it already holds proves
 * nothing — every check downstream would stay green with the sidebar wired to
 * nothing at all. One field authored to a value the seed cannot produce is
 * what keeps this pass honest. */
const AUTHORED_KICKER = 'Nachhaltige Lösungen, seit 2003';

const failures = [];
function check(condition, message) {
  if (condition) {
    console.log(`  ok   ${message}`);
  } else {
    console.error(`  FAIL ${message}`);
    failures.push(message);
  }
}

function launch() {
  return chromium.launch(EXECUTABLE ? { executablePath: EXECUTABLE } : {});
}

async function login(page, username, password) {
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded' });
  await page.fill('input[name="__ac_name"]', username);
  await page.fill('input[name="__ac_password"]', password);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
    page.click('button[name="buttons.login"], input[name="buttons.login"]'),
  ]);
}

async function openEditor(page, path) {
  await page.goto(`${BASE}${path}/@@aurora-edit`, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('[data-slate-editor]', { timeout: 90000 });
  await page.waitForTimeout(1500);
}

/** The slash menu's item labels, with the menu left open. */
async function slashMenuItems(page) {
  await page.locator('[data-slate-editor] [data-slate-node="element"]').last().click();
  await page.keyboard.type('/');
  await page.waitForTimeout(1500);
  return page.locator('[role="option"], [cmdk-item], [role="menuitem"]').allTextContents();
}

/**
 * Open one of the sidebar's fieldsets by its accordion title.
 *
 * cmsui gives every fieldset its own accordion and expands only the one whose
 * id is `default` (schema.ts), and react-aria keeps a collapsed panel's inputs
 * in the DOM under `hidden` — so a `fill()` on a folded fieldset fails on
 * actionability rather than on anything the block did. Idempotent: a fieldset
 * already open is left alone.
 */
async function openFieldset(page, title) {
  const trigger = page.locator(`button:has-text("${title}")`).first();
  await trigger.waitFor({ timeout: 15000 });
  if ((await trigger.getAttribute('aria-expanded')) !== 'true') {
    await trigger.click();
    await page.waitForTimeout(300);
  }
}

/** Type into a sidebar field, by its `name` or its `id`. */
async function fill(page, selector, value) {
  const field = page.locator(selector).first();
  await field.waitFor({ timeout: 15000 });
  await field.click();
  await field.fill(value);
  /* The sidebar writes straight onto the Plate node through
   * `onFormDataChange`; blurring is what settles a controlled input's last
   * keystroke before the next field steals focus. */
  await field.blur();
  await page.waitForTimeout(150);
}

/**
 * Pick a content item in one of the hero's reference fields.
 *
 * The widget is Blicca's object browser over pat-contentbrowser: an island of
 * patternslib markup inside a React sidebar. Its controls are reached by
 * structure rather than by label — this site runs in German, and a test that
 * matched "Select or Upload" would pass only on an English instance.
 */
async function pick(page, labelText, itemTitle) {
  const field = page
    .locator('.derico-hero-widget--reference')
    .filter({ has: page.locator(`label:text-is("${labelText}")`) })
    .first();
  await field.waitFor({ timeout: 15000 });
  await field.locator('.content-browser-wrapper a.btn').first().click();
  const item = page
    .locator('.contentItem[data-uuid]')
    .filter({ hasText: itemTitle })
    .first();
  await item.waitFor({ timeout: 20000 });
  await item.locator('.item-title').first().click();
  const confirm = page.locator('.preview button.btn-primary').first();
  await confirm.waitFor({ timeout: 15000 });
  await confirm.click();
  await page.waitForTimeout(800);
}

/** Every resource the page fetched from the block's own directory. */
function blockResources(page) {
  return page.evaluate(
    (prefix) =>
      performance
        .getEntriesByType('resource')
        .map((entry) => entry.name)
        .filter((name) => name.includes(prefix))
        .map((name) => name.split(prefix)[1].split('?')[0]),
    BLOCK_RESOURCE,
  );
}

const near = (a, b, slack = 2) =>
  typeof a === 'number' && typeof b === 'number' && Math.abs(a - b) <= slack;

/**
 * Where the hero's full-bleed box starts and ends on screen, and what it is
 * breaking out OF.
 *
 * Rendered pixels on purpose — see the caller. `column` is the width the
 * blocks that are not full-bleed keep, read from the surface itself
 * (`--layout-container-width`, the rung blocks_view.css derives from the
 * theme's own content column) rather than restated as a number here.
 */
function heroBleed(page) {
  return page.evaluate(() => {
    const hero = document.querySelector('.derico-hero');
    if (!hero) return null;
    const surface =
      document.querySelector('[data-slate-editor]') ||
      document.querySelector('.aurora-blocks-view');
    const rect = hero.getBoundingClientRect();
    /* Both lengths are read by LAYING THEM OUT, not by parsing the custom
     * property: the rail is declared in rem and `--layout-container-width`
     * in percent, and getComputedStyle hands back either token unresolved.
     * The column probe goes in flow (a positioned one would resolve its
     * percentage against the initial containing block, not the column). */
    const measure = (parent, css) => {
      const probe = document.createElement('div');
      probe.style.cssText = `position:relative;visibility:hidden;height:0;${css}`;
      parent.appendChild(probe);
      const width = Math.round(probe.getBoundingClientRect().width);
      probe.remove();
      return width;
    };
    /* Where the hero is actually PAINTED, which its own rect cannot say: the
     * canvas editable clips to its content column, and the rule that lifts
     * that clip for a breakout is one unlayered declaration a host theme's
     * Bootstrap can outrank with an `!important` utility of the same
     * Tailwind name. When it loses, the hero keeps a full-bleed rect and is
     * simply not on screen past the column — invisible to every width
     * measurement, and the only thing an author would actually notice. */
    let clip = null;
    for (
      let n = hero.parentElement;
      n && n !== document.documentElement;
      n = n.parentElement
    ) {
      const cs = getComputedStyle(n);
      if (cs.overflowX === 'visible' && cs.overflowY === 'visible') continue;
      const r = n.getBoundingClientRect();
      if (!clip || r.width < clip.right - clip.left) {
        clip = { left: Math.round(r.left), right: Math.round(r.right) };
      }
    }
    return {
      left: Math.round(rect.left),
      right: Math.round(rect.right),
      paintedLeft: clip
        ? Math.max(Math.round(rect.left), clip.left)
        : Math.round(rect.left),
      paintedRight: clip
        ? Math.min(Math.round(rect.right), clip.right)
        : Math.round(rect.right),
      column: measure(surface, 'width:var(--layout-container-width)'),
      viewport: window.innerWidth,
      rail: measure(
        document.body,
        'width:var(--aurora-full-bleed-offset, 0px)',
      ),
    };
  });
}

/** The hero's own box, and whether anything inside it overflows. */
function heroGeometry(page) {
  return page.evaluate(() => {
    const hero = document.querySelector('.derico-hero');
    if (!hero) return null;
    const rect = hero.getBoundingClientRect();
    return {
      width: Math.round(rect.width * 10) / 10,
      scrollWidth: hero.scrollWidth,
      clientWidth: hero.clientWidth,
      documentScrollWidth: document.documentElement.scrollWidth,
      documentClientWidth: document.documentElement.clientWidth,
    };
  });
}

(async () => {
  const fixture = await buildFixture(BASE);
  const editor = await ensureEditorUser(BASE);

  const browser = await launch();
  const admin = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await admin.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push((error.stack || String(error)).slice(0, 400)));

  try {
    /* ------------------------------------------------------------------ *
     * 1. The administrator inserts and authors the block
     * ------------------------------------------------------------------ */
    console.log('\n# site administrator');
    await login(page, USER, PASSWORD);
    await openEditor(page, fixture.emptyPage);

    const editorLang = await page.evaluate(() => document.documentElement.lang);
    const viewLang = await page.evaluate(async (url) => {
      const response = await fetch(url, { credentials: 'include' });
      const html = await response.text();
      return (html.match(/<html[^>]*\slang="([^"]*)"/i) || [])[1];
    }, `${BASE}${fixture.heroPage}`);
    /* Ticket 15 reasoned this out with no instance running and deliberately
     * did not trust it: `aurora_edit.pt` declares `lang="en"` on the element
     * carrying `metal:use-macro`, which METAL should discard in favour of
     * main_template's `lang python:portal_state.language()`. If it did not,
     * `hyphens: auto` would hyphenate a German canvas with English rules. */
    check(
      editorLang === viewLang,
      `editor and view agree on <html lang> (editor ${editorLang}, view ${viewLang})`,
    );

    const items = await slashMenuItems(page);
    check(
      items.some((item) => item.includes('Derico Hero')),
      `the slash menu offers the Derico Hero (${items.length} items)`,
    );

    await page
      .locator('[role="option"], [cmdk-item], [role="menuitem"]')
      .filter({ hasText: 'Derico Hero' })
      .first()
      .click();
    await page.waitForTimeout(2500);
    check(
      await page.evaluate(() => !!document.querySelector('.derico-hero')),
      'the inserted block renders its own root in the canvas',
    );

    /* -- the insert seed ---------------------------------------------- */
    /* A fresh insert arrives carrying the mockup's copy, written by the
     * block's own `edit` component (`defaults.ts`): Aurora inserts a node
     * with `@type` and nothing else, so an author who had to type all eight
     * fields from scratch could not see which field was which. Everything
     * below then EDITS that draft rather than filling an empty form, which is
     * why the authored kicker is deliberately not the seeded one — otherwise
     * every assertion in this pass would also pass with the sidebar broken. */
    const insertedText = await page.evaluate(
      () => document.querySelector('.derico-hero').innerText,
    );
    check(
      insertedText.includes(COPY.headline) &&
        insertedText.includes(COPY.legend[3].title),
      'a fresh insert already carries the mockup copy',
    );

    /* The SIDEBAR shows the seed too. The settings form mounts off the
     * still-unseeded node in the same commit as the canvas, and the seed
     * lands one render later — the wrapper has to remount the form on that
     * external write (plone-block-sidebar.tsx), or the author faces a wall
     * of empty inputs while the canvas shows the finished draft. */
    await page.waitForSelector('input[name="kicker"]', { timeout: 15000 });
    /* The legend inputs live in a folded fieldset; they are in the DOM and
     * carry their value either way, so the seed is read without opening it. */
    const sidebarSeed = await page.evaluate(() => ({
      kicker: document.querySelector('input[name="kicker"]')?.value,
      lastLegendTitle: document.querySelector('input#legend-3-title')?.value,
    }));
    check(
      sidebarSeed.kicker === COPY.kicker &&
        sidebarSeed.lastLegendTitle === COPY.legend[3].title,
      `the sidebar form shows the seeded values on first insert (kicker ${JSON.stringify(sidebarSeed.kicker)}, ring 4 ${JSON.stringify(sidebarSeed.lastLegendTitle)})`,
    );

    /* -- the body type, in the CANVAS: ticket 17/22 -------------------- */
    /* This assertion is the whole justification for the seam. The theme-layer
     * alternative would have fixed the published view and BROKEN this, because
     * Blicca states its Tailwind stack on `.aurora-blocks-view` only and the
     * canvas takes its stack from Aurora's scoped preflight instead. One
     * declaration in the block's own scope-wrapped sheet lands on both
     * surfaces, so the same numbers must come back here as in
     * `hero-view.e2e.js`. Pinned rather than assumed. */
    const canvasType = await page.evaluate(() => {
      const style = getComputedStyle(document.querySelector('.derico-hero'));
      const size = parseFloat(style.fontSize);
      return {
        family: style.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
        leading: Math.round((parseFloat(style.lineHeight) / size) * 100) / 100,
      };
    });
    check(
      canvasType.family === 'Source Sans 3',
      `the canvas hero's body family is the theme's (${canvasType.family})`,
    );
    check(
      Math.abs(canvasType.leading - 1.65) <= 0.02,
      `the canvas hero's leading is the design's 1.65 (${canvasType.leading})`,
    );

    /* -- the ring halo, in the canvas: ticket 20/23 -------------------- */
    const canvasHalo = await page.evaluate(() => {
      const disc = document.querySelector('.derico-hero .rings-disc');
      const halo = disc && disc.querySelector('.ring-halo');
      const ink = disc && disc.querySelector('.ring-ink');
      if (!halo || !ink) return null;
      const widths = (g) =>
        Array.from(g.querySelectorAll('circle')).map((c) =>
          parseFloat(getComputedStyle(c).strokeWidth),
        );
      return { halo: widths(halo), ink: widths(ink) };
    });
    check(!!canvasHalo, 'the canvas hero carries the ring halo');
    if (canvasHalo) {
      check(
        canvasHalo.halo.length === 8 &&
          canvasHalo.halo.every((w, i) => w - canvasHalo.ink[i] >= 3),
        `every canvas halo surrounds its ink by at least 3px (${JSON.stringify(canvasHalo.halo)} vs ${JSON.stringify(canvasHalo.ink)})`,
      );
    }

    /* -- one React ---------------------------------------------------- */
    const resources = await blockResources(page);
    check(
      resources.length > 0 && resources.every((name) => /^(hero\.js|blocks\.css)$/.test(name)),
      `the block ships only its entry and its sheet: ${JSON.stringify(resources)}`,
    );
    const importMap = await page.evaluate(() => {
      const script = document.querySelector('script[type="importmap"]');
      return script ? JSON.parse(script.textContent).imports : null;
    });
    check(
      importMap && typeof importMap.react === 'string' && importMap.react.includes('auroraeditor'),
      `the import map aliases react onto the editor remote (${importMap && importMap.react})`,
    );

    /* -- author every field ------------------------------------------- */
    await fill(page, 'input[name="kicker"]', AUTHORED_KICKER);
    await fill(page, 'input[name="headline"]', COPY.headline);
    await fill(page, 'textarea#lede', COPY.lede);
    await fill(page, 'input[name="cta_label"]', COPY.cta_label);
    await fill(page, 'input[name="link_label"]', COPY.link_label);
    await openFieldset(page, 'Ring legend');
    for (const [index, entry] of COPY.legend.entries()) {
      await fill(page, `input#legend-${index}-title`, entry.title);
      await fill(page, `input#legend-${index}-subtitle`, entry.subtitle);
    }
    await openFieldset(page, 'Targets and images');
    await pick(page, 'Primary target', 'Kontakt');
    await pick(page, 'Secondary target', 'Leistungen');
    await pick(page, 'Wide image', 'Hero, wide crop');
    await pick(page, 'Portrait image', 'Hero, portrait crop');

    const canvasText = await page.evaluate(
      () => document.querySelector('.derico-hero').innerText,
    );
    check(
      canvasText.includes(AUTHORED_KICKER) &&
        canvasText.includes(COPY.headline) &&
        canvasText.includes(COPY.legend[3].title),
      'the canvas previews what the sidebar was given',
    );

    /* -- save, and read the stored node back -------------------------- */
    await page.click('.aurora-save');
    await page.waitForTimeout(3000);

    const stored = await heroNodeOf(BASE, fixture.emptyPage);
    check(!!stored, 'the saved page holds a derico-hero node');
    if (stored) {
      check(stored.kicker === AUTHORED_KICKER, 'the edited kicker survived the save');
      check(stored.headline === COPY.headline, 'headline survived the save');
      check(stored.lede === COPY.lede, 'lede survived the save');
      check(stored.cta_label === COPY.cta_label, 'primary call to action survived the save');
      check(stored.link_label === COPY.link_label, 'secondary link survived the save');
      check(
        JSON.stringify((stored.legend || []).map((entry) => [entry.title, entry.subtitle])) ===
          JSON.stringify(COPY.legend.map((entry) => [entry.title, entry.subtitle])),
        'all four legend rows survived the save',
      );
      check(
        stored.blockWidth === 'full',
        `the editor materialised blockWidth (${stored.blockWidth})`,
      );
      /* Ticket 02's shape: one element carrying the bare `@id`. The object
       * browser hands over a whole brain; `derico_reference` trims it, so a
       * rename survives and no stale metadata is persisted.
       *
       * `image_scales` is the ONE key allowed beside it, and it is not the
       * block's: stock plone.restapi enriches any nested `@id` with it on
       * read and strips it again on write (ticket 01, contract §5.3), which
       * is why the two content picks come back bare and the two image picks
       * do not. Anything else in the object would be the widget failing to
       * trim. That the enrichment is not PERSISTED is pinned server-side by
       * `tests/test_hero_view.py`; from out here only the read is visible. */
      for (const field of ['cta_href', 'link_href', 'image_wide', 'image_portrait']) {
        const value = stored[field];
        const one = Array.isArray(value) && value.length === 1 && typeof value[0] === 'object';
        const keys = one ? Object.keys(value[0]).sort() : [];
        const shape =
          one &&
          typeof value[0]['@id'] === 'string' &&
          keys.every((key) => key === '@id' || key === 'image_scales');
        check(
          shape,
          `${field} is one bare @id (plus restapi's own image_scales, if any): ${JSON.stringify(keys)}`,
        );
      }
    }

    /* -- and the reload shows it -------------------------------------- */
    await openEditor(page, fixture.emptyPage);
    const reloaded = await page.evaluate(() => {
      const hero = document.querySelector('.derico-hero');
      return hero && { text: hero.innerText, images: hero.querySelectorAll('img').length };
    });
    check(!!reloaded, 'the reloaded editor renders the hero');
    check(
      reloaded && reloaded.text.includes(COPY.headline) && reloaded.text.includes(AUTHORED_KICKER),
      'the reloaded canvas shows the saved copy',
    );
    check(reloaded && reloaded.images > 0, 'the reloaded canvas previews the picked image');

    /* -- and it is FULL-BLEED there, not just on the page -------------- *
     *
     * `defaultBlockWidth: 'full'` only reaches the canvas as pixels through
     * BliccaFullWidthClassPlugin, which stamps `has--block-width--full` on
     * the block, and the breakout rule keyed off it (auroraeditor's
     * wrapper/src/styles/index.css). Storing `blockWidth: "full"` — checked
     * above — proves the data, not the width the author is looking at while
     * they decide; a hero that stopped at the content column in the canvas
     * would pass every other check in this file.
     *
     * Measured against the SAME page published, in the same window and
     * logged in, so the toolbar rail both surfaces subtract is in the
     * picture on both. Rendered pixels, not offsetWidth: the canvas is
     * `zoom`ed to fit (canvas-fit.ts) and the bleed is divided by that scale
     * precisely so it comes out at the window either way. */
    const canvasHero = await heroBleed(page);
    const publishedPage = await admin.newPage();
    await publishedPage.goto(`${BASE}${fixture.emptyPage}`, {
      waitUntil: 'domcontentloaded',
    });
    await publishedPage.waitForSelector('.derico-hero');
    const publishedHero = await heroBleed(publishedPage);
    await publishedPage.close();

    check(
      canvasHero && publishedHero,
      'the hero is measurable on both surfaces',
    );
    if (canvasHero && publishedHero) {
      check(
        near(canvasHero.left, publishedHero.left) &&
          near(canvasHero.right, publishedHero.right),
        'the canvas hero spans the same box as the published one ' +
          `(${canvasHero.left}-${canvasHero.right} vs ` +
          `${publishedHero.left}-${publishedHero.right})`,
      );
      check(
        near(canvasHero.right, canvasHero.viewport) &&
          canvasHero.left <= canvasHero.rail + 1,
        'the canvas hero bleeds from the toolbar rail to the window edge ' +
          `(${canvasHero.left}-${canvasHero.right} in a ` +
          `${canvasHero.viewport}px window with a ${canvasHero.rail}px rail)`,
      );
      /* The claim the breakout exists for: it is WIDER than the content
       * column the rest of the page keeps, by more than a rounding. */
      check(
        canvasHero.right - canvasHero.left > canvasHero.column + 8,
        'the canvas hero is wider than the content column ' +
          `(${canvasHero.right - canvasHero.left}px vs ${canvasHero.column}px)`,
      );
      /* And is PAINTED that wide. Everything above is satisfied by a hero
       * that is laid out full-bleed and then clipped to the column by the
       * canvas editable — the state this file's checks used to pass in. */
      check(
        near(canvasHero.paintedLeft, canvasHero.left) &&
          near(canvasHero.paintedRight, canvasHero.right),
        'nothing clips the canvas hero back to the column ' +
          `(painted ${canvasHero.paintedLeft}-${canvasHero.paintedRight} of ` +
          `${canvasHero.left}-${canvasHero.right})`,
      );
    }

    /* ------------------------------------------------------------------ *
     * 4. Nothing clips at 320 or 375 in the canvas (ticket 15)
     * ------------------------------------------------------------------ */
    console.log('\n# the canvas at mobile widths');
    await openEditor(page, fixture.longPage);
    for (const width of [375, 320]) {
      await page.setViewportSize({ width, height: 900 });
      await page.waitForTimeout(600);
      const geometry = await heroGeometry(page);
      check(
        geometry && geometry.scrollWidth === geometry.clientWidth,
        `@${width} the canvas hero does not overflow itself (${
          geometry && `${geometry.scrollWidth}/${geometry.clientWidth}`
        })`,
      );
      check(
        geometry && geometry.documentScrollWidth <= geometry.documentClientWidth,
        `@${width} the canvas page has no horizontal scroll (${
          geometry && `${geometry.documentScrollWidth}/${geometry.documentClientWidth}`
        })`,
      );
    }
    await page.setViewportSize({ width: 1920, height: 1080 });

    check(pageErrors.length === 0, `no uncaught page errors:\n${pageErrors.join('\n')}`);

    /* ------------------------------------------------------------------ *
     * 2. The ordinary editor: no insert, but the hero still renders
     * ------------------------------------------------------------------ */
    console.log('\n# ordinary editor');
    const ordinary = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const editorPage = await ordinary.newPage();
    const editorErrors = [];
    editorPage.on('pageerror', (error) =>
      editorErrors.push((error.stack || String(error)).slice(0, 400)),
    );

    await login(editorPage, editor.username, editor.password);
    await openEditor(editorPage, fixture.heroPage);

    check(
      await editorPage.evaluate(() => !!document.querySelector('.derico-hero')),
      'a page that already holds a hero still RENDERS it for an ordinary editor',
    );
    check(
      await editorPage.evaluate(
        () => !document.querySelector('[class*="unknown"], [data-unknown-block]'),
      ),
      'no unknown-block placeholder is shown instead',
    );
    const editorItems = await slashMenuItems(editorPage);
    check(
      editorItems.length > 0 && !editorItems.some((item) => item.includes('Derico Hero')),
      `the slash menu withholds the Derico Hero (${editorItems.length} items offered)`,
    );
    check(
      editorErrors.length === 0,
      `no uncaught page errors for the ordinary editor:\n${editorErrors.join('\n')}`,
    );
    await ordinary.close();
  } finally {
    await browser.close();
    if (!process.env.DERICO_E2E_KEEP) await removeFixture(BASE);
  }

  console.log(
    `\n${failures.length ? `FAILED (${failures.length})` : 'PASSED'} — hero-editor.e2e.js`,
  );
  process.exitCode = failures.length ? 1 : 0;
})();
