/**
 * The Derico Hero's sidebar form (hero ticket 02, contract §1.5).
 *
 * Deliberately inflexible: the design's text and images and nothing else. No
 * width control, no palette variant, no "hide the rings" toggle — a brand
 * block implements one design template and offers the author no options.
 *
 * Two omissions are load-bearing:
 *
 * - **No `blockWidth`.** The width is template, not content. Aurora resolves a
 *   ploneBlock's width as `styleFields.blockWidth ?? defaultBlockWidth`, so
 *   declaring the field here would hand the control back and silently undo
 *   `defaultBlockWidth: 'full'` in index.tsx (contract §1.4).
 * - **Nothing in `required`.** A half-authored hero has to save and preview;
 *   the renderers omit what is missing (see data.ts).
 */

export const HERO_BLOCK_TYPE = 'derico-hero';

/**
 * `object_browser` options ride Aurora's own `widgetOptions.pattern_options`
 * envelope (contract §1.5), not top-level schema keys. plone.restapi already
 * serializes relation fields this way, so a schema written like this keeps
 * working if Blicca's widget substitution is ever dropped for Aurora's.
 */
const imagePick = (title: string) => ({
  title,
  widget: 'derico_reference',
  mode: 'single',
  widgetOptions: {
    pattern_options: { selectableTypes: ['Image'], upload: true },
  },
});

const contentPick = (title: string) => ({
  title,
  widget: 'derico_reference',
  mode: 'single',
});

export const HeroSchema = {
  title: 'Derico Hero',
  fieldsets: [
    {
      id: 'default',
      title: 'Default',
      fields: [
        'kicker',
        'headline',
        'lede',
        'cta_label',
        'cta_href',
        'link_label',
        'link_href',
        'image_wide',
        'image_portrait',
        'legend',
      ],
    },
  ],
  required: [],
  properties: {
    kicker: { title: 'Kicker' },
    headline: { title: 'Headline' },
    // Namespaced, never the generic `textarea`: `registerWidget` is a global
    // last-wins map, and a theme must not redefine vocabulary for blocks it
    // knows nothing about (ticket 02).
    lede: { title: 'Lede', widget: 'derico_textarea' },

    cta_label: { title: 'Primary call to action' },
    cta_href: contentPick('Primary target'),
    link_label: { title: 'Secondary link' },
    link_href: contentPick('Secondary target'),

    // `image_wide` / `image_portrait`, never `image`: cmsui resolves a
    // widget by FIELD ID before it looks at `widget`, so a field called
    // `image` would silently take the registered image widget.
    image_wide: imagePick('Wide image'),
    image_portrait: imagePick('Portrait image'),

    legend: { title: 'Ring legend', widget: 'derico_ring_legend' },
  },
};

export default HeroSchema;
