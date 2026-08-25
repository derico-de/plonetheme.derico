/**
 * The registration contract (hero ticket 08, contract §1.3/§1.4).
 *
 * `install()` runs once per registration record, before `mount()`, and the
 * loader THROWS if it does not hand the config object back (`main.tsx:96`) —
 * a failure that costs the whole editor, not just this block. None of it is
 * exercised by rendering a hero, so it is pinned here.
 *
 * The `defaultBlockWidth` / `blockSchema` interlock is the subtle one: the two
 * are a single decision expressed in two files, and either one drifting alone
 * silently returns the width control to the author (ticket 11).
 */
import { describe, expect, test } from 'vitest';

import installDericoHero, { HERO_BLOCK_TYPE } from './index';

type TestConfig = {
  blocks: { blocksConfig: Record<string, any> };
  registerWidget?: (registration: {
    key: string;
    definition: Record<string, unknown>;
  }) => void;
};

const makeConfig = (): TestConfig => ({ blocks: { blocksConfig: {} } });

const install = (config: TestConfig) =>
  installDericoHero(config as any) as unknown as TestConfig;

describe('install()', () => {
  test('hands back the very object it was given', () => {
    const config = makeConfig();
    // Identity, not equality: the loader passes the result on as THE config.
    expect(install(config)).toBe(config);
  });

  test('registers the block under its own @type', () => {
    const { blocks } = install(makeConfig());
    expect(Object.keys(blocks.blocksConfig)).toEqual([HERO_BLOCK_TYPE]);
    expect(HERO_BLOCK_TYPE).toBe('derico-hero');
  });

  test('supplies every key the blocksConfig entry owes', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[HERO_BLOCK_TYPE];
    for (const key of ['id', 'title', 'icon', 'edit', 'view', 'blockSchema']) {
      expect(entry[key], `blocksConfig.${key}`).toBeTruthy();
    }
    expect(entry.id).toBe(HERO_BLOCK_TYPE);
    // Both halves, per the charting constraint: a block with only an `edit`
    // renders blank the moment the page is viewed rather than edited.
    expect(typeof entry.edit).toBe('function');
    expect(typeof entry.view).toBe('function');
  });

  test('asks for full bleed, and leaves the schema no way to countermand it', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[HERO_BLOCK_TYPE];
    // Aurora resolves `styleFields.blockWidth ?? defaultBlockWidth` and
    // materialises the result onto the node at insert. A `blockWidth` property
    // in the schema wins, so these two assertions are one contract.
    expect(entry.defaultBlockWidth).toBe('full');
    expect(entry.blockSchema.properties).not.toHaveProperty('blockWidth');
    expect(entry.blockSchema.fieldsets[0].fields).not.toContain('blockWidth');
  });

  test('namespaces its widgets rather than redefining shared vocabulary', () => {
    const registered: Record<string, unknown>[] = [];
    const config = makeConfig();
    config.registerWidget = ({ key, definition }) => {
      expect(key).toBe('widget');
      registered.push(definition);
    };
    install(config);

    const definition = registered[0] ?? {};
    expect(Object.keys(definition).sort()).toEqual([
      'derico_reference',
      'derico_ring_legend',
      'derico_textarea',
    ]);
    // `registerWidget` is a global, last-wins map shared with every other
    // add-on: claiming `textarea` would rewrite it for blocks this theme
    // knows nothing about (ticket 02).
    for (const generic of ['textarea', 'legend', 'reference']) {
      expect(definition).not.toHaveProperty(generic);
    }
  });

  test('still registers the block when the host exposes no widget registry', () => {
    // `registerWidget` is optional in the contract; losing the sidebar
    // widgets must not cost the block itself.
    const config = makeConfig();
    expect(() => install(config)).not.toThrow();
    expect(config.blocks.blocksConfig[HERO_BLOCK_TYPE]).toBeTruthy();
  });
});
