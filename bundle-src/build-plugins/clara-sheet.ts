/**
 * The Clara sheet: plonetheme.clara's bundle compiled from its Sass sources
 * without the Bootstrap parts derico never uses (`clara-sheet/`), committed as
 * `static/clara.min.css`. The `plonetheme-clara` bundle record loads it in
 * place of Clara's own sheet.
 *
 * Reads Clara's sources from the sibling checkout, where derico's development
 * and CI already keep it.
 */
import { writeFile } from 'node:fs/promises';
import path from 'node:path';
import { compile } from 'sass';
import type { Plugin } from 'vite';

import { STATIC } from './theme-sheet.ts';

export const CLARA_SHEET = 'clara.min.css';
export const ENTRY = path.resolve(import.meta.dirname, '../clara-sheet/clara.scss');
export const CLARA = path.resolve(import.meta.dirname, '../../../plonetheme.clara');
export const CLARA_SCSS = path.join(CLARA, 'theme/scss');

export function buildClaraSheet() {
  return compile(ENTRY, {
    style: 'compressed',
    loadPaths: [CLARA_SCSS, path.resolve(import.meta.dirname, '../node_modules')],
    quietDeps: true,
    silenceDeprecations: ['import'],
  }).css;
}

export function claraSheet(): Plugin {
  return {
    name: 'derico-clara-sheet',
    apply: 'build',
    async closeBundle() {
      await writeFile(path.join(STATIC, CLARA_SHEET), buildClaraSheet());
    },
  };
}
