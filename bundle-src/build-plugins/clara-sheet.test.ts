// @vitest-environment node
/**
 * `static/clara.min.css` is committed build output from Clara's sources, so
 * these tests also notice when Clara moves on without derico.
 */
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

import { buildClaraSheet, CLARA, CLARA_SCSS, CLARA_SHEET, ENTRY } from './clara-sheet.ts';
import { STATIC } from './theme-sheet.ts';

const imports = (file: string) =>
  [...readFileSync(file, 'utf8').matchAll(/^@import "([^"]+)";/gm)].map((match) => match[1]);
const bootstrapPin = (file: string) => {
  const { dependencies, devDependencies } = JSON.parse(readFileSync(file, 'utf8'));
  return { ...dependencies, ...devDependencies }.bootstrap;
};

describe('the Clara sheet', () => {
  const built = buildClaraSheet();

  it('is committed as built from its sources', () => {
    const committed = readFileSync(path.join(STATIC, CLARA_SHEET), 'utf8');
    expect(committed === built, 'static/clara.min.css is stale: run `pnpm build`').toBe(true);
  });

  it("imports Clara's partials in Clara's order, with its own Bootstrap layer", () => {
    const clara = imports(path.join(CLARA_SCSS, 'clara.scss'));
    const derico = imports(ENTRY);
    expect(derico).toEqual(clara.map((name) => (name === 'clara-bootstrap' ? 'derico-bootstrap' : name)));
  });

  it('compiles the Bootstrap release Clara pins', () => {
    expect(bootstrapPin(path.resolve(import.meta.dirname, '../package.json'))).toBe(
      bootstrapPin(path.join(CLARA, 'package.json')),
    );
  });

  it("keeps Clara's spacing remap for third-party utilities", () => {
    expect(built).toContain('.mb-3{margin-bottom:var(--plone-space-s) !important}');
  });

  it('carries no dark mode', () => {
    expect(built).not.toMatch(/prefers-color-scheme/);
    expect(built).not.toMatch(/:root[^{]*\[data-bs-theme=dark\]|^\[data-bs-theme=dark\]/m);
  });
});
