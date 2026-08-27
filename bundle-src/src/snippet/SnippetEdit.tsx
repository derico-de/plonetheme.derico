/**
 * The `edit` half: the canvas preview, plus the one write this block ever
 * makes to its own node.
 *
 * Aurora's slash menu creates a node carrying `@type` and nothing else, and
 * `blocksConfig` has no initial-data hook, so — exactly as `HeroEdit` does —
 * the freshly inserted block seeds itself, here with the schema's own
 * default. Without the seed the renderers would still fall back to the
 * Balkenlage (snippets.ts / snippet.py), but the sidebar select would sit on
 * an unstored value: what the author sees claimed and what the node says
 * would disagree until the first manual change.
 *
 * No nag and no in-canvas editing: the block has no text, and a snippet with
 * its default stored is already finished.
 */
import { useEffect, useRef } from 'react';

import Snippet from './Snippet';
import { DEFAULT_SNIPPET } from './snippets';
import type { SnippetData } from './snippets';

export type SnippetEditProps = {
  data: SnippetData;
  /** The adapter's block id; `onChangeBlock`'s first argument. */
  block?: string;
  selected?: boolean;
  onChangeBlock?: (block: string, data: SnippetData) => void;
};

export function SnippetEdit({ block, data, onChangeBlock }: SnippetEditProps) {
  // In an effect, not in render: seeding writes to the Plate document, and
  // `setNodes` during another component's render is a mid-render store
  // update. The ref stops a host that re-renders before the write lands from
  // queueing a second one.
  const seedWritten = useRef(false);
  const unseeded = data?.snippet === undefined;
  useEffect(() => {
    if (!unseeded || seedWritten.current || !block || !onChangeBlock) return;
    seedWritten.current = true;
    onChangeBlock(block, { ...data, snippet: DEFAULT_SNIPPET });
  }, [unseeded, block, data, onChangeBlock]);

  return <Snippet data={data} />;
}

export default SnippetEdit;
