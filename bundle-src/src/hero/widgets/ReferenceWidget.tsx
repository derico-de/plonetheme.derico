/**
 * `derico_reference` — an `object_browser` pick, trimmed to a bare `@id`.
 *
 * ## Why this widget exists at all
 *
 * Ticket 02 decided the stored shape (`[{"@id": "../resolveuid/<uid>"}]` and
 * nothing else) and said the block's *edit component* would trim the enriched
 * brain in its `onChange` before calling `setBlock`. That is how Aurora's
 * teaser does it — but the teaser renders its own browser inside the canvas.
 * The hero edits every field in the SIDEBAR, and the sidebar writes straight
 * onto the Plate node: `SidebarAfterEditable`'s `onFormDataChange` calls
 * `editor.tf.setNodes(patch)` itself (`wrapper/src/editor/plone-block-sidebar.tsx`).
 * The edit component is never consulted and has no interception point, so a
 * widget is the only seam where the trim can happen. The stored shape ticket
 * 02 fixed is unchanged; only the place that produces it moved.
 *
 * ## Why trim
 *
 * The content browser returns an enriched brain — `UID`, `title`,
 * `review_state`, `image_field`, `image_scales`. Persisting all of it stores a
 * snapshot of ANOTHER object's metadata that nothing ever refreshes. The
 * server re-derives `image_field` and restapi strips `image_scales` on save,
 * so nothing is lost. `selectedItemAttrs` will not do it for us — Blicca's
 * widget ignores the list and always fetches the full contract field set.
 *
 * Options travel on `widgetOptions.pattern_options`, Aurora's own envelope
 * (contract §1.5); this widget forwards the whole props bag, so it neither
 * knows nor cares which keys the host reads.
 */
import { useCallback, useState } from 'react';
import type { ComponentType } from 'react';
import config from '@plone/registry';

import { reference } from '../data';

export type ReferenceWidgetProps = {
  id?: string;
  name?: string;
  label?: string;
  description?: string;
  mode?: string;
  widgetOptions?: Record<string, unknown>;
  defaultValue?: unknown;
  value?: unknown;
  onChange?: (value: Array<{ '@id': string }> | undefined) => void;
};

/** The stored shape: a one-element list of `{"@id": …}`, or nothing at all. */
export function trim(
  selected: Array<Record<string, unknown>> | undefined,
): Array<{ '@id': string }> | undefined {
  const first = selected?.[0];
  const id = first?.['@id'];
  return typeof id === 'string' && id ? [{ '@id': id }] : undefined;
}

export function DericoReferenceWidget(props: ReferenceWidgetProps) {
  const { onChange } = props;
  const [picked, setPicked] = useState(() =>
    reference(props.value ?? props.defaultValue),
  );
  const ObjectBrowser = config.getWidget('object_browser') as
    | ComponentType<Record<string, unknown>>
    | undefined;

  const onSelect = useCallback(
    (selected: Array<Record<string, unknown>>) => {
      const trimmed = trim(selected);
      setPicked(trimmed ? trimmed[0]['@id'] : '');
      onChange?.(trimmed);
    },
    [onChange],
  );

  const onClear = useCallback(() => {
    setPicked('');
    onChange?.(undefined);
  }, [onChange]);

  return (
    <div className="derico-hero-widget derico-hero-widget--reference">
      {props.label ? <label>{props.label}</label> : null}
      {picked ? (
        <p className="derico-hero-widget__picked">
          <span title={picked}>{picked.split('/').filter(Boolean).pop()}</span>
          <button type="button" onClick={onClear}>
            Clear
          </button>
        </p>
      ) : null}
      {ObjectBrowser ? (
        <ObjectBrowser
          {...props}
          label={undefined}
          description={undefined}
          mode={props.mode ?? 'single'}
          onChange={onSelect}
        />
      ) : (
        <p className="derico-hero-widget__description">
          No content browser is registered in this editor.
        </p>
      )}
      {props.description ? (
        <p className="derico-hero-widget__description">{props.description}</p>
      ) : null}
    </div>
  );
}

export default DericoReferenceWidget;
