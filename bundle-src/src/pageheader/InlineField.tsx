/**
 * The inline control the canvas draws for one of the header's three texts:
 * a bare `<textarea>` sitting exactly where the published page puts the
 * words, dressed by the sheet to inherit the element it stands in — so the
 * author types INTO the heading and sees the heading.
 *
 * A textarea for all three, on purpose: the title must wrap like the h1 it
 * will become, and an `<input>` cannot. A `line` folds any newline to a
 * space and swallows Enter.
 *
 * A ploneBlock is a Plate void with `contentEditable={false}`, so a native
 * control inside it receives focus and text normally — but every key event
 * still bubbles to the editor's plugin handlers, where Enter inserts a
 * paragraph after the block and Backspace on a selected block removes it.
 * The control therefore stops its keyboard and clipboard events at itself
 * (contract §1.7). Mouse events are left alone: a click must still select
 * the block, so its sidebar opens.
 */
import { useLayoutEffect, useRef, type SyntheticEvent } from 'react';

export type InlineFieldProps = {
  value: string;
  onChange: (value: string) => void;
  /** What the control shows while empty, and what a screen reader calls it. */
  label: string;
  /** Fold newlines away and swallow Enter: a title is one line. */
  line?: boolean;
};

const stop = (event: SyntheticEvent) => event.stopPropagation();

export function InlineField({ value, onChange, label, line = false }: InlineFieldProps) {
  const ref = useRef<HTMLTextAreaElement>(null);

  // Grow with the text; `field-sizing: content` does this in CSS where the
  // browser knows it, this is the fallback everywhere else.
  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) return;
    element.style.height = 'auto';
    element.style.height = `${element.scrollHeight}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      className="page-header__input"
      rows={1}
      value={value}
      placeholder={label}
      aria-label={label}
      onChange={(event) => {
        const next = event.target.value;
        onChange(line ? next.replace(/[\r\n]+/g, ' ') : next);
      }}
      onKeyDown={(event) => {
        event.stopPropagation();
        if (line && event.key === 'Enter') event.preventDefault();
      }}
      onKeyUp={stop}
      onBeforeInput={stop}
      onPaste={stop}
      onCopy={stop}
      onCut={stop}
      onDrop={stop}
    />
  );
}

export default InlineField;
