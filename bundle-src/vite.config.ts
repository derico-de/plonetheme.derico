/**
 * The brand blocks' editor bundles (block add-on contract §1.2, hero ticket
 * 04).
 *
 * One workspace, N entry points, N bundles, N records. Two members today:
 * `hero`, and `snippet` — whose entry is exactly the one line the map was
 * laid out for. Note the shared-stylesheet caveat below only concerns entries
 * that IMPORT css; `snippet` imports none (its styling is the theme's
 * `static/snippets.css`), so `blocks.css` remains the hero's alone.
 *
 * Output goes to `src/plonetheme/derico/static-blocks/`, a second static
 * directory registered as `++plone++plonetheme.derico.blocks` and reserved
 * ENTIRELY for build output — `emptyOutDir` wipes it on every build, so a
 * hand-written file placed there is deleted without warning (04 §3).
 */
import path from 'node:path';
import { defineConfig } from 'vite';

import { scopeWrap } from './build-plugins/scope-wrap.ts';
import {
  PROMISED_MODULES,
  promisedExternalsOnly,
} from './build-plugins/promised-externals.ts';

const here = import.meta.dirname;

export default defineConfig({
  // Lib mode defaults to the classic transform, which needs a global React
  // and crashes at render time without one. The contract mandates the
  // automatic runtime, resolved through the page import map.
  esbuild: { jsx: 'automatic' },
  plugins: [
    // `enforce: 'post'`, added here rather than in the vendored plugin: in
    // LIB mode Vite emits the single `cssFileName` asset from `vite:css-post`,
    // which runs after an unenforced plugin's `generateBundle` — so the sheet
    // shipped unwrapped and every token silently died against Aurora's scoped
    // preflight. The wrapper never hit this because its CSS arrives as
    // code-split chunks. The plugin CODE stays byte-identical to upstream.
    {
      ...scopeWrap({
        // Three roots, where the wrapper passes two. The wrapper styles the
        // editor; a block's sheet must also style the public page, which is
        // `.aurora-blocks-view`.
        scopeRoots: [
          '.aurora-editor',
          '.aurora-editor-portal',
          '.aurora-blocks-view',
        ],
        scopeLimit: '.aurora-pattern-island',
      }),
      enforce: 'post' as const,
    },
    promisedExternalsOnly(),
  ],
  build: {
    lib: {
      entry: {
        hero: path.resolve(here, 'src/hero/index.tsx'),
        snippet: path.resolve(here, 'src/snippet/index.tsx'),
        // Not a block: it registers the snippet corpus as fragments for
        // collective.fragmentsblock's generic block. Its own entry and its
        // own record for the same reason `snippet` has one — install() runs
        // once per record, so sharing a bundle would break the per-record
        // `enabled` switch.
        fragments: path.resolve(here, 'src/fragments/index.tsx'),
      },
      formats: ['es'],
      fileName: (_format, entryName) => `${entryName}.js`,
      // Lib mode emits ONE stylesheet per build, not per entry, so every
      // block record points its `css` field at this same asset (04 §5).
      cssFileName: 'blocks',
    },
    outDir: path.resolve(here, '../src/plonetheme/derico/static-blocks'),
    // Explicit, because the outDir is outside the project root and Vite
    // otherwise refuses to empty it. Committed artifacts plus hashed chunk
    // names plus `false` would accumulate orphans that `git diff
    // --exit-code` cannot see.
    emptyOutDir: true,
    target: 'es2022',
    minify: false,
    // The delivery story is that an admin with no Node installs this and
    // never builds it; an undebuggable artifact is a real cost.
    sourcemap: true,
    rollupOptions: {
      external: [...PROMISED_MODULES],
      output: {
        // Stable entry names; the webresource uuid on the entry URL does the
        // cache-busting, so a changed chunk hash changes the entry, which
        // changes the uuid (ADR 0010).
        chunkFileNames: 'chunks/[name]-[hash].js',
      },
    },
  },
});
