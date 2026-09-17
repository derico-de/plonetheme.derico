/**
 * Reading the page header's stored JSON.
 *
 * The block stores ONE thing: the kicker. The title and the description are
 * the page's own fields — `context.Title()` / `context.Description()` on the
 * published page, the host's form atom on the canvas (`content-fields.ts`).
 * Nothing is `required`, so every reader answers "absent" without throwing.
 */

export type PageHeaderData = {
  kicker?: unknown;
};

/** The trimmed text of a value, or `''` for anything that is not text. */
export function text(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

/** The value a control edits: untrimmed, or the author's trailing space is eaten. */
export function raw(value: unknown): string {
  return typeof value === 'string' ? value : '';
}
