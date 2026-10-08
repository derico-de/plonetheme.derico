/**
 * The Derico Hero's bundle entry point.
 *
 * The default export is the install function the wrapper calls once per
 * registration record, before `mount()` (contract §1.3). It MUST return the
 * config object — the loader throws otherwise.
 *
 * One bundle per block: a shared bundle would defeat the per-record
 * `enabled` kill switch.
 */
import './hero.css';

import HeroEdit from './HeroEdit';
import HeroIcon from './HeroIcon';
import HeroView from './HeroView';
import HeroSchema, { HERO_BLOCK_TYPE } from './schema';
import DericoReferenceWidget from './widgets/ReferenceWidget';
import DericoRingLegendWidget from './widgets/RingLegendWidget';

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
  // Namespaced keys: this map is global and last-wins.
  registry.registerWidget?.({
    key: 'widget',
    definition: {
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
    // The whole full-bleed wiring (contract §1.4); Aurora materialises it onto
    // the node. Works only while `blockSchema` declares no `blockWidth`.
    defaultBlockWidth: 'full',
  };

  return config;
}

export { HERO_BLOCK_TYPE };
