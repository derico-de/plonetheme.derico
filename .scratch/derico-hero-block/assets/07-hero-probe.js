/* Ticket 07 probe — NOT code to keep.
 *
 * Injects the mockup's hero markup plus 07-hero-probe.css into a LIVE page,
 * so the rings can be looked at inside @@aurora-edit and on the public
 * blocks view before either half of the block exists.
 *
 * Usage — paste into the devtools console on either surface:
 *   await dericoHeroProbe()                      // hero class on the block wrapper
 *   await dericoHeroProbe({ heroOn: 'section' }) // hero class on an inner <section>
 *   dericoHeroProbe.measure()                    // numbers, both surfaces
 *   dericoHeroProbe.remove()
 *
 * `heroOn` exists because ticket 06 left it open which element the hero paints
 * on. plate.py:346 stamps `block block-derico-hero has--block-width--full` on
 * the block WRAPPER, and blocks_view.css:733 breaks that element out — so on
 * the public view the wrapper is the hero's box. In the canvas the breakout
 * lands one level in, on `.has--block-width--full > .block-inner-container`
 * (wrapper/src/styles/index.css:31). If the hero paints on the wrapper on both
 * surfaces, the canvas paints the dark ground at COLUMN width while the inner
 * container breaks out past it. Run both settings and compare.
 */
(function () {
  const CSS_URL = new URL('07-hero-probe.css', document.currentScript?.src || location.href).href;

  const IMG = '/++theme++derico/hero.jpg'; // replaced below if not resolvable
  const MARKUP = (imgSrc) => `
<picture class="hero-media" aria-hidden="true">
  <img src="${imgSrc}" alt="" fetchpriority="high" decoding="async">
</picture>
<div class="hero-wash" aria-hidden="true"></div>
<div class="home-hero__grid">
  <div>
    <p class="kicker">Nachhaltige Lösungen, seit über 20 Jahren</p>
    <h1>Anwendungen, die bleiben.</h1>
    <p class="lede">Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem JavaScript und Open Source. Wartbarkeit, offene Standards und klare Entscheidungen sichern ihren Wert über viele Jahre.</p>
    <div class="action-row">
      <a class="button" href="#">Erstgespräch vereinbaren</a>
      <a class="quiet-link" href="#">Alle Leistungen</a>
    </div>
  </div>
  <figure class="rings-figure">
    <div class="rings-stage">
      <svg class="rings-disc" viewBox="0 0 680 470" role="img" aria-label="Wachstumsringe einer Anwendung">
        <g transform="translate(105 0)">
          <circle cx="150" cy="235" r="40" class="ring-thin"/>
          <circle cx="153" cy="232" r="80"/>
          <circle cx="147" cy="238" r="125" class="ring-thin"/>
          <circle cx="154" cy="231" r="170"/>
          <circle cx="148" cy="237" r="215" class="ring-thin"/>
          <circle cx="152" cy="234" r="250"/>
          <circle cx="150" cy="235" r="290" class="ring-now"/>
          <circle cx="151" cy="234" r="315" class="ring-future"/>
        </g>
      </svg>
      <ol class="ring-markers" aria-hidden="true"><li>1</li><li>2</li><li>3</li><li class="is-now">4</li></ol>
    </div>
    <dl class="ring-legend">
      <div><b>1</b><dt>schneller Prototyp</dt><dd>in Wochen bedienbar</dd></div>
      <div><b>2</b><dt>erste Anwendung</dt><dd>trägt die tägliche Arbeit</dd></div>
      <div><b>3</b><dt>erfahrener Begleiter</dt><dd>wächst mit den Anforderungen</dd></div>
      <div class="is-now"><b>4</b><dt>mit der Zeit gegangen</dt><dd>offen, aktuell, migrierbar</dd></div>
    </dl>
  </figure>
</div>`;

  function surface() {
    if (document.querySelector('.aurora-blocks-view')) return 'view';
    if (document.querySelector('.aurora-editor')) return 'editor';
    return null;
  }

  /* Where a real block sits, found rather than hardcoded — the two surfaces
   * nest differently and only the live DOM knows how.
   *
   * Public view:  .aurora-blocks-view > .block
   * Canvas:       … > .slate-blockWrapper.flow-root > .block > .block-inner-container
   *
   * Returns {host, wrapperClass}: insert into `host`, wrapped in a div of
   * `wrapperClass` when the surface interposes one. */
  function blockSlot(where) {
    const anyBlock = document.querySelector(
      where === 'view' ? '.aurora-blocks-view .block' : '.aurora-editor .block'
    );
    if (!anyBlock) {
      return {
        host: document.querySelector(where === 'view' ? '.aurora-blocks-view' : '.aurora-editor'),
        wrapperClass: where === 'view' ? null : 'slate-blockWrapper flow-root',
      };
    }
    const parent = anyBlock.parentElement;
    if (parent.classList.contains('slate-blockWrapper')) {
      return { host: parent.parentElement, wrapperClass: parent.className };
    }
    return { host: parent, wrapperClass: null };
  }

  async function probe(opts = {}) {
    const heroOn = opts.heroOn || 'wrapper';
    const where = opts.surface || surface();
    if (!where) throw new Error('neither .aurora-blocks-view nor .aurora-editor on this page');

    remove();
    await ensureCss(opts.cssUrl || CSS_URL);

    const imgSrc = opts.image || (await firstUsableImage());
    const wrap = document.createElement('div');
    wrap.dataset.dericoProbe = '1';
    wrap.className = 'block block-derico-hero has--block-width--full';
    wrap.dataset.blockType = 'derico-hero';
    wrap.style.setProperty('--block-width', '100%');

    /* The canvas nests one level deeper than the view: Aurora puts every
     * block's content inside .block-inner-container, and that is the element
     * its full-bleed rule targets. Mirror the real anatomy per surface. */
    let host = wrap;
    if (where === 'editor') {
      const inner = document.createElement('div');
      inner.className = 'block-inner-container';
      wrap.appendChild(inner);
      host = inner;
    }

    /* The canvas editable is white-space: pre-wrap, so every newline between
     * two elements becomes a real line box — the raw-HTML template would add
     * ~48px between each legend row and ~120px inside the rings stage, which
     * the React block (JSX drops inter-element whitespace) never would. Strip
     * them, or the probe measures its own indentation. */
    const stripWhitespace = (node) => {
      [...node.childNodes].forEach((n) => {
        if (n.nodeType === 3 && !n.nodeValue.trim()) n.remove();
        else if (n.nodeType === 1) stripWhitespace(n);
      });
    };

    if (heroOn === 'section') {
      wrap.classList.remove('block-derico-hero');
      wrap.classList.add('block-derico-hero-probe-wrapper');
      const section = document.createElement('section');
      section.className = 'block-derico-hero';
      section.innerHTML = MARKUP(imgSrc);
      host.appendChild(section);
    } else {
      host.innerHTML = MARKUP(imgSrc);
    }

    stripWhitespace(wrap);

    const slot = blockSlot(where);
    let top = wrap;
    if (slot.wrapperClass) {
      top = document.createElement('div');
      top.className = slot.wrapperClass;
      top.appendChild(wrap);
    }
    top.dataset.dericoProbe = '1';
    slot.host.insertBefore(top, slot.host.firstChild);
    return measure();
  }

  function ensureCss(href) {
    return new Promise((resolve, reject) => {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      link.dataset.dericoProbe = '1';
      link.onload = resolve;
      link.onerror = () => reject(new Error('probe CSS did not load from ' + href));
      document.head.appendChild(link);
    });
  }

  /* Any image already on the site beats a broken <img> box for judging the
   * wash; ticket 05 settled delivery, this only needs pixels to darken. */
  async function firstUsableImage() {
    const img = [...document.images].find((i) => i.naturalWidth > 600);
    return img ? img.currentSrc || img.src : IMG;
  }

  function measure() {
    const el = document.querySelector('[data-derico-probe].block');
    if (!el) return null;
    const hero = el.querySelector('.block-derico-hero') || el;
    const inner = el.querySelector('.block-inner-container');
    const grid = el.querySelector('.home-hero__grid');
    const disc = el.querySelector('.rings-disc');
    const marker = el.querySelector('.ring-markers li');
    const dd = el.querySelector('.ring-legend dd');
    const r = (n) => (n ? Math.round(n.getBoundingClientRect().width * 10) / 10 : null);
    const x = (n) => (n ? Math.round(n.getBoundingClientRect().left * 10) / 10 : null);
    const cs = getComputedStyle(document.body);
    return {
      surface: surface(),
      viewport: window.innerWidth,
      documentWidth: document.documentElement.clientWidth,
      fullBleedOffset: cs.getPropertyValue('--aurora-full-bleed-offset').trim(),
      blockWrapper: { width: r(el), left: x(el) },
      innerContainer: inner ? { width: r(inner), left: x(inner) } : null,
      heroBox: { width: r(hero), left: x(hero) },
      gridWidth: r(grid),
      gridColumns: grid ? getComputedStyle(grid).gridTemplateColumns : null,
      containerSwitched: hero ? hero.getBoundingClientRect().width >= 56 * 16 : null,
      ringsDiscWidth: r(disc),
      markerSize: marker ? getComputedStyle(marker).width : null,
      legendCaptionFontSize: dd ? getComputedStyle(dd).fontSize : null,
      horizontalScroll: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    };
  }

  function remove() {
    document.querySelectorAll('[data-derico-probe]').forEach((n) => n.remove());
  }

  probe.measure = measure;
  probe.remove = remove;
  window.dericoHeroProbe = probe;
})();
