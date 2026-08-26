/**
 * The `edit` half: the canvas is a live preview, never an editing surface.
 *
 * Every field is edited in the sidebar (ticket 02). The block is a Plate VOID
 * node, so in-canvas text would mean re-solving focus, undo and selection
 * inside a void — a large bespoke cost, in a block whose whole premise is
 * that the author gets no choices to make.
 *
 * That decision is what makes two of the sheet's rules safe: the hero states
 * `white-space: normal`, overriding the `pre-wrap` the Plate editable
 * computes and inherits into everything it contains (ticket 07 measured the
 * canvas breaking the headline where the view kept it whole). Nothing here is
 * contenteditable, so nothing is lost by normalising it.
 *
 * The canvas is also where a fresh insert gets its words. Aurora writes a
 * node carrying `@type` and nothing else, and `blocksConfig` has no
 * initial-data hook, so this component is the first — and only — place the
 * block sees its own node in time to seed it (`defaults.ts`).
 *
 * The other thing the canvas adds to the public rendering is the nag: a
 * half-authored hero saves and previews happily — nothing in the schema is
 * required — so the editor is where the author is told what is still missing.
 * The hint is `contentEditable={false}` and outside the hero's own root, so
 * it can neither be typed into nor styled by the block's palette.
 */
import { useEffect, useRef } from 'react';

import Hero from './Hero';
import HeroMedia from './HeroMedia';
import { legend, link, reference, text } from './data';
import type { HeroData } from './data';
import { seeded, unseeded } from './defaults';

export type HeroEditProps = {
  data: HeroData;
  /** The adapter's block id; `onChangeBlock`'s first argument, unread here. */
  block?: string;
  selected?: boolean;
  onChangeBlock?: (block: string, data: HeroData) => void;
};

/** What a reader of the finished page would notice was missing. */
export function missing(data: HeroData): string[] {
  const gaps: string[] = [];
  if (!text(data.headline)) gaps.push('headline');
  if (!text(data.lede)) gaps.push('lede');
  if (!link(data.cta_label, data.cta_href)) gaps.push('primary call to action');
  if (!reference(data.image_wide)) gaps.push('wide image');
  if (legend(data.legend).every((entry) => !entry.title && !entry.subtitle)) {
    gaps.push('ring legend');
  }
  return gaps;
}

export function HeroEdit({ block, data, onChangeBlock }: HeroEditProps) {
  // In an effect, not in render: seeding writes to the Plate document, and
  // `setNodes` during another component's render is a mid-render store
  // update. Once per mounted block — the ref is what stops a host that
  // re-renders before the write lands from queueing a second one.
  const seedWritten = useRef(false);
  useEffect(() => {
    if (seedWritten.current || !onChangeBlock || !unseeded(data)) return;
    seedWritten.current = true;
    onChangeBlock(block ?? '', seeded(data));
  }, [block, data, onChangeBlock]);

  const gaps = missing(data);
  return (
    <>
      <Hero data={data} media={<HeroMedia data={data} />} />
      {gaps.length ? (
        <p className="derico-hero-incomplete" contentEditable={false}>
          Still to fill in: {gaps.join(', ')}.
        </p>
      ) : null}
    </>
  );
}

export default HeroEdit;
