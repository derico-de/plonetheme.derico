/**
 * The `view` half (contract §1.1).
 *
 * On a Blicca site nothing renders this: the published page is drawn by the
 * server view `@@aurora-block-derico-snippet`, which injects the same file
 * this bundle imported `?raw`. Implemented anyway, and trivially real rather
 * than a stub, for the same reason the hero's is: the contract's
 * single-ecosystem exemption covers publication only.
 */
import Snippet from './Snippet';
import type { SnippetData } from './snippets';

export function SnippetView({ data }: { data: SnippetData }) {
  return <Snippet data={data} />;
}

export default SnippetView;
