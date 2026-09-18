/**
 * The Derico Page Header's bundle entry point.
 *
 * The default export is the install function the wrapper calls once per
 * registration record, before `mount()` (contract §1.3). It MUST return the
 * config object — the loader throws otherwise.
 *
 * Its own bundle and its own record, like the hero: `loadBlockAddons` calls
 * `install(config)` per RECORD with no dedupe, so a shared bundle would
 * quietly kill the per-block `enabled` kill switch (hero ticket 04 §1).
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
    // The layout rung: the page's title stands on the layout edge (derico
    // grid alignment, derico.css §10), and so does this header. Aurora
    // MATERIALISES the resolved width onto the node at insert, so the server
    // reads an explicit `"layout"`. It works only while `blockSchema`
    // declares no `blockWidth` — a schema style field wins (contract §1.4).
    defaultBlockWidth: 'layout',
  };
  return config;
}

export { PAGE_HEADER_BLOCK_TYPE };
