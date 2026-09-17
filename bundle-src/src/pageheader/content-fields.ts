/**
 * The page's title and description, bound through the host's form atom.
 *
 * The host keeps the content item being edited in a jotai atom registered
 * as the `formAtom` utility; Aurora's title node reads and writes the title
 * through it with `useFieldFocusedAtom`, and Blicca's save carries every
 * field of that atom the canvas changed (block add-on contract §1.7). This
 * block binds `title` and `description` the same way: what the author types
 * lands in the atom at once, and Save persists it with the blocks — so a
 * page with this block needs neither the tree's title node nor its
 * description node, and the field stays what it was when the block goes.
 *
 * Resolved at render time through the registry, with an inert fallback where
 * no host registered one (a test, a bare registry). `jotai` and
 * `@plone/helpers` are promised facades (contract §2.1): the bundle imports
 * them from the page's import map and never carries a copy.
 */
import { atom, type PrimitiveAtom } from 'jotai';
import { useFieldFocusedAtom } from '@plone/helpers';
import config from '@plone/registry';

type Content = Record<string, unknown>;

export type ContentField = 'title' | 'description';

const fallbackFormAtom = atom<Content>({});

/** The host's form atom, or an inert one. */
export function formAtom(): PrimitiveAtom<Content> {
  const registry = config as {
    getUtility?: (options: { name: string; type: string }) => { method?: unknown } | undefined;
  };
  try {
    const method = registry.getUtility?.({ name: 'formAtom', type: 'atom' })?.method;
    const found = typeof method === 'function' ? method() : null;
    return (found ?? fallbackFormAtom) as PrimitiveAtom<Content>;
  } catch {
    return fallbackFormAtom;
  }
}

/**
 * `[value, setValue]` for one of the page's text fields. `''` while the atom
 * does not hold the field as a string — a bare registry, a field cleared to
 * `null` by restapi.
 */
export function useContentField(field: ContentField): [string, (value: string) => void] {
  const [value, setValue] = useFieldFocusedAtom<Content, string>(formAtom() as never, field as never);
  return [typeof value === 'string' ? value : '', setValue as (value: string) => void];
}
