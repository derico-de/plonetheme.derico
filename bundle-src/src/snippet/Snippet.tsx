/**
 * The one rendering both halves share: the stored key's fragment, injected
 * verbatim. `dangerouslySetInnerHTML` is safe by construction here — the
 * markup never comes from the node, only the LOOKUP KEY does, and the corpus
 * is the package's own `snippets/*.html` (see snippets.ts).
 */
import { markup } from './snippets';
import type { SnippetData } from './snippets';

export function Snippet({ data }: { data: SnippetData }) {
  return (
    <div
      className="derico-snippet"
      dangerouslySetInnerHTML={{ __html: markup(data) }}
    />
  );
}

export default Snippet;
