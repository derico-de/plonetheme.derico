/**
 * Unit tests for the editor half.
 *
 * The block's degradation table (hero ticket 02) is a seven-case contract
 * both halves have to honour identically, and the public view is tested from
 * pytest — so the canvas side needs a runner of its own or those cases go
 * unchecked until someone clicks through the editor. Hero ticket 04 §11 ruled
 * out a linter for a ~500-line workspace; a test runner is the opposite
 * trade, and it never reaches the shipped bundle.
 *
 * Note the promised modules are NOT external here: the bundle resolves them
 * through the page import map at runtime, while these tests resolve them from
 * node_modules like any other consumer.
 */
import { defineConfig } from 'vitest/config';

export default defineConfig({
  esbuild: { jsx: 'automatic' },
  // The ornament corpus lives in the PYTHON package (`src/plonetheme/derico/
  // snippets/*.html`, imported `?raw`) — one directory up from this
  // workspace, which Vite's file server denies by default. The build never
  // asks (Rollup reads files directly); only the test server needs the door.
  server: { fs: { allow: ['..'] } },
  test: {
    environment: 'jsdom',
    globals: false,
    include: ['src/**/*.test.tsx', 'src/**/*.test.ts'],
    css: false,
  },
});
