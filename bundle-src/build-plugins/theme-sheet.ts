/**
 * The theme sheet: the hand-written sheets under `static/`, minified into one
 * committed `derico.min.css` and its map, so a page makes one render-blocking
 * request for the theme instead of one per sheet. The sources stay readable;
 * the map points DevTools back at them.
 */
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { transform } from 'lightningcss';
import type { Plugin } from 'vite';

export const STATIC = path.resolve(
  import.meta.dirname,
  '../../src/plonetheme/derico/static',
);
export const THEME_SHEET = 'derico.min.css';

/** Cascade order: all but snippets.css are unlayered and unscoped. The token
 * layer opens; print closes, so a print rule wins every tie with the screen. */
const SOURCES = [
  'derico.css',
  'snippets.css',
  'header.css',
  'footer.css',
  'print.css',
];

/** Each source minified on its own, and an index map with a section per
 * source: lightningcss's bundler reads in parallel, so its map differs run
 * to run. */
export async function buildThemeSheet() {
  const sheets: string[] = [];
  const sections = [];
  let line = 0;
  for (const name of SOURCES) {
    const { code, map } = transform({
      filename: name,
      code: await readFile(path.join(STATIC, name)),
      minify: true,
      sourceMap: true,
    });
    const sheet = code.toString();
    sheets.push(sheet);
    sections.push({ offset: { line, column: 0 }, map: JSON.parse(String(map)) });
    line += sheet.split('\n').length;
  }
  return {
    css: `${sheets.join('\n')}\n/*# sourceMappingURL=${THEME_SHEET}.map */\n`,
    map: `${JSON.stringify({ version: 3, file: THEME_SHEET, sections })}\n`,
  };
}

export function themeSheet(): Plugin {
  return {
    name: 'derico-theme-sheet',
    apply: 'build',
    async closeBundle() {
      const { css, map } = await buildThemeSheet();
      await writeFile(path.join(STATIC, THEME_SHEET), css);
      await writeFile(path.join(STATIC, `${THEME_SHEET}.map`), map);
    },
  };
}
