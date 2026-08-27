/**
 * The fragment provider's registration contract, and the lockstep that
 * pays for restating the corpus in a second entry.
 *
 * Nothing here asserts how a fragment looks — the markup is the design
 * mockup's, pinned on the Snippet block's side by `snippets.test.tsx` and
 * on the server's by `tests/test_fragments.py`. What is pinned here is
 * that both entries publish the SAME corpus under the SAME ids and titles,
 * because the build forbids them sharing a module (see index.tsx).
 */
import { describe, expect, test } from 'vitest';

import installDericoFragments, {
  DERICO_FRAGMENTS,
  FRAGMENT_UTILITY_TYPE,
} from './index';
import { SNIPPETS } from '../snippet/snippets';
import { SNIPPET_CHOICES } from '../snippet/schema';

type Registration = { type: string; name: string; method: unknown };

const makeConfig = () => {
  const registered: Registration[] = [];
  return {
    registered,
    registerUtility: (registration: Registration) =>
      registered.push(registration),
  };
};

describe('install()', () => {
  test('hands back the very object it was given', () => {
    const config = makeConfig();
    expect(installDericoFragments(config)).toBe(config);
  });

  test('registers one utility per fragment, keyed by its id', () => {
    const { registered } = installDericoFragments(makeConfig());
    expect(registered.map((r) => r.name)).toEqual(
      DERICO_FRAGMENTS.map((f) => f.id),
    );
    for (const registration of registered) {
      expect(registration.type).toBe(FRAGMENT_UTILITY_TYPE);
      // the add-on enumerates records without their registration names, so
      // the record has to carry its own id — and the two must agree
      expect((registration.method as { id: string }).id).toBe(
        registration.name,
      );
    }
  });

  test('registers no blocks', () => {
    // The record declares no `types` for exactly this reason: the bundle
    // extends the generic fragment block's corpus, it does not add a block.
    const config = makeConfig() as Record<string, unknown>;
    config.blocks = { blocksConfig: {} };
    installDericoFragments(config as never);
    expect((config.blocks as { blocksConfig: object }).blocksConfig).toEqual(
      {},
    );
  });
});

describe('the corpus, restated', () => {
  test('is the Snippet block\'s corpus, id for id and title for title', () => {
    expect(DERICO_FRAGMENTS.map((f) => [f.id, f.title])).toEqual(
      SNIPPET_CHOICES,
    );
  });

  test('carries the same markup the Snippet block renders', () => {
    for (const fragment of DERICO_FRAGMENTS) {
      expect(fragment.html, fragment.id).toBe(SNIPPETS[fragment.id]);
    }
  });

  test('uses ids the server can resolve to a file', () => {
    // collective.fragmentsblock resolves `<id>.html` inside the provider's
    // directory and refuses anything else; an id that fails here would
    // render on the canvas and vanish on the published page.
    for (const fragment of DERICO_FRAGMENTS) {
      expect(fragment.id, fragment.id).toMatch(/^[A-Za-z0-9][A-Za-z0-9_-]*$/);
    }
  });
});
