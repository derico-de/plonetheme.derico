/**
 * The snippet corpus and its degradation rule, from the editor side.
 *
 * The rule is two lines — known key renders its file, anything else renders
 * the Balkenlage — but it is a rule BOTH halves state independently
 * (`snippets.ts` and `browser/snippet.py`), so each side pins its own copy;
 * `tests/test_snippet_view.py` additionally holds the corpus and the schema
 * choices in lockstep from the Python side.
 */
import { cleanup, render } from '@testing-library/react';
import { afterEach, describe, expect, test } from 'vitest';

import Snippet from './Snippet';
import SnippetSchema, { SNIPPET_CHOICES } from './schema';
import { DEFAULT_SNIPPET, markup, SNIPPETS } from './snippets';

afterEach(cleanup);

describe('the corpus', () => {
  test('one choice per snippet, in the same vocabulary', () => {
    expect(SNIPPET_CHOICES.map(([value]) => value).sort()).toEqual(
      Object.keys(SNIPPETS).sort(),
    );
    expect(SnippetSchema.properties.snippet.choices).toBe(SNIPPET_CHOICES);
    expect(SnippetSchema.properties.snippet.default).toBe(DEFAULT_SNIPPET);
  });

  test('every fragment is decorative and carries its own root class', () => {
    for (const [name, html] of Object.entries(SNIPPETS)) {
      expect(html, name).toContain('aria-hidden="true"');
      // The fragment must bring the class its stylesheet section targets;
      // nothing styles the injection wrapper.
      const root = name === 'balkenlage' ? 'balkenlage' : 'derico-staenderwerk';
      expect(html, name).toMatch(new RegExp(`^<div class="${root}"`));
    }
  });

  test('no animation hooks survive extraction', () => {
    // `data-balkenlage` / `data-service-frame` are the mockup's site.js
    // arming hooks; the Plone pages ship no snippet JS, and a hook with no
    // script is a claim the markup cannot keep.
    for (const [name, html] of Object.entries(SNIPPETS)) {
      expect(html, name).not.toMatch(/data-(balkenlage|service-frame)/);
    }
  });
});

describe('markup()', () => {
  test('a stored key renders its own fragment', () => {
    expect(markup({ snippet: 'service-frame' })).toBe(
      SNIPPETS['service-frame'],
    );
  });

  test.each([
    ['a fresh unseeded node', {}],
    ['an unknown key written through the API', { snippet: 'zapfen' }],
  ])('%s falls back to the Balkenlage', (_label, data) => {
    expect(markup(data as any)).toBe(SNIPPETS[DEFAULT_SNIPPET]);
  });
});

describe('<Snippet />', () => {
  test('injects the fragment verbatim inside the parity wrapper', () => {
    const { container } = render(<Snippet data={{ snippet: 'balkenlage' }} />);
    const wrapper = container.querySelector('.derico-snippet');
    // Reading innerHTML back re-serialises the fragment (`<circle/>` comes
    // out as `<circle></circle>`), so "verbatim" is asserted as DOM
    // equivalence: the same string parsed outside React must serialise
    // identically.
    const reference = document.createElement('div');
    reference.innerHTML = SNIPPETS['balkenlage'];
    expect(wrapper?.innerHTML).toBe(reference.innerHTML);
    expect(
      wrapper?.querySelectorAll('.balkenlage__balken'),
    ).toHaveLength(8);
  });
});
