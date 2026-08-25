/**
 * The `view` half (contract §1.1).
 *
 * On a Blicca site nothing renders this: the published page is drawn by the
 * server view `@@aurora-block-derico-hero`, which builds the real resolution
 * ladder. It is implemented anyway, and not as a stub, because the contract's
 * single-ecosystem exemption for a brand block covers PUBLICATION only — a
 * brand block that skips `view` is not exempt, it is broken, and it renders
 * blank the day the site is served through Aurora proper.
 */
import Hero from './Hero';
import HeroMedia from './HeroMedia';
import type { HeroData } from './data';

export function HeroView({ data }: { data: HeroData }) {
  return <Hero data={data} media={<HeroMedia data={data} />} />;
}

export default HeroView;
