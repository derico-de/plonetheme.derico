/**
 * Ticket 02's degradation table, case for case.
 *
 * Nothing in the hero's schema is `required`, so a half-authored block has to
 * save and preview without throwing — and the canvas and the published page
 * have to agree on *what* it shows, or the author is previewing a different
 * page from the one they will publish. The server half implements this same
 * table from the same stored JSON; these are the canvas's half of it.
 *
 * The table (ticket 02):
 *
 * | State                          | Renders                                |
 * | ------------------------------ | -------------------------------------- |
 * | no headline / kicker / lede    | that element omitted, grid keeps shape |
 * | label OR target missing        | nothing — never a dead <a>             |
 * | both crops set                 | art direction, portrait under 55.99rem |
 * | one crop only                  | that image at every breakpoint         |
 * | no crop at all                 | no <picture>, no wash                  |
 * | legend entry half-filled       | numeral always; only the half with text|
 * | legend entry entirely empty    | numeral only                           |
 */
import { render } from '@testing-library/react';
import { describe, expect, test } from 'vitest';

import HeroView from './HeroView';
import type { HeroData } from './data';

const ref = (path: string) => [{ '@id': `http://nohost/plone/${path}` }];

const full: HeroData = {
  kicker: 'Nachhaltige Lösungen, seit über 20 Jahren',
  headline: 'Anwendungen, die bleiben.',
  lede: 'Wir entwickeln Geschäftsanwendungen …',
  cta_label: 'Erstgespräch vereinbaren',
  cta_href: ref('kontakt'),
  link_label: 'Alle Leistungen',
  link_href: ref('leistungen'),
  image_wide: ref('hero-wide'),
  image_portrait: ref('hero-portrait'),
  legend: [
    { title: 'schneller Prototyp', subtitle: 'in Wochen bedienbar' },
    { title: 'erste Anwendung', subtitle: 'trägt die tägliche Arbeit' },
    { title: 'erfahrener Begleiter', subtitle: 'wächst mit den Anforderungen' },
    { title: 'mit der Zeit gegangen', subtitle: 'offen, aktuell, migrierbar' },
  ],
};

const draw = (data: HeroData) => {
  const { container } = render(<HeroView data={data} />);
  const hero = container.querySelector('.derico-hero');
  if (!hero) throw new Error('the hero rendered no root element');
  return hero as HTMLElement;
};

describe('the hero renders its own root', () => {
  test('the component owns `.derico-hero`, never Aurora’s wrapper stamp', () => {
    // Ticket 07: `.block-derico-hero` is the block WRAPPER, which is the
    // full-bleed box on the view but only the column box in the canvas.
    const hero = draw(full);
    expect(hero.tagName).toBe('SECTION');
    expect(hero.className).toBe('derico-hero');
  });

  test('it never sets its own width', () => {
    expect(draw(full).getAttribute('style')).toBeNull();
  });
});

describe('text', () => {
  test.each(['kicker', 'headline', 'lede'] as const)(
    'a missing %s omits its element and nothing else',
    (field) => {
      const hero = draw({ ...full, [field]: '' });
      const selector = field === 'headline' ? 'h1' : `.${field}`;
      expect(hero.querySelector(selector)).toBeNull();
      expect(hero.querySelector('.home-hero__grid')).not.toBeNull();
      expect(hero.querySelector('.rings-figure')).not.toBeNull();
    },
  );

  test('whitespace is not content', () => {
    expect(draw({ ...full, headline: '   ' }).querySelector('h1')).toBeNull();
  });
});

describe('links', () => {
  test('both halves present renders the anchor', () => {
    const cta = draw(full).querySelector('a.button') as HTMLAnchorElement;
    expect(cta.textContent).toBe('Erstgespräch vereinbaren');
    expect(cta.getAttribute('href')).toBe('http://nohost/plone/kontakt');
  });

  test.each([
    ['no label', { cta_label: '' }],
    ['no target', { cta_href: undefined }],
  ])('%s renders nothing — never a dead anchor', (_name, patch) => {
    const hero = draw({ ...full, ...patch });
    expect(hero.querySelector('a.button')).toBeNull();
    // …and the secondary link is unaffected: the two are independent.
    expect(hero.querySelector('a.quiet-link')).not.toBeNull();
  });

  test('with neither link the action row itself is gone', () => {
    const hero = draw({
      ...full,
      cta_label: '',
      link_label: '',
    });
    expect(hero.querySelector('.action-row')).toBeNull();
  });
});

describe('the two crops', () => {
  test('both set gives art direction, portrait first', () => {
    const picture = draw(full).querySelector('picture.hero-media')!;
    const source = picture.querySelector('source')!;
    // First matching source wins, so the narrow one has to come first.
    expect(source.getAttribute('media')).toBe('(max-width: 55.99rem)');
    expect(source.getAttribute('srcset')).toContain('hero-portrait');
    expect(picture.querySelector('img')!.getAttribute('src')).toContain(
      'hero-wide',
    );
  });

  test.each([
    ['wide only', { image_portrait: undefined }, 'hero-wide'],
    ['portrait only', { image_wide: undefined }, 'hero-portrait'],
  ])('%s renders at every breakpoint', (_name, patch, expected) => {
    const picture = draw({ ...full, ...patch }).querySelector(
      'picture.hero-media',
    )!;
    // The source it has no image for is dropped, not emitted empty.
    expect(picture.querySelectorAll('source')).toHaveLength(0);
    expect(picture.querySelector('img')!.getAttribute('src')).toContain(
      expected,
    );
  });

  test('no crop at all: no picture and no wash', () => {
    const hero = draw({
      ...full,
      image_wide: undefined,
      image_portrait: undefined,
    });
    expect(hero.querySelector('picture')).toBeNull();
    expect(hero.querySelector('.hero-wash')).toBeNull();
  });

  test('the photograph is decorative — hidden, and with no alt to author', () => {
    const picture = draw(full).querySelector('picture.hero-media')!;
    expect(picture.getAttribute('aria-hidden')).toBe('true');
    expect(picture.querySelector('img')!.getAttribute('alt')).toBe('');
  });
});

describe('the ring legend', () => {
  const entries = (hero: HTMLElement) =>
    Array.from(hero.querySelectorAll('.ring-legend > div'));

  test('always exactly four rows, whatever is stored', () => {
    for (const stored of [undefined, [], [{ title: 'one' }]]) {
      expect(entries(draw({ ...full, legend: stored }))).toHaveLength(4);
    }
  });

  test('the numerals are position, never content', () => {
    const hero = draw({ ...full, legend: [] });
    expect(entries(hero).map((row) => row.querySelector('b')!.textContent)).toEqual(
      ['1', '2', '3', '4'],
    );
    // …and the markers over the disc agree with them.
    expect(
      Array.from(hero.querySelectorAll('.ring-markers li')).map(
        (marker) => marker.textContent,
      ),
    ).toEqual(['1', '2', '3', '4']);
  });

  test('a half-filled entry keeps its numeral and emits only the filled half', () => {
    const hero = draw({
      ...full,
      legend: [{ title: 'schneller Prototyp' }, {}, {}, { subtitle: 'nur Bildtext' }],
    });
    const [first, , , fourth] = entries(hero);
    expect(first.querySelector('dt')!.textContent).toBe('schneller Prototyp');
    expect(first.querySelector('dd')).toBeNull();
    expect(fourth.querySelector('dt')).toBeNull();
    expect(fourth.querySelector('dd')!.textContent).toBe('nur Bildtext');
  });

  test('an entirely empty entry is a numeral and nothing else', () => {
    const [row] = entries(draw({ ...full, legend: [] }));
    expect(row.querySelector('b')!.textContent).toBe('1');
    expect(row.querySelector('dt')).toBeNull();
    expect(row.querySelector('dd')).toBeNull();
  });

  test('the last ring is the one marked "now"', () => {
    const hero = draw(full);
    expect(entries(hero)[3].className).toBe('is-now');
    expect(hero.querySelectorAll('.ring-legend .is-now')).toHaveLength(1);
    expect(hero.querySelector('.ring-markers .is-now')!.textContent).toBe('4');
  });
});

describe('an entirely empty hero', () => {
  test('renders, and renders nothing it has no data for', () => {
    const hero = draw({});
    expect(hero.querySelector('h1')).toBeNull();
    expect(hero.querySelector('picture')).toBeNull();
    expect(hero.querySelector('.action-row')).toBeNull();
    // The rings are template, not content: they are there from insert.
    expect(hero.querySelectorAll('.rings-disc circle')).toHaveLength(16);
    expect(hero.querySelectorAll('.ring-legend > div')).toHaveLength(4);
  });

  /* Ticket 20/23. The halo is only a contrast guarantee if it is actually
   * PAIRED with the ink — a halo group that drifted to seven circles, or that
   * moved after the ink group and so paints over it, is a silent failure. The
   * geometry is stated twice in this file and twice again in `hero.pt`; this
   * is what makes that duplication safe rather than merely regretted. */
  test('pairs every ring stroke with a halo beneath it', () => {
    const hero = draw(full);
    const disc = hero.querySelector('.rings-disc')!;
    const halo = disc.querySelector('.ring-halo')!;
    const ink = disc.querySelector('.ring-ink')!;

    expect(halo).not.toBeNull();
    expect(ink).not.toBeNull();
    // Halo FIRST: SVG paints in document order, so the reverse hides the ink.
    expect(halo.compareDocumentPosition(ink) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();

    const circles = (group: Element) =>
      Array.from(group.querySelectorAll('circle')).map((c) =>
        ['cx', 'cy', 'r', 'class'].map((a) => c.getAttribute(a)).join('|'),
      );
    expect(circles(halo)).toHaveLength(8);
    // Same cx/cy/r AND the same per-circle class, so `.ring-now`'s heavier
    // stroke gets the heavier halo rather than the default one.
    expect(circles(halo)).toEqual(circles(ink));
    // Both groups carry the translate, or the halo sits 105 units to the left.
    expect(halo.getAttribute('transform')).toBe(ink.getAttribute('transform'));
  });
});
