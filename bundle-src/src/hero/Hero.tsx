/**
 * The Derico Hero, as one component rendered by both `edit` and `view`.
 *
 * ## `.derico-hero`, not `.block-derico-hero`
 *
 * Aurora's `block-<@type>` wrapper is the full-bleed box on the public view
 * but only the column box in the canvas, so the hero paints on its own root.
 *
 * ## The hero never sets its own width
 *
 * The breakout is Blicca's, on the wrapper (public) and the inner container
 * (canvas), and `defaultBlockWidth: 'full'` is the whole of the wiring. A
 * `width` here would break the equivalence in one surface only.
 *
 * ## No whitespace-only text nodes
 *
 * The Plate editable's inherited `white-space: pre-wrap` turns newlines
 * between elements into line boxes; JSX drops them, the server template
 * must strip its own.
 */
import Rings from './Rings';
import { legend, link, reference, text } from './data';
import type { HeroData } from './data';

export type HeroProps = {
  data: HeroData;
  /**
   * The canvas renders one plain scale per crop; the public view renders the
   * spliced two-crop `<picture>` its server template builds. Both emit the
   * same `.hero-media` element with an `<img>` inside it, so one rule set
   * covers them.
   */
  media?: React.ReactNode;
};

export function Hero({ data, media }: HeroProps) {
  const kicker = text(data.kicker);
  const headline = text(data.headline);
  const lede = text(data.lede);
  const cta = link(data.cta_label, data.cta_href);
  const quiet = link(data.link_label, data.link_href);
  const entries = legend(data.legend);
  // Asked of the DATA, not of `media`: a React element is truthy even when
  // the component returns null, so keying the wash on the slot painted a
  // gradient over the token ground of a hero with no photograph at all.
  const hasMedia = Boolean(
    reference(data.image_wide) || reference(data.image_portrait),
  );

  return (
    <section className="derico-hero">
      {media}
      {hasMedia ? <div className="hero-wash" aria-hidden="true" /> : null}
      <div className="home-hero__grid">
        <div>
          {kicker ? <p className="kicker">{kicker}</p> : null}
          {headline ? <h1>{headline}</h1> : null}
          {lede ? <p className="lede">{lede}</p> : null}
          {cta || quiet ? (
            <div className="action-row">
              {cta ? (
                <a className="button" href={cta.href}>
                  {cta.label}
                </a>
              ) : null}
              {quiet ? (
                <a className="quiet-link" href={quiet.href}>
                  {quiet.label}
                </a>
              ) : null}
            </div>
          ) : null}
        </div>
        <Rings entries={entries} />
      </div>
    </section>
  );
}

export default Hero;
