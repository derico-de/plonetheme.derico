/**
 * `derico_textarea` — the lede's multi-line input.
 *
 * Ticket 02 left one question open for this ticket: bundle Aurora's
 * `QuantaTextAreaField` (it ships unregistered in `@plone/components`) or
 * render a plain element. **Plain element.** `@plone/components` is not a
 * promised module (contract §2.1), so bundling it would compile react-aria
 * and a second react-aria context into the block bundle to gain one field;
 * the styling gap it was meant to close is closed instead by the block's own
 * sheet, which reaches the sidebar because the sidebar lives inside the
 * `.aurora-editor` scope root.
 *
 * Registered under a namespaced key, never the generic `textarea`:
 * `registerWidget` is a global, last-wins map, and whether Blicca should
 * register a generic one is Blicca's call to make deliberately, not a side
 * effect of installing a theme.
 *
 * Uncontrolled, like every other field in this form: cmsui hands widgets
 * `defaultValue` (not `value`) and remounts the form when the selected block
 * changes, so holding the text in React state here would only add a caret to
 * lose.
 */
export type TextareaWidgetProps = {
  id?: string;
  name?: string;
  label?: string;
  description?: string;
  placeholder?: string;
  defaultValue?: unknown;
  value?: unknown;
  onChange?: (value: string) => void;
};

export function DericoTextareaWidget(props: TextareaWidgetProps) {
  const initial = props.value ?? props.defaultValue ?? '';
  const fieldId = props.id ?? props.name;
  return (
    <div className="derico-hero-widget">
      {props.label ? <label htmlFor={fieldId}>{props.label}</label> : null}
      <textarea
        id={fieldId}
        name={props.name}
        rows={4}
        defaultValue={typeof initial === 'string' ? initial : ''}
        placeholder={props.placeholder}
        onChange={(event) => props.onChange?.(event.target.value)}
      />
      {props.description ? (
        <p className="derico-hero-widget__description">{props.description}</p>
      ) : null}
    </div>
  );
}

export default DericoTextareaWidget;
