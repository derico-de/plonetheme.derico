// @vitest-environment node
/**
 * `static/derico.min.css` is committed build output, so nothing but this
 * test notices a source edit that was never rebuilt.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

import { buildThemeSheet, STATIC, THEME_SHEET } from './theme-sheet.ts';

const read = (name: string) => readFileSync(path.join(STATIC, name), 'utf8');
const count = (text: string, pattern: RegExp) => text.match(pattern)?.length ?? 0;

describe('the theme sheet', async () => {
  const built = await buildThemeSheet();

  it('is committed as built from its sources', () => {
    const stale = 'static/derico.min.css is stale: run `pnpm build`';
    expect(read(THEME_SHEET) === built.css, stale).toBe(true);
    expect(read(`${THEME_SHEET}.map`) === built.map, stale).toBe(true);
  });

  it("keeps the snippets' scope and its limit", () => {
    expect(built.css).toMatch(
      /@scope\s*\(\.aurora-editor,\s*\.aurora-editor-portal,\s*\.aurora-blocks-view\)\s*to\s*\(\.aurora-pattern-island\)\s*\{/,
    );
  });

  it("keeps every container query of the header's layout container", () => {
    const query = /@container derico-page /g;
    expect(count(built.css, query)).toBe(count(read('header.css'), query));
  });
});
