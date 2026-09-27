/**
 * Reading the hero's stored JSON. Nothing is `required`, so every reader
 * answers "absent" without throwing. The server renderer implements the same
 * degradation rules (`degradation.test.tsx`); change both together.
 */

export type Reference = { '@id'?: unknown };

export type LegendEntry = { title?: unknown; subtitle?: unknown };

export type HeroData = {
  kicker?: unknown;
  headline?: unknown;
  lede?: unknown;
  cta_label?: unknown;
  cta_href?: unknown;
  link_label?: unknown;
  link_href?: unknown;
  image_wide?: unknown;
  image_portrait?: unknown;
  legend?: unknown;
};

/** Exactly four legend entries; the numerals are position, never content. */
export const LEGEND_LENGTH = 4;

/** The ring the design marks as "now" — the last one, by construction. */
export const LEGEND_NOW_INDEX = LEGEND_LENGTH - 1;

export function text(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

/**
 * The `@id` of a reference field.
 *
 * Stored as a one-element list of `{"@id": …}`, but a value that
 * never went through the editor may be a bare object or a plain string, and
 * neither is worth throwing over.
 */
export function reference(value: unknown): string {
  const first = Array.isArray(value) ? value[0] : value;
  if (typeof first === 'string') return first.trim();
  if (first && typeof first === 'object') {
    const id = (first as Reference)['@id'];
    if (typeof id === 'string') return id.trim();
  }
  return '';
}

/**
 * A link renders only when it has BOTH a label and a target.
 *
 * Symmetric on purpose: no fall back to the target's Title. A fallback would
 * make the canvas fetch the target just to agree with the server, and the two
 * surfaces would still diverge for the moment between picking and reloading.
 */
export function link(
  label: unknown,
  href: unknown,
): { label: string; href: string } | null {
  const labelText = text(label);
  const target = reference(href);
  return labelText && target ? { label: labelText, href: target } : null;
}

/**
 * The canvas preview URL for a picked image.
 *
 * One plain scale derived from the `@id`: a freshly picked image has no
 * `image_scales` yet, so deriving the URL is the only path that always works.
 */
export function previewImage(value: unknown): string {
  const id = reference(value);
  return id ? `${id.replace(/\/+$/, '')}/@@images/image/large` : '';
}

/** Four entries, always — a shorter or absent list is padded, not rejected. */
export function legend(value: unknown): Array<{ title: string; subtitle: string }> {
  const stored = Array.isArray(value) ? value : [];
  return Array.from({ length: LEGEND_LENGTH }, (_unused, index) => {
    const entry = (stored[index] ?? {}) as LegendEntry;
    return { title: text(entry.title), subtitle: text(entry.subtitle) };
  });
}

/** The legend a freshly inserted hero carries. */
export function emptyLegend(): Array<{ title: string; subtitle: string }> {
  return Array.from({ length: LEGEND_LENGTH }, () => ({
    title: '',
    subtitle: '',
  }));
}
