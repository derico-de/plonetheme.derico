/**
 * The rings figure: geometry is template, words are content.
 *
 * The circles, their offsets and the marker positions are the design, not
 * data — there is no field for them and no author-facing control. Only the
 * four `{title, subtitle}` pairs come from the block; the numerals are
 * derived from position, and the `is-now` highlight is the last ring by
 * construction.
 *
 * The legend is HTML *beneath* the SVG precisely so it does not scale with
 * the graphic: ticket 07 measured captions at 15px on both surfaces and at
 * both 1440 and 375, which is Clara's label floor exactly. Fold the legend
 * into the SVG and that floor goes.
 *
 * A half-filled entry keeps its numeral and emits only the half that has
 * text; an entirely empty entry is a numeral and a rule (ticket 02's
 * degradation table).
 */
import { LEGEND_NOW_INDEX } from './data';

type LegendEntries = Array<{ title: string; subtitle: string }>;

export function Rings({ entries }: { entries: LegendEntries }) {
  return (
    <figure className="rings-figure">
      <div className="rings-stage">
        <svg
          className="rings-disc"
          viewBox="0 0 680 470"
          role="img"
          aria-label="Wachstumsringe einer Anwendung"
        >
          <g transform="translate(105 0)">
            <circle cx="150" cy="235" r="40" className="ring-thin" />
            <circle cx="153" cy="232" r="80" />
            <circle cx="147" cy="238" r="125" className="ring-thin" />
            <circle cx="154" cy="231" r="170" />
            <circle cx="148" cy="237" r="215" className="ring-thin" />
            <circle cx="152" cy="234" r="250" />
            <circle cx="150" cy="235" r="290" className="ring-now" />
            <circle cx="151" cy="234" r="315" className="ring-future" />
          </g>
        </svg>
        <ol className="ring-markers" aria-hidden="true">
          {entries.map((_entry, index) => (
            <li key={index} className={index === LEGEND_NOW_INDEX ? 'is-now' : undefined}>
              {index + 1}
            </li>
          ))}
        </ol>
      </div>
      <dl className="ring-legend">
        {entries.map((entry, index) => (
          <div key={index} className={index === LEGEND_NOW_INDEX ? 'is-now' : undefined}>
            <b>{index + 1}</b>
            {entry.title ? <dt>{entry.title}</dt> : null}
            {entry.subtitle ? <dd>{entry.subtitle}</dd> : null}
          </div>
        ))}
      </dl>
    </figure>
  );
}

export default Rings;
