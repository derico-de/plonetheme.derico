/**
 * The fragment provider's registration contract, and its lockstep with the
 * corpus on disk.
 *
 * Nothing here asserts how a fragment looks — the markup is the design
 * mockup's, and `static/snippets.css` is what restates the mockup's rules.
 * What is pinned is that the map this entry publishes is exactly the
 * directory the server reads: an id with no file renders on the canvas and
 * vanishes when published, and a file no entry publishes is an ornament
 * nobody can place. `tests/test_fragments.py` pins the same seam from the
 * server's side.
 */
import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, test } from 'vitest';

import installDericoFragments, {
  DERICO_FRAGMENTS,
  FRAGMENT_UTILITY_TYPE,
} from './index';

const CORPUS_DIR = path.resolve(
  import.meta.dirname,
  '../../../src/plonetheme/derico/snippets',
);

const corpusFiles = () =>
  readdirSync(CORPUS_DIR).filter((name) => name.endsWith('.html'));

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

describe('the published map', () => {
  test('publishes every shipped ornament, and only those', () => {
    expect(DERICO_FRAGMENTS.map((f) => `${f.id}.html`).sort()).toEqual(
      corpusFiles().sort(),
    );
  });

  test('carries each file verbatim', () => {
    for (const fragment of DERICO_FRAGMENTS) {
      const onDisk = readFileSync(
        path.join(CORPUS_DIR, `${fragment.id}.html`),
        'utf8',
      );
      expect(fragment.html, fragment.id).toBe(onDisk);
    }
  });

  test('titles every ornament', () => {
    for (const fragment of DERICO_FRAGMENTS) {
      expect(fragment.title.trim(), fragment.id).toBeTruthy();
    }
  });

  test('uses ids the server can resolve to a file', () => {
    // collective.fragmentsblock resolves `<id>.html` inside the provider's
    // directory and refuses anything else.
    for (const fragment of DERICO_FRAGMENTS) {
      expect(fragment.id, fragment.id).toMatch(/^[A-Za-z0-9][A-Za-z0-9_-]*$/);
    }
  });
});
