/**
 * The registration contract, pinned the same way the hero's is: none of this
 * is exercised by rendering a snippet, and every failure mode is a fail-soft
 * skip that costs the block its slash-menu entry silently.
 */
import { describe, expect, test } from 'vitest';

import installDericoSnippet, { SNIPPET_BLOCK_TYPE } from './index';

type TestConfig = {
  blocks: { blocksConfig: Record<string, any> };
  registerWidget?: (registration: unknown) => void;
};

const makeConfig = (): TestConfig => ({ blocks: { blocksConfig: {} } });

const install = (config: TestConfig) =>
  installDericoSnippet(config as any) as unknown as TestConfig;

describe('install()', () => {
  test('hands back the very object it was given', () => {
    const config = makeConfig();
    expect(install(config)).toBe(config);
  });

  test('registers the block under its own @type', () => {
    const { blocks } = install(makeConfig());
    expect(Object.keys(blocks.blocksConfig)).toEqual([SNIPPET_BLOCK_TYPE]);
    expect(SNIPPET_BLOCK_TYPE).toBe('derico-snippet');
  });

  test('supplies every key the blocksConfig entry owes', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[SNIPPET_BLOCK_TYPE];
    for (const key of ['id', 'title', 'icon', 'edit', 'view', 'blockSchema']) {
      expect(entry[key], `blocksConfig.${key}`).toBeTruthy();
    }
    expect(entry.id).toBe(SNIPPET_BLOCK_TYPE);
    expect(typeof entry.edit).toBe('function');
    expect(typeof entry.view).toBe('function');
  });

  test('asks for layout width, and leaves the schema no way to countermand it', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[SNIPPET_BLOCK_TYPE];
    // Same interlock the hero pins: a `blockWidth` schema property wins over
    // `defaultBlockWidth`, so these two assertions are one contract.
    expect(entry.defaultBlockWidth).toBe('layout');
    expect(entry.blockSchema.properties).not.toHaveProperty('blockWidth');
    expect(entry.blockSchema.fieldsets[0].fields).not.toContain('blockWidth');
  });

  test('registers no widgets', () => {
    // One `choices` field is vocabulary the wrapper already provides; a call
    // here would be this block claiming shared registry territory it has no
    // business in.
    const registered: unknown[] = [];
    const config = makeConfig();
    config.registerWidget = (registration) => registered.push(registration);
    install(config);
    expect(registered).toEqual([]);
  });
});
