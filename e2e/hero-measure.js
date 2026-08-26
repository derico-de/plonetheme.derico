/* The shared geometry, type and contrast vocabulary for the hero tests.
 *
 * Two surfaces answer to the same questions here: the published Plone page
 * (`section.derico-hero`) and the design source served straight from
 * `docs/design/derico.de/site` (`section.home-hero`). Everything that is
 * meant to match the mockup is read through one function on both, so a
 * difference is a difference in the page and never in how it was measured.
 *
 * Contrast is measured against the pixels the text actually sits on. The hero
 * paints ground, then photograph (a negative-z-index child paints above the
 * element background and below in-flow content), then the wash gradient — so
 * the computed `background-color` of any ancestor is not what the reader
 * sees, and a photograph is not uniform enough for one number to stand for
 * it.
 *
 * The method is a difference of two screenshots: one as rendered, one with
 * the glyphs painted transparent. Where they differ, a glyph covered that
 * pixel; the second shot says what was underneath it. Contrast is measured
 * over those covered pixels alone — not over the text's whole box, which
 * would judge the design by a bright patch of forest no letter sits on — and
 * reported three ways: the worst ratio, the median, and the SHARE of the
 * glyph area below the threshold. The share is what separates a speckle of
 * bright leaf under one letter from a line nobody can read; the worst pixel
 * alone cannot tell those apart.
 *
 * `color: transparent` rather than `visibility: hidden` on purpose: hiding an
 * element takes its own background with it, and the call to action and the
 * ring markers are read against exactly that.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

/** The elements whose size, type and contrast the design fixes. */
const PARTS = {
  hero: ['section.derico-hero', 'section.home-hero'],
  grid: ['.home-hero__grid', '.home-hero__grid'],
  kicker: ['.kicker', '.kicker'],
  headline: ['h1', 'h1'],
  lede: ['.lede', '.lede'],
  cta: ['.action-row .button', '.action-row .button'],
  quiet: ['.action-row .quiet-link', '.action-row .quiet-link'],
  figure: ['.rings-figure', '.rings-figure'],
  stage: ['.rings-stage', '.rings-stage'],
  disc: ['.rings-disc', '.rings-disc'],
  marker: ['.ring-markers li', '.ring-markers li'],
  legend: ['.ring-legend', '.ring-legend'],
  legendTitle: ['.ring-legend dt', '.ring-legend dt'],
  legendCaption: ['.ring-legend dd', '.ring-legend dd'],
  legendNumeral: ['.ring-legend b', '.ring-legend b'],
  media: ['.hero-media', '.hero-media'],
};

/** Which column of PARTS a surface reads: 0 = Plone page, 1 = mockup. */
const PLONE = 0;
const MOCKUP = 1;

function selectors(surface) {
  return Object.fromEntries(
    Object.entries(PARTS).map(([name, pair]) => [name, pair[surface]]),
  );
}

/**
 * Everything one viewport of one surface has to say: the boxes, the type
 * sizes, and whether anything overflows.
 */
async function measure(page, surface) {
  return page.evaluate((map) => {
    const round = (value) => Math.round(value * 10) / 10;
    const box = (element) => {
      if (!element) return null;
      const rect = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      return {
        width: round(rect.width),
        height: round(rect.height),
        left: round(rect.left),
        top: round(rect.top),
        fontSize: round(parseFloat(style.fontSize)),
        lineHeight: style.lineHeight,
        color: style.color,
        scrollWidth: element.scrollWidth,
        clientWidth: element.clientWidth,
      };
    };

    const hero = document.querySelector(map.hero);
    const parts = Object.fromEntries(
      Object.entries(map).map(([name, selector]) => [
        name,
        box(name === 'hero' ? hero : hero && hero.querySelector(selector)),
      ]),
    );

    /* Every text node the hero renders, so "no text below 15px" is a claim
     * about the whole block and not about the parts this file happens to
     * name. Empty and whitespace-only nodes carry no type. */
    const smallest = [];
    if (hero) {
      const walker = document.createTreeWalker(hero, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        if (!node.textContent.trim()) continue;
        const element = node.parentElement;
        if (!element || !element.getClientRects().length) continue;
        smallest.push({
          text: node.textContent.trim().slice(0, 40),
          tag: element.tagName.toLowerCase(),
          className: element.className || '',
          fontSize: round(parseFloat(getComputedStyle(element).fontSize)),
        });
      }
    }
    smallest.sort((a, b) => a.fontSize - b.fontSize);

    const gridStyle = hero
      ? getComputedStyle(hero.querySelector(map.grid) || hero)
      : null;

    return {
      viewport: { width: innerWidth, height: innerHeight },
      parts,
      /* The resolved track list — "1fr" is one column, two entries is the
       * two-column desktop layout. The container query decides it. */
      gridTemplateColumns: gridStyle ? gridStyle.gridTemplateColumns : null,
      columns: gridStyle
        ? gridStyle.gridTemplateColumns.trim().split(/\s+/).filter(Boolean).length
        : 0,
      document: {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      },
      minFontSize: smallest.length ? smallest[0].fontSize : null,
      smallestText: smallest.slice(0, 5),
    };
  }, selectors(surface));
}

/** The `<picture>` the server built: its sources, in order, and the `<img>`. */
async function pictureOf(page, surface) {
  return page.evaluate((map) => {
    const picture = document.querySelector(`${map.hero} ${map.media}`);
    if (!picture) return null;
    const img = picture.querySelector('img');
    return {
      ariaHidden: picture.getAttribute('aria-hidden'),
      sources: [...picture.querySelectorAll('source')].map((source) => ({
        media: source.getAttribute('media'),
        type: source.getAttribute('type'),
        sizes: source.getAttribute('sizes'),
        srcset: source.getAttribute('srcset'),
      })),
      img: img && {
        src: img.getAttribute('src'),
        srcset: img.getAttribute('srcset'),
        sizes: img.getAttribute('sizes'),
        alt: img.getAttribute('alt'),
        loading: img.getAttribute('loading'),
        fetchpriority: img.getAttribute('fetchpriority'),
        currentSrc: img.currentSrc,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        renderedWidth: Math.round(img.getBoundingClientRect().width),
      },
    };
  }, selectors(surface));
}

/**
 * Worst-case WCAG contrast for every text element in the hero, against the
 * composited pixels behind it.
 *
 * Screenshots the hero twice — as rendered, and with every glyph painted
 * transparent — then hands both images back to the page and compares them in
 * a canvas: a pixel the two disagree on is a pixel a glyph covered, and the
 * second image says what it covered. Reading the pixels in the page rather
 * than decoding a PNG here keeps this dependency-free, and a data URL is
 * same-origin so the canvas never taints.
 */
async function contrastReport(page, surface, textSelectors) {
  const map = selectors(surface);
  /* Page coordinates, not viewport coordinates: at 375 the hero is three
   * screens tall, and a viewport-clipped screenshot would simply miss the
   * ring legend — which is exactly the part sitting on the busiest pixels. */
  const heroBox = await page.evaluate((map) => {
    const hero = document.querySelector(map.hero);
    if (!hero) return null;
    const rect = hero.getBoundingClientRect();
    return {
      x: rect.x + scrollX,
      y: rect.y + scrollY,
      width: rect.width,
      height: rect.height,
    };
  }, map);
  if (!heroBox) return [];

  const targets = await page.evaluate(
    ({ map, textSelectors }) => {
      const hero = document.querySelector(map.hero);
      return textSelectors.flatMap((selector) =>
        [...hero.querySelectorAll(selector)]
          .filter((element) => element.textContent.trim() && element.getClientRects().length)
          .map((element) => {
            const rect = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            return {
              selector,
              text: element.textContent.trim().slice(0, 30),
              color: style.color,
              fontSize: parseFloat(style.fontSize),
              fontWeight: style.fontWeight,
              rect: {
                x: rect.x + scrollX,
                y: rect.y + scrollY,
                width: rect.width,
                height: rect.height,
              },
            };
          }),
      );
    },
    { map, textSelectors },
  );

  const clip = {
    x: heroBox.x,
    y: heroBox.y,
    width: heroBox.width,
    height: heroBox.height,
  };
  const painted = await page.screenshot({ clip, fullPage: true });
  const transparent = await page.addStyleTag({
    content: `${map.hero} * {
      color: transparent !important;
      -webkit-text-fill-color: transparent !important;
      text-shadow: none !important;
      text-decoration-color: transparent !important;
    }`,
  });
  const bare = await page.screenshot({ clip, fullPage: true });
  await page.evaluate((handle) => handle.remove(), transparent);

  return page.evaluate(
    async ({ paintedUrl, bareUrl, origin, targets }) => {
      const load = async (url) => {
        const image = new Image();
        image.src = url;
        await image.decode();
        const canvas = document.createElement('canvas');
        canvas.width = image.width;
        canvas.height = image.height;
        const context = canvas.getContext('2d', { willReadFrequently: true });
        context.drawImage(image, 0, 0);
        return { image, context };
      };
      const { image, context: paintedContext } = await load(paintedUrl);
      const { context } = await load(bareUrl);

      const channel = (value) => {
        const v = value / 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      };
      const luminance = ([r, g, b]) =>
        0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
      /* Resolve whatever colour syntax the sheet used — Chromium hands back
       * `oklch(…)` verbatim for an oklch-authored colour, and reading those
       * three numbers as RGB makes every ratio come out at 1.0. Painting the
       * colour and reading the pixel back is syntax-agnostic. */
      const swatch = document.createElement('canvas');
      swatch.width = swatch.height = 1;
      const swatchContext = swatch.getContext('2d');
      const parse = (color) => {
        swatchContext.clearRect(0, 0, 1, 1);
        swatchContext.fillStyle = color;
        swatchContext.fillRect(0, 0, 1, 1);
        return [...swatchContext.getImageData(0, 0, 1, 1).data].slice(0, 3);
      };
      const ratio = (a, b) => {
        const [hi, lo] = a > b ? [a, b] : [b, a];
        return (hi + 0.05) / (lo + 0.05);
      };

      /* The image is the hero's own box, so page coordinates shift by its
       * origin; devicePixelRatio is 1 in these runs but is applied anyway so
       * a retina emulation would not silently sample the wrong pixels. */
      const scale = image.width / origin.width;
      return targets.map((target) => {
        const x0 = Math.max(0, Math.floor((target.rect.x - origin.x) * scale));
        const y0 = Math.max(0, Math.floor((target.rect.y - origin.y) * scale));
        const w = Math.max(1, Math.min(Math.ceil(target.rect.width * scale), image.width - x0));
        const h = Math.max(1, Math.min(Math.ceil(target.rect.height * scale), image.height - y0));
        const { data } = context.getImageData(x0, y0, w, h);
        const glyphs = paintedContext.getImageData(x0, y0, w, h).data;
        const foreground = luminance(parse(target.color));
        let worst = Infinity;
        let worstPixel = null;
        let covered = 0;
        const ratios = [];
        for (let index = 0; index < data.length; index += 4) {
          /* A pixel a glyph covered: the two shots disagree there. The
           * threshold skips the anti-aliased fringe, whose blended colour
           * is not the text colour and would report a contrast no reader
           * ever experiences. */
          const difference = Math.max(
            Math.abs(data[index] - glyphs[index]),
            Math.abs(data[index + 1] - glyphs[index + 1]),
            Math.abs(data[index + 2] - glyphs[index + 2]),
          );
          if (difference < 48) continue;
          covered += 1;
          const background = luminance([data[index], data[index + 1], data[index + 2]]);
          const value = ratio(foreground, background);
          ratios.push(value);
          if (value < worst) {
            worst = value;
            worstPixel = [data[index], data[index + 1], data[index + 2]];
          }
        }
        /* WCAG "large text": >= 24px, or >= 18.66px when bold. */
        const large =
          target.fontSize >= 24 ||
          (target.fontSize >= 18.66 && Number(target.fontWeight) >= 700);
        return {
          selector: target.selector,
          text: target.text,
          color: target.color,
          fontSize: target.fontSize,
          large,
          required: large ? 3 : 4.5,
          /* `covered === 0` means no glyph pixel was found — a transparent
           * text colour, or an element the difference could not see. Reported
           * as null rather than as a passing Infinity. */
          contrast: covered ? Math.round(worst * 100) / 100 : null,
          /* The worst pixel alone cannot tell a speckle in a photograph from
           * a genuinely unreadable line, so the share of the glyph area that
           * misses the threshold is reported next to it. A letter over a
           * single bright leaf is not the same defect as a paragraph over a
           * bright sky, and the two want different answers. */
          belowShare: covered
            ? Math.round(
                (ratios.filter((value) => value < (large ? 3 : 4.5)).length / covered) * 1000,
              ) / 1000
            : null,
          median: covered
            ? Math.round(ratios.sort((a, b) => a - b)[Math.floor(ratios.length / 2)] * 100) / 100
            : null,
          covered,
          worstPixel,
        };
      });
    },
    {
      paintedUrl: `data:image/png;base64,${painted.toString("base64")}`,
      bareUrl: `data:image/png;base64,${bare.toString("base64")}`,
      origin: heroBox,
      targets,
    },
  );
}

/**
 * Serve a directory over HTTP on an ephemeral port.
 *
 * The design source is measured in a browser, and Chromium refuses `file://`
 * subresources the way this page needs them, so it gets a real origin.
 */
function serveStatic(root) {
  const TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.jpg': 'image/jpeg',
    '.webp': 'image/webp',
    '.avif': 'image/avif',
    '.png': 'image/png',
    '.woff2': 'font/woff2',
  };
  const server = http.createServer((request, response) => {
    const relative = decodeURIComponent(request.url.split('?')[0]).replace(/^\/+/, '');
    const file = path.join(root, relative);
    if (!file.startsWith(root)) {
      response.writeHead(403).end();
      return;
    }
    fs.readFile(file, (error, body) => {
      if (error) {
        response.writeHead(404).end();
        return;
      }
      response.writeHead(200, {
        'content-type': TYPES[path.extname(file)] || 'application/octet-stream',
        /* The sheet and the images are read fresh on every run: a cached copy
         * of a design source that has since been edited is the one way this
         * comparison can lie. */
        'cache-control': 'no-store',
      });
      response.end(body);
    });
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({
        url: `http://127.0.0.1:${port}`,
        close: () => new Promise((done) => server.close(done)),
      });
    });
  });
}

module.exports = {
  MOCKUP,
  PARTS,
  PLONE,
  contrastReport,
  measure,
  pictureOf,
  selectors,
  serveStatic,
};
