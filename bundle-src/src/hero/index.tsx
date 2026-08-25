/**
 * The Derico Hero's bundle entry point.
 *
 * The default export is the install function the wrapper calls once per
 * registration record, before `mount()` (contract §1.3). It MUST return the
 * config object — the loader throws otherwise.
 *
 * One record, one bundle, one `install()`: a shared bundle registering every
 * derico block would quietly kill the per-block `enabled` kill switch, since
 * `loadBlockAddons` calls `install(config)` per RECORD with no dedupe and the
 * first record's install would re-register the block a second record had
 * disabled (ticket 04 §1).
 */
import './hero.css';

import HeroEdit from './HeroEdit';
import HeroIcon from './HeroIcon';
import HeroView from './HeroView';
import HeroSchema, { HERO_BLOCK_TYPE } from './schema';
import DericoReferenceWidget from './widgets/ReferenceWidget';
import DericoRingLegendWidget from './widgets/RingLegendWidget';
import DericoTextareaWidget from './widgets/TextareaWidget';

type WidgetRegistry = {
  registerWidget: (registration: {
    key: string;
    definition: Record<string, unknown>;
  }) => void;
};

type BlocksConfig = {
  blocks: { blocksConfig: Record<string, unknown> };
};

export default function installDericoHero<T extends BlocksConfig>(
  config: T,
): T {
  const registry = config as unknown as Partial<WidgetRegistry>;
  // Namespaced keys, never the generic `textarea` / `legend` / `reference`:
  // this map is global and last-wins, and a theme must not redefine
  // vocabulary for blocks it knows nothing about (ticket 02).
  registry.registerWidget?.({
    key: 'widget',
    definition: {
      derico_textarea: DericoTextareaWidget,
      derico_ring_legend: DericoRingLegendWidget,
      derico_reference: DericoReferenceWidget,
    },
  });

  config.blocks.blocksConfig[HERO_BLOCK_TYPE] = {
    id: HERO_BLOCK_TYPE,
    title: 'Derico Hero',
    icon: HeroIcon,
    edit: HeroEdit,
    view: HeroView,
    blockSchema: HeroSchema,
    // The whole of the full-bleed wiring (ticket 11, contract §1.4). Aurora
    // resolves the width as `styleFields.blockWidth ?? defaultBlockWidth` and
    // MATERIALISES the result onto the node at insert, so the server reads an
    // explicit `"full"` and needs no per-@type default of its own. It works
    // only while `blockSchema` declares no `blockWidth` — a schema style
    // field wins, and declaring both hands the author back the control this
    // block exists to withhold.
    defaultBlockWidth: 'full',
  };

  return config;
}

export { HERO_BLOCK_TYPE };
