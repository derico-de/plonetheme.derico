/**
 * The registration contract (contract §1.3/§1.4), the hero's pinned again
 * for the second block: `install()` runs once per record and the loader
 * THROWS if it does not hand the config object back.
 */
import { describe, expect, test } from 'vitest';

import installDericoPageHeader, { PAGE_HEADER_BLOCK_TYPE } from './index';

type TestConfig = { blocks: { blocksConfig: Record<string, any> } };

const makeConfig = (): TestConfig => ({ blocks: { blocksConfig: {} } });

const install = (config: TestConfig) =>
  installDericoPageHeader(config as any) as unknown as TestConfig;

const fieldsetFields = (schema: any): string[] =>
  schema.fieldsets.flatMap((fieldset: any) => fieldset.fields);

describe('install()', () => {
  test('hands back the very object it was given', () => {
    const config = makeConfig();
    expect(install(config)).toBe(config);
  });

  test('registers the block under its own @type', () => {
    const { blocks } = install(makeConfig());
    expect(Object.keys(blocks.blocksConfig)).toEqual([PAGE_HEADER_BLOCK_TYPE]);
    expect(PAGE_HEADER_BLOCK_TYPE).toBe('derico-page-header');
  });

  test('supplies every key the blocksConfig entry owes', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE];
    for (const key of ['id', 'title', 'icon', 'edit', 'view', 'blockSchema']) {
      expect(entry[key], `blocksConfig.${key}`).toBeTruthy();
    }
    expect(entry.id).toBe(PAGE_HEADER_BLOCK_TYPE);
    expect(typeof entry.edit).toBe('function');
    expect(typeof entry.view).toBe('function');
  });

  test('asks for the layout rung, and leaves the schema no way to countermand it', () => {
    const entry = install(makeConfig()).blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE];
    expect(entry.defaultBlockWidth).toBe('layout');
    expect(entry.blockSchema.properties).not.toHaveProperty('blockWidth');
    expect(fieldsetFields(entry.blockSchema)).not.toContain('blockWidth');
  });

  test('declares itself the document header', () => {
    // The host seeds a new page with it instead of the title and
    // description nodes, and drops the pair from a tree that holds it
    // (contract §1.8): the header prints both, bound to the same fields.
    const entry = install(makeConfig()).blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE];
    expect(entry.documentHeader).toBe(true);
  });

  test('stores the kicker and nothing else', () => {
    // The title and the description are the page's fields, bound on the
    // canvas; a schema copy would be a second control for the same value.
    const schema = install(makeConfig()).blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE].blockSchema;
    expect(Object.keys(schema.properties)).toEqual(['kicker']);
    expect(fieldsetFields(schema)).toEqual(['kicker']);
    expect(schema.fieldsets[0].id).toBe('default');
    expect(schema.required).toEqual([]);
  });
});
