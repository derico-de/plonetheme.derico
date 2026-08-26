/**
 * The insert seed: the mockup's words, written once, editable afterwards.
 *
 * Two separate claims, and they fail for different reasons:
 *
 * 1. **The copy is the mockup's.** Read out of
 *    `docs/design/derico.de/site/de/index.html` rather than restated here, so
 *    a headline reworded in the design and not in the block is a red test
 *    instead of a page nobody notices is a version behind. The same lockstep
 *    reasoning as `tests/test_block_addon_lockstep.py`, against a file that
 *    lives in this repo and so can never merely skip.
 * 2. **It is written exactly once.** A seed that re-runs is not a default, it
 *    is a floor the author cannot get below — the failure mode is silent and
 *    only shows up when someone deliberately empties a field.
 */
import { render } from '@testing-library/react';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { describe, expect, test, vi } from 'vitest';

import HeroEdit from './HeroEdit';
import { LEGEND_LENGTH, legend } from './data';
import type { HeroData } from './data';
import { HERO_DEFAULTS, HERO_FIELDS, seeded, unseeded } from './defaults';

/* ── the mockup, as the design published it ─────────────────────────────── */

const MOCKUP = 'docs/design/derico.de/site/de/index.html';

/**
 * Found by walking up from the working directory, not by `import.meta.url`:
 * Vitest serves test modules over its own dev server, so `import.meta.url` is
 * an http URL here and `new URL(…)` against it is not a path at all.
 */
function mockupFile(): string {
  let directory = process.cwd();
  for (let up = 0; up < 4; up += 1) {
    const candidate = join(directory, MOCKUP);
    if (existsSync(candidate)) return candidate;
    directory = dirname(directory);
  }
  throw new Error(`no ${MOCKUP} above ${process.cwd()}`);
}

/** The mockup's `<section class="home-hero">`, parsed. */
function mockupHero(): HTMLElement {
  const html = readFileSync(mockupFile(), 'utf8');
  const document = new DOMParser().parseFromString(html, 'text/html');
  const hero = document.querySelector('section.home-hero');
  if (!hero) throw new Error(`no .home-hero in ${MOCKUP}`);
  return hero as HTMLElement;
}

const said = (hero: HTMLElement, selector: string) =>
  hero.querySelector(selector)?.textContent?.replace(/\s+/g, ' ').trim();

describe('the seed says what the mockup says', () => {
  const hero = mockupHero();

  test.each([
    ['kicker', 'p.kicker'],
    ['headline', 'h1'],
    ['lede', 'p.lede'],
    ['cta_label', '.action-row a.button'],
    ['link_label', '.action-row a.quiet-link'],
  ] as const)('%s', (field, selector) => {
    expect(HERO_DEFAULTS[field]).toBe(said(hero, selector));
  });

  test('the ring legend, all four rows in order', () => {
    const rows = Array.from(hero.querySelectorAll('.ring-legend > div')).map(
      (row) => ({
        title: said(row as HTMLElement, 'dt'),
        subtitle: said(row as HTMLElement, 'dd'),
      }),
    );
    expect(rows).toHaveLength(LEGEND_LENGTH);
    expect(legend(HERO_DEFAULTS.legend)).toEqual(rows);
  });

  test('nothing site-specific is seeded', () => {
    // Links and images are references into one site's content; a plausible
    // path that resolves nowhere is worse than an empty field.
    for (const field of ['cta_href', 'link_href', 'image_wide', 'image_portrait'] as const) {
      expect(field in HERO_DEFAULTS).toBe(false);
    }
  });
});

/* ── written once ───────────────────────────────────────────────────────── */

describe('unseeded', () => {
  test('a node Aurora has just inserted carries no hero key', () => {
    expect(unseeded({} as HeroData)).toBe(true);
  });

  test('a seeded node is not unseeded', () => {
    expect(unseeded(seeded({}))).toBe(false);
  });

  test.each(HERO_FIELDS)(
    'an emptied %s still counts as seeded — the keys answer, not the values',
    (field) => {
      expect(unseeded({ [field]: '' } as HeroData)).toBe(false);
    },
  );
});

describe('seeded', () => {
  test('keeps what the host already put on the node', () => {
    const node = { '@type': 'derico-hero', blockWidth: 'full' } as HeroData;
    expect(seeded(node)).toMatchObject(node);
  });
});

/* ── the canvas is where it happens ─────────────────────────────────────── */

const draw = (data: HeroData) => {
  const onChangeBlock = vi.fn();
  const view = render(
    <HeroEdit block="hero-1" data={data} onChangeBlock={onChangeBlock} />,
  );
  return { onChangeBlock, view };
};

describe('HeroEdit seeds a fresh insert', () => {
  test('a bare node is filled in, under its own block id', () => {
    const { onChangeBlock } = draw({} as HeroData);
    expect(onChangeBlock).toHaveBeenCalledTimes(1);
    expect(onChangeBlock).toHaveBeenCalledWith(
      'hero-1',
      expect.objectContaining(HERO_DEFAULTS),
    );
  });

  test('an authored hero is left alone', () => {
    const { onChangeBlock } = draw({ headline: 'Etwas ganz anderes' });
    expect(onChangeBlock).not.toHaveBeenCalled();
  });

  test('a hero the author emptied is left empty', () => {
    const cleared = Object.fromEntries(
      HERO_FIELDS.map((field) => [field, '']),
    ) as HeroData;
    const { onChangeBlock } = draw(cleared);
    expect(onChangeBlock).not.toHaveBeenCalled();
  });

  test('re-rendering before the write lands does not seed twice', () => {
    // The host re-renders the canvas from its own state, so the seeded data
    // can arrive a render late — and `data` is a fresh object every time.
    const { onChangeBlock, view } = draw({} as HeroData);
    view.rerender(
      <HeroEdit block="hero-1" data={{}} onChangeBlock={onChangeBlock} />,
    );
    expect(onChangeBlock).toHaveBeenCalledTimes(1);
  });

  test('without a host to write to, it renders anyway', () => {
    expect(() => render(<HeroEdit data={{}} />)).not.toThrow();
  });
});
