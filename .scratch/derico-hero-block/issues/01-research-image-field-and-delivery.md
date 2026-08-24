# Research: how an Aurora block schema takes an image, and how it reaches the renderer

Type: research
Status: closed
Assignee: md@derico.de
Blocked by: —

## Question

The Derico Hero needs two image fields. Nobody here has yet written an Aurora
block that takes an image, so the mechanics are unknown at both ends.

Answer, from the Aurora sources in
`plone.blicca.auroraeditor/wrapper/node_modules/@plone/` and from Blicca's own
renderers in `src/plone/blicca/auroraeditor/browser/rendering/`:

1. **Authoring.** What does a `blockSchema` entry for an image look like — which
   field type and widget does Aurora ship, and what UI does the author get
   (upload, content browser, both)? How do `@plone/blocks`'s own `Image` and
   `Teaser` blocks declare theirs?
2. **Stored shape.** What lands in the block's JSON — a UID, an `@id` URL, a
   full serialised object? Is it a list even for a single image?
3. **Derived data.** The editor needs enough to draw a preview; the server
   renderer needs enough to build `<picture>`. Contract §5.3 says
   editor-expected derived data MUST arrive via a restapi serialisation
   transformer with a paired stripping deserialiser. What do `image_scales` and
   friends look like on the wire, and what does Blicca's existing
   `image_block.py` / `teaser_block.py` / `picture.py` already do with them?
4. **Reuse.** Is there a Blicca helper or base class that already turns a stored
   image reference into picture-variant markup, or does each renderer redo it?

Findings go in `../assets/`, with file:line citations. This blocks the content
model (02) and image delivery (05).

---

## Answer (2026-08-22)

Full findings, 718 lines with `path:line` on every claim:
[`../assets/01-image-field-and-delivery-findings.md`](../assets/01-image-field-and-delivery-findings.md).

**1. Authoring.** There is no image *field type*. `JSONSchema` is
`{title, fieldsets, properties: Record<string, any>, required}`
(`@plone/types/src/config/Blocks.d.ts:232`); behaviour comes from the `widget`
key. Two relevant widgets are registered by `@plone/cmsui`
(`cmsui/config/widgets.ts:41`): `image` and `object_browser`. The Image block
declares one bare property `url: {title: 'Image URL', widget: 'image'}`
(`@plone/blocks/Image/schema.tsx:33`) — `image_field` / `image_scales` are
never schema fields; the edit component writes them
(`Image/ImageBlockEdit.tsx:46`). The Teaser uses `object_browser` twice: `href`
with `mode: 'single'` and `preview_image` with `mode: 'image'`, each declaring
`selectedItemAttrs` (`Teaser/schema.tsx:23`).

**Blicca replaces both widgets** (`wrapper/src/bootstrap/config.ts:35`):
`BliccaImageWidget` is pat-contentbrowser restricted to `Image` **with** upload
and no external-URL input (`wrapper/src/widgets/ImageWidget.tsx:122`);
`BliccaObjectBrowserWidget` is the same host, unrestricted by type, **without**
upload.

**The trap that decides ticket 02.** The sidebar form calls widgets with a
one-argument `onChange(value)` (`cmsui/.../BlockSettingsForm.tsx:72`), so
`widget: 'image'`'s second argument — `{title, image_field, image_scales}` — is
silently dropped, and Blicca's compensating node patch is hard-coded to
`@type === 'image'` (`ImageWidget.tsx:28`). `object_browser` survives the
sidebar because the whole enriched-brain array *is* its value.

**2. Stored shape.** Two idioms, and they differ. The Image block stores a
**bare string**, `url = "../resolveuid/<UID>"` — Blicca deliberately stores
resolveuid rather than `@id` (`wrapper/src/widgets/ImageWidget.tsx:99`,
asserted in `tests/test_rendering_views.py:161`). The Teaser stores **lists of
objects**, `href: [selectedTarget]` (`Teaser/TeaserBlockEdit.tsx:29`), and
restapi normalises a bare string into `[{"@id": url}]`
(`plone/restapi/serializer/blocks.py:232`) — so yes, a list even for a single
image. `image_scales` is **never persisted at any depth**:
`ResolveUIDDeserializerBase` pops it from every dict it walks and rewrites
`@id` back to resolveuid (`plone/restapi/deserializer/blocks.py:86`).

**3. Derived data.** `image_scales` is a catalog metadata column
(`Products/CMFPlone/image_scales/indexer.py:9`), keyed by field name, each
value a **one-element list** of
`{filename, content-type, size, download, width, height, scales: {...}}`
(`plone/namedfile/adapters.py:62`), with `download` relative to the object URL.
`base_path` is not namedfile's — plone.volto's preview-image adapter adds it
(`plone/volto/behaviors/preview_link.py:64`) and both Aurora's `Image` and
Blicca's `scales.py` honour it as a base override.

Injection is **stock restapi**: `ResolveUIDSerializerBase._process_data`
resolves any `url` / `href` / `preview_image` string *and any nested dict's
`@id`*, injecting `image_scales` into the enclosing dict
(`serializer/blocks.py:76`). Editor and public renderer see identical data —
`@@aurora-edit` inlines `ISerializeToJson` (`aurora_edit.py:199`) and
`rendering/serializer.py:21` re-runs the same handler loop; `NestedBlocksVisitor`
descends into `__somersault__` (`plone/restapi/blocks.py:60`).

Blicca's `picture.py:81` builds `<picture>` through
`plone.namedfile.picture.Img2PictureTag` against `plone.picture_variants`,
choosing the variant from `size` / `blockWidth`; `scales.py:20` is the plain
`<img>` fallback. `image_block.py` (54 lines) and `teaser_block.py` (98) are
thin wrappers over those.

**4. Reuse.** A helper exists and all three renderers use it — `picture_tag`,
`variant_for_image_block`, `variant_for_block_width` (`picture.py:30,61,81`),
`image_model`, `path_of` (`scales.py:13,20`). **But it is explicitly not
promised API** (contract §5.2 at `aurora-block-addon-contract.md:307`;
`rendering.py:8`), and the promised `BaseBlockView` has zero image support
(`base.py:77`). Each renderer still re-writes the same three-line glue.
`plone.blicca.heroblock` and the `blicca_block_addon` scaffold do not exist in
this checkout, as the map already assumed.

### What this settles, and what it hands on

- **Ticket 02 (content model):** use two `widget: 'object_browser'`,
  `mode: 'image'` properties — the Teaser `preview_image` idiom — **not**
  `widget: 'image'`. Only `object_browser` survives the sidebar's one-argument
  `onChange`. On-disk shape is a one-element list of
  `{"@id": "../resolveuid/<uid>"}` per image; on the wire, absolute `@id` plus
  `image_scales`.
- **§5.3 transformer: probably not needed.** Stock restapi already injects
  `image_scales` into any nested `@id` dict regardless of field name, and
  strips it on save. **Assert this with a test before relying on it** — no test
  in restapi or the add-on covers the injection for a non-standard field name.
  If it fails, the pair is ~50 lines on the `listing_transform.py` model.
- **Ticket 05 (image delivery):** `variant_for_*` does **not** apply — the hero
  carries no `size` and its `blockWidth` is fixed — so the picture variants must
  be named explicitly per field.
- **Ticket 09 (server half):** `picture_tag` / `image_model` are reusable but
  unpromised; write fresh the explicit variant choice, the
  `aria-hidden="true"` on the `<picture>` (`picture_tag` never emits it and
  always writes `alt`), and the glue.
- **Ticket 08 (editor half):** the hero likely needs a custom edit component
  rendering `BliccaImageWidget` inline — the only path that gives the author
  upload rather than browse-only.

### Not determined

- Whether `@plone/layout`'s `Image` `useRouteLoaderData('root')` resolves under
  the wrapper's MemoryRouter.
- Whether the nested-`@id` injection is exercised anywhere for a non-standard
  field name — no test covers it, which is why the point above says test first.
