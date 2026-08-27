/**
 * The Derico Snippet's bundle entry point.
 *
 * Same registration contract as the hero's (contract §1.3): the default
 * export is the install function, called once per registration record, and it
 * MUST return the config object. Its own bundle and its own record rather
 * than a line in the hero's install, because `loadBlockAddons` calls
 * `install(config)` per RECORD with no dedupe — a shared bundle would kill
 * the per-block `enabled` kill switch (hero ticket 04 §1).
 *
 * Two things the hero's entry does that this one deliberately does not:
 *
 * - **No CSS import.** The snippets are styled by the theme's own
 *   `static/snippets.css` bundle, hand-scope-wrapped; this bundle ships only
 *   markup and registration, so the build's shared `blocks.css` stays the
 *   hero's alone and the record declares no `css`.
 * - **No widget registrations.** One `choices` field is vocabulary the
 *   wrapper already provides.
 */
import SnippetEdit from './SnippetEdit';
import SnippetIcon from './SnippetIcon';
import SnippetView from './SnippetView';
import SnippetSchema, { SNIPPET_BLOCK_TYPE } from './schema';

type BlocksConfig = {
  blocks: { blocksConfig: Record<string, unknown> };
};

export default function installDericoSnippet<T extends BlocksConfig>(
  config: T,
): T {
  config.blocks.blocksConfig[SNIPPET_BLOCK_TYPE] = {
    id: SNIPPET_BLOCK_TYPE,
    title: 'Derico Snippet',
    icon: SnippetIcon,
    edit: SnippetEdit,
    view: SnippetView,
    blockSchema: SnippetSchema,
    // The shell width both ornaments sit at in the mockup (they live inside
    // `.shell` there, never bled to the viewport). Materialised onto the node
    // at insert; works only while `blockSchema` declares no `blockWidth` —
    // the same interlock the hero pins (contract §1.4).
    defaultBlockWidth: 'layout',
  };

  return config;
}

export { SNIPPET_BLOCK_TYPE };
