/**
 * The Derico Snippet's sidebar form: one choice, nothing else.
 *
 * A brand block gains a variant only when the design itself demands one, and
 * this block IS that case: the design ships several static ornaments that
 * differ in nothing but their markup, so the variant field is the block's
 * whole reason to be generic. `choices` is what makes the wrapper render a
 * select (its registered `choices` widget slot) — no custom widget needed.
 *
 * No `blockWidth`, same interlock as the hero: the width is template, not
 * content. `defaultBlockWidth: 'layout'` in index.tsx fixes it at the shell
 * width the mockup places both ornaments at, and a `blockWidth` property here
 * would silently hand the control back (contract §1.4).
 */

export const SNIPPET_BLOCK_TYPE = 'derico-snippet';

/** One entry per file in `src/plonetheme/derico/snippets/`. */
export const SNIPPET_CHOICES: Array<[string, string]> = [
  ['balkenlage', 'Balkenlage (Trenner)'],
  ['service-frame', 'Ständerwerk (Rahmen)'],
];

export const SnippetSchema = {
  title: 'Derico Snippet',
  fieldsets: [
    {
      id: 'default',
      title: 'Default',
      fields: ['snippet'],
    },
  ],
  required: [],
  properties: {
    snippet: {
      title: 'Snippet',
      choices: SNIPPET_CHOICES,
      default: 'balkenlage',
    },
  },
};

export default SnippetSchema;
