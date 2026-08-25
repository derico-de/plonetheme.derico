/**
 * The host's promised module surface, and the guard that keeps it out of the
 * bundle (block add-on contract §2.1, hero ticket 04 §6).
 *
 * Every specifier below is served to the browser as an import-map facade by
 * `@@aurora-edit`, so the bundle must import it rather than contain it. A
 * promised singleton compiled *into* a block bundle is a second copy at
 * runtime: two Reacts, a null hook dispatcher, and a block that throws the
 * moment it renders inside Plate.
 *
 * The whole list is externalized, not just the modules this block happens to
 * import today. Externalizing an unimported module costs nothing; a partial
 * list is a landmine for the next brand block that adds an import.
 */
import type { Plugin } from 'vite';

export const PROMISED_MODULES = [
  'react',
  'react/jsx-runtime',
  'react-dom',
  'react-dom/client',
  'jotai',
  'platejs',
  '@plone/registry',
  '@plone/helpers',
] as const;

/**
 * Fail the build if a chunk imports anything that is neither relative nor
 * promised.
 *
 * An ALLOW-list, deliberately: a deny-list of the eight names above would
 * pass `platejs/react` or a transitive dependency that reaches React under
 * some other specifier, and either of those is the duplicate-instance bug the
 * externals exist to prevent. Anything genuinely new here is a decision — add
 * it to the list on purpose, or bundle it.
 */
export function promisedExternalsOnly(): Plugin {
  const allowed = new Set<string>(PROMISED_MODULES);
  return {
    name: 'derico:promised-externals-only',
    apply: 'build',
    generateBundle(_outputOptions, bundle) {
      const offenders: string[] = [];
      for (const [fileName, output] of Object.entries(bundle)) {
        if (output.type !== 'chunk') continue;
        for (const specifier of [...output.imports, ...output.dynamicImports]) {
          if (specifier.startsWith('.') || specifier.startsWith('/')) continue;
          if (allowed.has(specifier)) continue;
          offenders.push(`${fileName} imports ${specifier}`);
        }
      }
      if (offenders.length) {
        this.error(
          'bare imports outside the promised module surface (contract ' +
            `§2.1) — bundle them or promise them:\n  ${offenders.join('\n  ')}`,
        );
      }
    },
  };
}
