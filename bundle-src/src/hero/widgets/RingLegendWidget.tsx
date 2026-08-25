/**
 * `derico_ring_legend` — the four `{title, subtitle}` pairs beneath the rings.
 *
 * Exactly four, always: the numerals are derived from position and the "now"
 * highlight is unambiguously the last one, so the count is a template
 * invariant both halves may assert rather than defend against. Aurora has no
 * object-list widget at all — cmsui's `Field` has no `items`/`array` branch —
 * so an array field needs a widget of its own either way; ticket 02 chose the
 * array over eight flat `ring1Title…ring4Subtitle` keys so that a design which
 * ever wants five rings is a template change and not a data migration.
 *
 * Writes the WHOLE four-element array on every keystroke. Uncontrolled inputs
 * over a ref, for the same reason as the textarea: cmsui hands widgets a
 * `defaultValue` and re-renders the form on each change, and a controlled
 * input in that loop loses the caret on every character.
 */
import { useCallback, useRef } from 'react';

import { LEGEND_LENGTH, LEGEND_NOW_INDEX, legend } from '../data';

export type RingLegendWidgetProps = {
  id?: string;
  name?: string;
  label?: string;
  description?: string;
  defaultValue?: unknown;
  value?: unknown;
  onChange?: (value: Array<{ title: string; subtitle: string }>) => void;
};

export function DericoRingLegendWidget(props: RingLegendWidgetProps) {
  const { onChange } = props;
  const entries = useRef(legend(props.value ?? props.defaultValue));

  const update = useCallback(
    (index: number, key: 'title' | 'subtitle', next: string) => {
      entries.current = entries.current.map((entry, position) =>
        position === index ? { ...entry, [key]: next } : entry,
      );
      onChange?.(entries.current);
    },
    [onChange],
  );

  const fieldId = props.id ?? props.name ?? 'legend';

  return (
    <fieldset className="derico-hero-widget derico-hero-widget--legend">
      {props.label ? <legend>{props.label}</legend> : null}
      {Array.from({ length: LEGEND_LENGTH }, (_unused, index) => (
        <div
          key={index}
          className={
            index === LEGEND_NOW_INDEX
              ? 'derico-hero-widget__ring is-now'
              : 'derico-hero-widget__ring'
          }
        >
          <span aria-hidden="true">{index + 1}</span>
          <label htmlFor={`${fieldId}-${index}-title`}>Title</label>
          <input
            id={`${fieldId}-${index}-title`}
            type="text"
            defaultValue={entries.current[index].title}
            onChange={(event) => update(index, 'title', event.target.value)}
          />
          <label htmlFor={`${fieldId}-${index}-subtitle`}>Caption</label>
          <input
            id={`${fieldId}-${index}-subtitle`}
            type="text"
            defaultValue={entries.current[index].subtitle}
            onChange={(event) => update(index, 'subtitle', event.target.value)}
          />
        </div>
      ))}
      {props.description ? (
        <p className="derico-hero-widget__description">{props.description}</p>
      ) : null}
    </fieldset>
  );
}

export default DericoRingLegendWidget;
