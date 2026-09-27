/**
 * The Derico Page Header's bundle entry point.
 *
 * The default export is the install function the wrapper calls once per
 * registration record, before `mount()` (contract §1.3). It MUST return the
 * config object — the loader throws otherwise.
 *
 * Its own bundle, like the hero: a shared bundle would defeat the per-record
 * `enabled` kill switch.
 */
import './pageheader.css';

import PageHeaderEdit from './PageHeaderEdit';
import PageHeaderIcon from './PageHeaderIcon';
import PageHeaderView from './PageHeaderView';
import PageHeaderSchema, { PAGE_HEADER_BLOCK_TYPE } from './schema';

type BlocksConfig = {
  blocks: { blocksConfig: Record<string, unknown> };
};

export default function installDericoPageHeader<T extends BlocksConfig>(config: T): T {
  config.blocks.blocksConfig[PAGE_HEADER_BLOCK_TYPE] = {
    id: PAGE_HEADER_BLOCK_TYPE,
    title: 'Derico Page Header',
    icon: PageHeaderIcon,
    edit: PageHeaderEdit,
    view: PageHeaderView,
    blockSchema: PageHeaderSchema,
    // The page's opening, whole: this block prints the title and the
    // description itself (contract §1.8), so a new page opens with it in
    // place of the tree's title and description nodes, and a tree that
    // holds it drops the pair — the page would open twice otherwise.
    documentHeader: true,
    // The page title stands on the layout edge. Aurora materialises this onto
    // the node; works only while `blockSchema` declares no `blockWidth`
    // (contract §1.4).
    defaultBlockWidth: 'layout',
  };
  return config;
}

export { PAGE_HEADER_BLOCK_TYPE };
