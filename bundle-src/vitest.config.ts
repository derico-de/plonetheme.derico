/**
 * Unit tests for the editor half.
 *
 * The public view's degradation rules are tested from pytest; these pin the
 * canvas side of the same table.
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
