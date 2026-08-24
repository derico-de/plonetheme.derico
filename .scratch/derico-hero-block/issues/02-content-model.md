# Decide: the Derico Hero's content model

Type: grilling
Status: closed
Blocked by: 01

## Question

Fix the block's `blockSchema` and its stored JSON shape, so the editor half and
the server half can be built against the same contract.

Settled at charting — the editable inventory is kicker, headline, lede, primary
CTA (text + link), secondary link (text + link), wide image, portrait image, and
exactly four `{title, subtitle}` legend pairs. No alt text, no author options.

Open here:

- **Field ids and types.** Names for each of the above, and which are plain text
  versus rich text. Is the lede plain (one paragraph, matching the mockup) or
  rich (author might want emphasis)? Are the CTA link fields URL strings or
  Plone content references — internal links to `kontakt.html`'s equivalent
  should survive a rename.
- **The legend's shape.** Four fixed field pairs (`ring1Title`, `ring1Text`, …)
  or one four-element array? The array is tidier but Aurora's schema support for
  fixed-length object lists needs checking; the flat form is dull and certain.
- **Empty and partial states.** What renders when the secondary link has a label
  but no URL, when a legend entry is blank, when no image is set at all? The
  block must degrade without throwing in either half.
- **The `@type` string and record name.** Consistent with the contract's
  `<pkg>.<block>` convention.

Write the resulting schema into the answer so 08 and 09 can build from it
without re-deciding.

## Answer

Grilled with md@derico.de, 2026-08-23. Every field below is fixed; 08 and 09
build against it without re-deciding. Facts cited were read from the checkout
during the session and are quoted with their paths.

### `@type`, record and view names

| Thing | Value |
| --- | --- |
| `@type` | `derico-hero` |
| CSS class / DOM | `.block-derico-hero`, `data-block-type="derico-hero"` (stamped by `plate.py:341-351`) |
| Server view | `browser:page name="aurora-block-derico-hero"` (contract §5.1) |
| Registry record | `plonetheme.derico.hero` (contract §3.2, `<pkg>.<block>`) |
| Bundle | `++plone++plonetheme.derico.blocks/hero.js` (ticket 04's `static-blocks/`) |

Kebab, not `derico_hero` and not a dot: `@type` is not only a dispatch key, it
lands verbatim in a CSS class and a ZCML view name. A dot would need escaping in
every selector; `aurora-block-default` already establishes the hyphen.

### `blockSchema`

All text is **plain**. No rich text exists to choose: cmsui registers
`recurrence, date, datetime, boolean, align, size, width, image, object_browser,
querystring` plus `choices`/`Relation List`/catalog
(`cmsui/config/widgets.ts:16-68`, `wrapper/src/bootstrap/config.ts:35-66`), and
the default widget is a single-line `TextField` (`widgets.ts:17`).

```ts
{
  title: 'Derico Hero',
  fieldsets: [{ id: 'default', title: 'Default',
    fields: ['kicker', 'headline', 'lede',
             'cta_label', 'cta_href', 'link_label', 'link_href',
             'image_wide', 'image_portrait', 'legend'] }],
  required: [],                       // nothing required — see degradation
  properties: {
    kicker:     { title: 'Kicker' },
    headline:   { title: 'Headline' },
    lede:       { title: 'Lede', widget: 'derico_textarea' },

    cta_label:  { title: 'Primary call to action' },
    cta_href:   { title: 'Primary target', widget: 'object_browser',
                  mode: 'single', allowExternals: true,
                  selectedItemAttrs: ['@id'] },
    link_label: { title: 'Secondary link' },
    link_href:  { title: 'Secondary target', widget: 'object_browser',
                  mode: 'single', allowExternals: true,
                  selectedItemAttrs: ['@id'] },

    image_wide:     { title: 'Wide image', widget: 'object_browser',
                      mode: 'single', allowExternals: false,
                      selectableTypes: ['Image'], upload: true,
                      selectedItemAttrs: ['@id'] },
    image_portrait: { title: 'Portrait image', widget: 'object_browser',
                      mode: 'single', allowExternals: false,
                      selectableTypes: ['Image'], upload: true,
                      selectedItemAttrs: ['@id'] },

    legend:     { title: 'Ring legend', widget: 'derico_ring_legend' },
  },
}
```

No field id collides with a registered widget key — the sidebar resolves
`getWidgetByFieldId(id)` **first** (`cmsui/components/Form/Field.tsx:169-180`),
so a field named `image` would silently take the image widget. `image_wide` /
`image_portrait` avoid it and declare `object_browser` explicitly.

`selectableTypes` and `upload` are **not yet forwarded** by Blicca's widget —
see ticket 13, which blocks 08.

### Editing surface: sidebar, canvas is a preview

Every field is edited in the sidebar form; the canvas renders the block as it
will look, with in-canvas placeholders for the two crops while unset (the
Teaser's precedent, `@plone/blocks/Teaser/TeaserBlockEdit.tsx:44-60`). No
in-canvas text editing: the block is a Plate **void** node, so inline text means
re-solving focus, undo and selection inside the void — a large bespoke cost that
buys editing flexibility in a block whose premise is that the author gets none.

### Stored JSON

On the `ploneBlock` void node inside `blocks.__somersault__.value`:

```json
{
  "type": "ploneBlock",
  "@type": "derico-hero",
  "kicker": "Nachhaltige Lösungen, seit über 20 Jahren",
  "headline": "Anwendungen, die bleiben.",
  "lede": "Wir entwickeln Geschäftsanwendungen …",
  "cta_label": "Erstgespräch vereinbaren",
  "cta_href":  [{ "@id": "../resolveuid/<uid>" }],
  "link_label": "Alle Leistungen",
  "link_href": [{ "@id": "../resolveuid/<uid>" }],
  "image_wide":     [{ "@id": "../resolveuid/<uid>" }],
  "image_portrait": [{ "@id": "../resolveuid/<uid>" }],
  "legend": [
    { "title": "schneller Prototyp",    "subtitle": "in Wochen bedienbar" },
    { "title": "erste Anwendung",       "subtitle": "trägt die tägliche Arbeit" },
    { "title": "erfahrener Begleiter",  "subtitle": "wächst mit den Anforderungen" },
    { "title": "mit der Zeit gegangen", "subtitle": "offen, aktuell, migrierbar" }
  ]
}
```

Four decisions are load-bearing here:

- **References, not URLs, for all four `@id` fields.** Internal links survive a
  rename or a move because restapi rewrites `@id`↔`resolveuid` on every save and
  load (`serializer/blocks.py:232-234`, `deserializer/blocks.py:89-92`). Stored
  as a one-element list, matching every upstream precedent and Blicca's
  `_first()` helpers.
- **Trimmed to bare `{"@id": …}`.** The content browser returns an enriched
  brain (`UID`, `title`, `review_state`, `image_field`, `image_scales`); the
  Teaser persists all of it and thereby stores a snapshot of another object's
  metadata that nothing refreshes. The hero's edit component trims in its
  `onChange` before `setBlock` — `selectedItemAttrs` will not do it for us,
  because `BliccaObjectBrowserWidget` ignores the list and always fetches the
  full set (`wrapper/src/widgets/ObjectBrowserWidget.tsx:9-14`). `image_field`
  is re-derived server-side and `image_scales` is stripped by restapi on save,
  so nothing is lost.
- **`legend` is always exactly four entries**, seeded at insert with four
  `{"title": "", "subtitle": ""}`. Fixed length is a template invariant both
  halves may assert rather than defend against; the numerals stay
  position-derived and `is-now` is unambiguously index 3. An array rather than
  eight flat `ring1Title…ring4Subtitle` keys: the count belongs in the template,
  not in the field names, so a design that ever wants five rings is a template
  change and not a data migration. Aurora has no object-list widget — `Field.tsx`
  has no `items`/`array` branch at all — so the array needs a widget either way;
  the stored contract is not bent around that.
- **No `blockWidth` key.** The width is template, like the rings — "the block
  fixes its own width; the author never chooses it". Today `block_width_for`
  (`plate.py:113-119`) falls back on `DEFAULT_BLOCK_WIDTHS[node["type"]]`, where
  `type` is the literal `"ploneBlock"` and never the `@type`, so full-bleed
  depends entirely on ticket 11. 08, 09 and 10 already block on it.

**Insert-time default** written by the slash-menu entry — no `*_href` or
`image_*` keys until something is picked:

```json
{ "type": "ploneBlock", "@type": "derico-hero",
  "kicker": "", "headline": "", "lede": "",
  "cta_label": "", "link_label": "",
  "legend": [{"title":"","subtitle":""},{"title":"","subtitle":""},
             {"title":"","subtitle":""},{"title":"","subtitle":""}] }
```

### Degradation

Nothing is `required`: a half-authored hero must save and preview without
throwing. The public renderer emits what is present and omits the rest; the
nagging lives in the editor canvas, which shows a visible incomplete hint. Both
halves must agree case for case, or canvas and page diverge:

| State | Renders |
| --- | --- |
| No `headline` / `kicker` / `lede` | that element is omitted; the grid keeps its shape |
| Label **or** target missing on a link | nothing — never a dead `<a>`, never a label-less button. Symmetric on purpose: no Title fallback, so the canvas needs no fetch to agree with the server |
| Both crops set | full art direction, portrait under `(max-width: 55.99rem)` |
| One crop only | that image at every breakpoint; the `media` sources it has no image for are dropped |
| No crop at all | no `<picture>`, no `.hero-wash`; the section falls back to its token background |
| Legend entry half-filled | numeral always renders (it is geometry); only the half with text emits its `<dt>` or `<dd>` |
| Legend entry entirely empty | numeral only |

Contract §5.4 remains the backstop below all of this: a throwing renderer
becomes a `block-render-error` placeholder in production, propagating loudly in
development.

### Widget registrations — namespaced

The hero's bundle registers **`derico_textarea`** and **`derico_ring_legend`**,
never the generic `textarea` / `legend`. `config.registerWidget` is a global,
last-wins map shared by the whole editor (`bootstrap/config.ts:35-66` overrides
cmsui's entries by exactly this mechanism); a brand block must not redefine
generic vocabulary for blocks it knows nothing about. If a generic `textarea`
widget should exist — `QuantaTextAreaField` ships unregistered at
`@plone/components/src/index.ts:77` — that is Blicca's call to make
deliberately, not a side effect of installing a theme.

`derico_ring_legend` renders four fixed title/subtitle pairs and writes the
whole four-element array back on every change.

### Left open for ticket 08 (does not affect the content model)

How `derico_textarea` gets its input element: bundle `QuantaTextAreaField` from
`@plone/components` into the block bundle — the import map exposes only `react`,
`platejs`, `jotai`, `@plone/registry` (`aurora_edit.pt:38`), so it cannot be
imported at runtime — or render a plain `<textarea>` styled by the hero's own
scoped sheet. Bundling matches Blicca's sidebar chrome but duplicates react-aria
context; the plain element is dependency-free but looks off-brand next to the
Quanta fields. Stored shape is identical either way.
