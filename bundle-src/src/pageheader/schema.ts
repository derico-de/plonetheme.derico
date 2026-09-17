/**
 * The Derico Page Header's sidebar form (contract §1.5).
 *
 * One field. The title and the description are not here because they are
 * not the block's: they are the page's fields, edited on the canvas through
 * the host's form atom (`content-fields.ts`) — and a second copy in the
 * sidebar would be a second control for the same value. The kicker is here
 * as well as on the canvas because the sidebar is where an author looks for
 * "what does this block store".
 *
 * No `blockWidth`: the width is template, not content. Aurora resolves a
 * ploneBlock's width as `styleFields.blockWidth ?? defaultBlockWidth`, so
 * declaring the field here would hand the control back and silently undo
 * `defaultBlockWidth: 'layout'` in index.tsx (contract §1.4).
 */

export const PAGE_HEADER_BLOCK_TYPE = 'derico-page-header';

export const PageHeaderSchema = {
  title: 'Derico Page Header',
  // The id is load-bearing: cmsui expands only the fieldset literally called
  // `default`, so a renamed one opens closed.
  fieldsets: [{ id: 'default', title: 'Default', fields: ['kicker'] }],
  required: [],
  properties: {
    kicker: {
      title: 'Kicker',
      description:
        'The line above the title. The title and the description are the page’s own fields — type them on the canvas.',
    },
  },
};

export default PageHeaderSchema;
