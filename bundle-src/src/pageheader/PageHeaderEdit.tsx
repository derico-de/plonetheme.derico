/**
 * The `edit` half: the canvas IS the editing surface.
 *
 * Three inline controls, one per word of the header, each standing where
 * the published page puts that word (`InlineField`). The kicker is the
 * block's own data and goes through `onChangeBlock`; the title and the
 * description are the page's fields and go through the host's form atom
 * (`content-fields.ts`, contract §1.7) — the same pair Aurora's title node
 * writes, so the two never disagree.
 *
 * Every slot is always rendered here, empty or not: a slot the author
 * cannot see cannot be typed into. The public view omits what is empty.
 */
import InlineField from './InlineField';
import PageHeader from './PageHeader';
import { useContentField } from './content-fields';
import { raw } from './data';
import type { PageHeaderData } from './data';

export type PageHeaderEditProps = {
  data: PageHeaderData;
  /** The adapter's block id; `onChangeBlock`'s first argument. */
  block?: string;
  selected?: boolean;
  onChangeBlock?: (block: string, data: PageHeaderData) => void;
};

export function PageHeaderEdit({ block, data, onChangeBlock }: PageHeaderEditProps) {
  const [title, setTitle] = useContentField('title');
  const [description, setDescription] = useContentField('description');
  const setKicker = (kicker: string) => onChangeBlock?.(block ?? '', { ...data, kicker });

  return (
    <PageHeader
      kicker={<InlineField value={raw(data.kicker)} onChange={setKicker} label="Kicker" />}
      title={<InlineField value={title} onChange={setTitle} label="Title" line />}
      description={<InlineField value={description} onChange={setDescription} label="Description" />}
    />
  );
}

export default PageHeaderEdit;
