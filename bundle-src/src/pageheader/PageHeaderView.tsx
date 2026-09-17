/**
 * The `view` half (contract §1.1).
 *
 * On a Blicca site nothing renders this: the published page is drawn by the
 * server view `@@aurora-block-derico-page-header` from the content's own
 * Title and Description. It is implemented anyway — a brand block that skips
 * `view` renders blank the day the site is served through Aurora proper —
 * and it reads the same form atom the canvas writes, which is the content.
 */
import PageHeader from './PageHeader';
import { useContentField } from './content-fields';
import { text } from './data';
import type { PageHeaderData } from './data';

export function PageHeaderView({ data }: { data: PageHeaderData }) {
  const [title] = useContentField('title');
  const [description] = useContentField('description');
  return (
    <PageHeader kicker={text(data.kicker)} title={text(title)} description={text(description)} />
  );
}

export default PageHeaderView;
