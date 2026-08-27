/**
 * The snippet corpus, imported `?raw` from the Python package's own
 * `snippets/` directory — the same files `browser/snippet.py` reads at render
 * time. Neither half owns a copy, so the canvas and the published page cannot
 * drift: there is exactly one Balkenlage and exactly one Ständerwerk, and
 * both surfaces inject it verbatim.
 *
 * Adding a snippet is: one file in `snippets/`, one import and map entry
 * here, one choice in `schema.ts`. `tests/test_snippet_view.py` holds the
 * file list and the choice list in lockstep from the Python side.
 */
import balkenlage from '../../../src/plonetheme/derico/snippets/balkenlage.html?raw';
import serviceFrame from '../../../src/plonetheme/derico/snippets/service-frame.html?raw';

export const SNIPPETS: Record<string, string> = {
  balkenlage,
  'service-frame': serviceFrame,
};

export const DEFAULT_SNIPPET = 'balkenlage';

export type SnippetData = {
  snippet?: string;
};

/**
 * The markup for a node's stored key. The value is untrusted in exactly the
 * way the server view's is — the block is authorable through the API — and is
 * only ever a lookup key: unknown or absent falls back to the Balkenlage,
 * mirroring `DericoSnippetView.markup`.
 */
export function markup(data: SnippetData): string {
  const key = data?.snippet ?? '';
  return SNIPPETS[key] ?? SNIPPETS[DEFAULT_SNIPPET];
}
