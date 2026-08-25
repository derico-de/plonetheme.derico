/**
 * The Derico Hero, as one component rendered by both `edit` and `view`.
 *
 * ## `.derico-hero`, not `.block-derico-hero`
 *
 * Aurora stamps `block-<@type>` on the block WRAPPER, and ticket 07 measured
 * what that wrapper actually is on each surface at 1440: on the public view
 * it is the full-bleed box (1220 @220), but in the canvas it is only the
 * column box (1134.9 @262.5) with the breakout one level in, on
 * `.block-inner-container`. Painting the hero on the wrapper therefore gives
 * the editor a 1134.9px hero whose `overflow: hidden` clips the 1220px
 * container inside it — the dark ground stops at the column edge and there is
 * no breakout at all. The component owns its own root element instead, and
 * both surfaces then measure 1220 @220 to the pixel.
 *
 * The `.block-derico-hero` stamp stays free for `derico.css`'s
 * chrome-suppression rule, which wants the wrapper anyway.
 *
 * ## The hero never sets its own width
 *
 * The breakout is Blicca's, on the wrapper (public) and the inner container
 * (canvas), and `defaultBlockWidth: 'full'` is the whole of the wiring. A
 * `width` here would break the equivalence in one surface only.
 *
 * ## No whitespace-only text nodes
 *
 * The Plate editable computes `white-space: pre-wrap`, which inherits in and
 * turns every newline BETWEEN two elements into a real line box — ticket 07
 * measured the mockup's indented markup inflating the rings figure by 76%.
 * JSX drops inter-element whitespace, so this file is safe by construction;
 * a `dangerouslySetInnerHTML` preview would not be, and the server template
 * has to strip its own indentation.
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
