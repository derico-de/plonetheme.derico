# How an Aurora block takes an image, and how it reaches the renderer

Findings for [issue 01](../issues/01-research-image-field-and-delivery.md).
Primary sources only: the vendored Aurora packages in
`plone.blicca.auroraeditor/wrapper/node_modules/@plone/`, Blicca's own
wrapper and renderers, the block add-on contract, and the installed
`plone.restapi` / `plone.namedfile` / `Products.CMFPlone` eggs.

Paths are relative to `/workspaces/derico.de/derico.de/sources/` unless they
start with `.venv/`, which is relative to `/workspaces/derico.de/derico.de/`.

**Versions in this checkout** (`wrapper/node_modules/@plone/*/package.json`):
`@plone/blocks` 1.0.0-alpha.11, `@plone/types` 3.0.0-alpha.2,
`@plone/registry` 4.0.0-alpha.1, `@plone/helpers` 2.0.0-alpha.7,
`@plone/plate` 1.0.0-alpha.9, `@plone/components` 5.0.0-alpha.1,
`@plone/cmsui` 1.0.0-alpha.4.

---

## 1. Authoring — what a `blockSchema` image entry looks like

### 1.1 There is no image *field type*, only an image *widget*

`JSONSchema` is a thin structure — there is no field-type vocabulary at all:

```ts
export type JSONSchema = {
  title: string;
  fieldsets: JSONSchemaFieldsets[];
  properties: Record<string, any>;
  required: string[];
};
```

`plone.blicca.auroraeditor/wrapper/node_modules/@plone/types/src/config/Blocks.d.ts:232-237`.
`properties` is `Record<string, any>` — anything goes; what actually selects
behaviour is the `widget` key, resolved through the registry.

Two widget names are relevant, both registered by `@plone/cmsui`:

```ts
config.registerWidget({ key: 'widget', definition: { image: ImageWidget } });
config.registerWidget({ key: 'widget', definition: { object_browser: ObjectBrowserWidget } });
```

`plone.blicca.auroraeditor/wrapper/node_modules/@plone/cmsui/config/widgets.ts:41-56`.
The full shipped widget set is `recurrence, date, datetime, boolean, align,
size, width, image, object_browser, querystring`, plus a `Relation List`
factory and a `plone.app.vocabularies.Catalog` vocabulary mapping and a
default `TextField`
(`.../cmsui/config/widgets.ts:16-68`).

Widget lookup order in the sidebar form is
`getWidgetByFieldId(id ?? name) || …widgetOptions… || getWidgetByName(widget) || …`
(`.../cmsui/components/Form/Field.tsx:169-180`), and `getWidget` scans **every**
registry category for the key
(`.../@plone/registry/dist/index.js:397-406`). Consequence worth knowing: a
schema field literally *named* `image` picks up the image widget even without
a `widget` key. Name the hero's fields something else (`image_wide`,
`image_portrait`) if that is not wanted, or lean on it deliberately.

### 1.2 `@plone/blocks` Image — `widget: 'image'`, a bare string field

```tsx
url: {
  title: 'Image URL',
  widget: 'image',
},
alt: { title: 'Alt text', … },
```

`plone.blicca.auroraeditor/wrapper/node_modules/@plone/blocks/Image/schema.tsx:33-52`
(whole schema `:7-84`; registry entry with `blockSchema: ImageSchema` at
`.../@plone/blocks/Image/index.ts:6-18`).

Note the schema declares **only** `url`. `image_field` and `image_scales`
are *not* schema fields — they are written onto the block data by the edit
component, never authored
(`.../@plone/blocks/Image/ImageBlockEdit.tsx:46-57`).

### 1.3 `@plone/blocks` Teaser — `widget: 'object_browser'` with `mode`

```tsx
href: {
  title: 'Target',
  widget: 'object_browser',
  mode: 'single',
  selectedItemAttrs: ['@id','Title','title','Description','description',
                      'head_title','hasPreviewImage','image_field',
                      'image_scales','@type'],
  allowExternals: true,
},
…
preview_image: {
  title: 'Image override',
  widget: 'object_browser',
  mode: 'image',
  allowExternals: true,
  selectedItemAttrs: ['@id', 'image_field', 'image_scales'],
},
```

`plone.blicca.auroraeditor/wrapper/node_modules/@plone/blocks/Teaser/schema.tsx:23-64`.

So upstream ships **two idioms**: `widget: 'image'` (string URL, used by the
Image block for its one image) and `widget: 'object_browser', mode: 'image'`
(used by the Teaser for its preview-image override). `selectedItemAttrs` is
the declared wish-list of brain metadata the block wants back.

### 1.4 The UI the author gets

**Upstream `@plone/cmsui` ImageWidget** offers all three affordances:
an object-browser button (`.../cmsui/components/ImageWidget/ImageWidget.tsx:387-402`),
a drag-and-drop / file-picker upload that POSTs to `@createContent`
(`:237-301`, `:421-425`), and a link input for an external URL
(`:438-454`). Its `hideLinkPicker` / `hideObjectBrowserPicker` /
`restrictFileUpload` props switch parts off (`:41-55`). On object-browser
selection it forwards **only** `@id` and `title` — no scales
(`:320-330`).

**Blicca substitutes both widgets** after cmsui installs, because Aurora's own
ObjectBrowserWidget calls `useLoaderData` and crashes under the wrapper's
one-route MemoryRouter (ADR 0009):

```ts
config.registerWidget({ key: 'widget', definition: { object_browser: BliccaObjectBrowserWidget } });
config.registerWidget({ key: 'widget', definition: { image: BliccaImageWidget } });
```

`plone.blicca.auroraeditor/wrapper/src/bootstrap/config.ts:35-42` (plus
`factory: 'Relation List'` and the Catalog vocabulary at `:49-56`).

- `BliccaImageWidget` = upload-enabled `pat-contentbrowser` restricted to
  `Image` objects — `<PatternHost mode="single" selectableTypes={['Image']} upload />`
  (`wrapper/src/widgets/ImageWidget.tsx:122-132`). So the author gets
  **content browser + upload**, and **no** free-text external-URL input.
- `BliccaObjectBrowserWidget` = the same pattern host without the type
  restriction and without upload
  (`wrapper/src/widgets/ObjectBrowserWidget.tsx:43-55`).
- `PatternHost` mounts the Mockup pattern imperatively and enriches the
  selected UIDs (`wrapper/src/widgets/pattern-host.tsx:31-44`).

### 1.5 The `onChange` contract differs per host — a real trap

`BliccaImageWidget` calls `onChange(url, {title, image_field, image_scales})`
(`wrapper/src/widgets/ImageWidget.tsx:108-112`), but the **sidebar** form
passes each field a one-argument `onChange(value)`
(`.../cmsui/components/BlockEditor/BlockSettingsForm.tsx:72-82`,
`.../cmsui/components/Form/Field.tsx:190-197`) — the extras are dropped.
Blicca papers over this by patching the selected Plate node directly, but the
patch is hard-coded to `@type === 'image'`:

```ts
const isImagePloneBlock = (node: unknown): node is Record<string, unknown> =>
  Boolean(node && typeof node === 'object' &&
    (node as Record<string, unknown>).type === PLONE_BLOCK_TYPE &&
    (node as Record<string, unknown>)['@type'] === 'image');
```

`wrapper/src/widgets/ImageWidget.tsx:28-34`, used by `patchSelectedImageBlock`
at `:47-72`. For any other `@type` the patch is a silent no-op (harmless, but
it means a hero block using `widget: 'image'` from the sidebar gets **only the
URL string**, never `image_field`/`image_scales`).

`BliccaObjectBrowserWidget`, by contrast, calls `onChange(items)` with the
whole enriched-brain array (`wrapper/src/widgets/ObjectBrowserWidget.tsx:36-41`),
so the sidebar's single-argument `onChange` receives the full objects. **The
object_browser idiom survives the sidebar; the image idiom does not.**

The enriched brain comes from one `@search` round-trip requesting
`UID, image_field, image_scales, hasPreviewImage, head_title` as
`metadata_fields` (`wrapper/src/widgets/enrich.ts:16-45`), typed as:

```ts
export type EnrichedBrain = Record<string, unknown> & {
  '@id': string; '@type'?: string; UID?: string; title?: string;
  description?: string; image_field?: string;
  image_scales?: Record<string, unknown>;
  hasPreviewImage?: boolean; head_title?: string;
};
```

`wrapper/src/widgets/enrich.ts:3-13`.

---

## 2. Stored shape — what lands in the block JSON

### 2.1 The Image block stores a bare `resolveuid` **string**

Blicca deliberately writes `../resolveuid/<UID>` rather than the absolute
`@id`:

```ts
const url = item.UID ? `../resolveuid/${item.UID}` : item['@id'];
```

`wrapper/src/widgets/ImageWidget.tsx:107` — with the rationale in the comment
at `:99-106` (Aurora's `flattenToAppUrl` strips the `/<site>` prefix and 404s
every scale on a Classic backend; a resolveuid URL is prefix-free and restapi
already resolves it on load/save).

Confirmed by the rendering tests, which set the stored block to
`url=f"../resolveuid/{self.image.UID()}"` and assert the rendered HTML
contains `/pic` and **not** `resolveuid`:
`plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/tests/test_rendering_views.py:161-176`.

Not a list. Not an object. A plain string, under key `url`.

### 2.2 The Teaser stores **lists of objects** for `href` and `preview_image`

The edit component writes `href: [selectedTarget]`
(`.../@plone/blocks/Teaser/TeaserBlockEdit.tsx:29-38`) and both view and
renderer defensively unwrap list-or-single:

```ts
const asFirstItem = <T,>(value: T | T[] | undefined): T | undefined =>
  Array.isArray(value) ? value[0] : value;
```

`.../@plone/blocks/Teaser/TeaserBlockView.tsx:9-15`; Python mirror
`_first()` at
`plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/browser/rendering/teaser_block.py:24-28`
("Aurora stores href/preview_image as list-or-single; take the first").

plone.restapi itself normalises a string `href` into a one-element list on
serialisation:

```python
if isinstance(value, str):
    url = value
    value = [{"@id": url}]
```

`.venv/lib/python3.12/site-packages/plone/restapi/serializer/blocks.py:232-234`.

So: **yes, a list even for a single image**, in the object_browser idiom.

### 2.3 What is persisted vs. what is transient

Blocks live flat on the `ploneBlock` void node inside
`blocks.__somersault__.value`; blocks write no serialisation code
(contract §1, `plone.blicca.auroraeditor/docs/design/aurora-block-addon-contract.md:62-63`).
The save PATCH sends `{title, blocks, blocks_layout}` with
`Prefer: return=representation`
(`wrapper/src/save/save-content.ts:60-85`), so restapi's
`BlocksJSONFieldDeserializer` runs on every save
(`.venv/…/plone/restapi/deserializer/blocks.py:37-58`) and
`BlocksJSONFieldSerializer` runs on the way back
(`.venv/…/plone/restapi/serializer/blocks.py:30-51`).

The generic `ResolveUIDDeserializerBase` rewrites `@id` back to
`resolveuid` and **pops `image_scales` from every dict it walks**:

```python
elif data.get("@id", None):
    data = deepcopy(data)
    data["@id"] = path2uid(context=self.context, link=data["@id"])
data.pop("image_scales", None)
```

`.venv/…/plone/restapi/deserializer/blocks.py:89-92`; `fields = ["url", "href",
"preview_image"]` at `:70`; the paired serialiser's field list is identical
(`.venv/…/plone/restapi/serializer/blocks.py:57`). A dedicated
`ImageBlockDeserializer` (`block_type = "image"`) additionally forces
`block["url"] = path2uid(...)` (`.venv/…/plone/restapi/deserializer/blocks.py:143-155`).

**So `image_scales` is never persisted, for any block type, at any nesting
depth — the stock deserialiser already strips it.**

---

## 3. Derived data on the wire

### 3.1 The `image_scales` shape

`image_scales` is a **catalog metadata column**, not a field. The indexer:

```python
@indexer(IDexterityContent)
def image_scales(obj):
    adapter = queryMultiAdapter((obj, getRequest()), IImageScalesAdapter)
    …
    return PersistentMapping(scales)
```

`.venv/lib/python3.12/site-packages/Products/CMFPlone/image_scales/indexer.py:9-22`.
The adapter walks every schema field and keys the result by field name
(`.venv/…/Products/CMFPlone/image_scales/adapters.py:20-33`), and each image
field contributes **a one-element list of dicts**:

```python
return [
    {
        "filename": image.filename,
        "content-type": image.contentType,
        "size": image.getSize(),
        "download": self._scale_view_from_url(url),   # "@@images/image-1200-…"
        "width": width,
        "height": height,
        "scales": scales,                              # {name: {download,width,height}}
    }
]
```

`.venv/lib/python3.12/site-packages/plone/namedfile/adapters.py:68-78`; the
per-scale entries at `:112-116`; the deliberate list-of-one rationale at
`:62-67`; `download` is a **relative** path (`@@images/...`), stripped of the
object URL at `:131-136`.

TypeScript mirror in `@plone/types`:

```ts
export type ImageScale = { download: string; height: number; width: number };
export type Image = {
  'content-type': string;
  base_path?: string;
  download: string;
  filename: string;
  height: number;
  scales: Partial<{ [key: string]: ImageScale; great: …; huge: …; icon: …; large: …;
                    larger: …; mini: …; preview: …; teaser: …; thumb: …; title: … }>;
  size: number;
  width: number;
};
```

`plone.blicca.auroraeditor/wrapper/node_modules/@plone/types/src/content/common.d.ts:47-74`;
containers declare `image_scales: Record<string, Image> | null` at `:26-45`
(the service type at `src/services/common.d.ts:37` says
`Record<string, Array<Image>>`, which matches the Python — the content typing
is loose/wrong upstream).

`base_path` is **not** produced by `plone.namedfile`; it is added by
`plone.volto`'s `PreviewImageScalesFieldAdapter` for the `preview_image_link`
relation, where the scales belong to a *different* object than the item's own
`@id` (`.venv/…/plone/volto/behaviors/preview_link.py:64-80`). Both Aurora's
`Image` component and Blicca's `scales.py` honour it as a base-URL override
(`.../@plone/layout/components/Image/Image.tsx:17-34` and `:91-94`;
`…/rendering/scales.py:44-48`, `…/rendering/picture.py:97-102`).

Companion key `image_field` (the name of the field inside `image_scales`) is
a plain catalog metadata column included in restapi's default summary field
set together with `image_scales`
(`.venv/lib/python3.12/site-packages/plone/volto/summary.py:11-22`).

### 3.2 How it gets *into* the block — no add-on transformer needed today

**Bare string in a `url` / `href` / `preview_image` field.** The generic
`ResolveUIDSerializerBase` resolves the uid and, when a brain came back,
injects `image_scales` into the enclosing dict:

```python
for field in fields:
    if field not in data or not isinstance(data[field], str):
        continue
    newdata[field], brain = resolve_uid(data[field])
    if brain is not None and "image_scales" not in newdata:
        newdata["image_scales"] = json_compatible(
            getattr(brain, "image_scales", None)
        )
…
if newdata.get("image_scales"):
    result["image_scales"] = newdata["image_scales"]
```

`.venv/lib/python3.12/site-packages/plone/restapi/serializer/blocks.py:76-95`;
`fields = ["url", "href", "preview_image"]` at `:57`, plus `"@id"` always,
and `"value"` for `@type: URL` dicts (`:73-75`). `resolve_uid` is at
`.venv/…/plone/restapi/serializer/utils.py:13-46`.

That is exactly how the Image block gets its scales — the block dict itself
is the enclosing dict, so `image_scales` lands **at block level** next to
`url`. Round-trip proof:
`.venv/…/plone/restapi/tests/test_content_get.py:207-244` stores
`{"@type": "image", "url": "../resolveuid/<uid>"}` and reads back
`blocks["123"]["image_scales"]["image"][0]["download"]`.

**Nested dict with `@id`.** The same method recurses into every dict value
(`:85-95`), so a value shaped `{"@id": "../resolveuid/<uid>"}` — or a *list*
of them — gets its `@id` resolved to an absolute URL **and** `image_scales`
injected into that same nested dict, regardless of the field's name. This is
the mechanism that would carry two custom hero image fields for free. It does
**not** add `image_field`; consumers fall back to `"image"` or the first key
(see §3.4).

**Teaser only.** `TeaserBlockSerializerBase` (order 0, `block_type="teaser"`)
goes further and merges the whole `ISerializeToJsonSummary` of the target into
`href[0]`:

```python
serialized_brain = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
…
value[0].update(serialized_brain)
data["href"] = value
```

`.venv/lib/python3.12/site-packages/plone/restapi/serializer/blocks.py:212-255`.
The summary carries `image_field` and `image_scales` because
`plone.volto`'s `JSONSummarySerializerMetadata` puts them in the default
metadata set (`.venv/…/plone/volto/summary.py:11-22`).

**Both the editor and the public renderer see the same enriched data**,
because `@@aurora-edit` inlines `ISerializeToJson(self.context)()`
(`plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/browser/aurora_edit.py:199-212`)
and the public view runs the identical transformer loop:

```python
for block in visit_blocks(context, value):
    new_block = block.copy()
    for handler in iter_block_transform_handlers(
        context, block, IBlockFieldSerializationTransformer
    ):
        new_block = handler(new_block)
```

`…/browser/rendering/serializer.py:21-32`, called from
`…/browser/rendering/blocks_view.py:66-69`.

`ploneBlock` nodes nested in the somersault tree are reached because
restapi's `NestedBlocksVisitor` descends into `__somersault__`'s `value`
(`.venv/lib/python3.12/site-packages/plone/restapi/blocks.py:60-87`) — this is
the ADR-0004 hook the contract's §5.3 relies on.

### 3.3 What contract §5.3 actually demands

> Derived data the block's **editor component** expects at render time (resolved
> uids, image scales, query results) MUST be supplied by an
> `IBlockFieldSerializationTransformer` in the add-on, so editor and public
> renderer see identical data … Every transformer-injected field MUST be
> stripped by a paired `IBlockFieldDeserializationTransformer` — derived data
> is never persisted.

`plone.blicca.auroraeditor/docs/design/aurora-block-addon-contract.md:310-321`
(worked example named there: `listing_transform.py`; register for **both**
`IBlocks` and `IPloneSiteRoot`).

The worked example in full — 4 classes, ~50 lines, `order`/`block_type`
class attributes, serialiser adds `items`, deserialiser pops it:

```python
class ListingBlockSerializerBase:
    order = 200
    block_type = "listing"
    def __call__(self, value):
        …
        value["items"] = json_compatible(items)
        return value

class ListingBlockDeserializerBase:
    order = 200
    block_type = "listing"
    def __call__(self, value):
        value.pop("items", None)
        return value
```

`…/browser/rendering/listing_transform.py:30-82`, registered as four
`<subscriber>` directives in
`…/browser/rendering/configure.zcml:96-111`. Note they adapt
`(IBlocks | IPloneSiteRoot, IPloneBliccaAuroraeditorLayer)` — a **browser
layer**, so the transform only fires on sites with the add-on installed.

### 3.4 What Blicca's renderers already do with it

`picture.py` — the only place `<picture>` markup is built:

```python
def picture_tag(item, variant_name, alt="", css_class=None):
    variant = get_picture_variants().get(variant_name)
    if not variant or not variant.get("sourceset"):
        return None
    image = _first_image(item or {})
    if not image or not image.get("download"):
        return None
    if image.get("content-type") == "image/svg+xml":
        return None
    base = image.get("base_path")
    if not base:
        url = item.get("@id") or item.get("url") or ""
        base = urlparse(url).path or url
    …
    tag = Img2PictureTag().create_picture_tag(
        variant["sourceset"], attributes, lazy=True
    )
```

`…/browser/rendering/picture.py:81-117`; the `image_field` fallback chain
(`image_field` → `"image"` → first key) is `_first_image` at `:72-78`.
It renders through Classic UI's `plone.picture_variants` +
`plone.allowed_sizes` registry records via
`plone.namedfile.picture.Img2PictureTag` — the same machinery behind
TinyMCE's picture markup (`:1-14`, imports at `:18-19`).

Variant selection is **block-shape-driven, not caller-driven**:
`variant_for_image_block(data)` maps the image block's `size` (`l/m/s` →
`large/medium/small`) and upgrades to `fullwidth` for `blockWidth in
("layout","full")` (`picture.py:22-42`); `variant_for_block_width(data,
fallback)` walks a per-width preference ladder for card images that fill
their block (`picture.py:53-69`).

The `fullwidth` variant is installed by this add-on's setup handler (a
JSONField, so no GS syntax):
`plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/setuphandlers.py:13-28`
(shape) and `:50-57` (`ensure_fullwidth_variant`).

`scales.py` — the non-`<picture>` fallback, mirroring `@plone/layout`'s
`Image`: returns `{src, srcset, width, height, alt}`, sorts named scales
ascending by width, honours `base_path`, and makes URLs site-relative
(`…/browser/rendering/scales.py:20-63`; `path_of()` at `:13-17`).

`image_block.py` — 54 lines total: a `picture` property and an `image`
fallback property, feeding
`{"@id": data["url"], "image_field": …, "image_scales": …}` into the helpers
(`…/browser/rendering/image_block.py:22-54`). The template picks picture when
present, plain `<img>` otherwise
(`…/browser/rendering/templates/image_block.pt:1-15`).

`teaser_block.py` — `_image_item()` prefers `preview_image[0]` when it carries
`image_scales` or `download`, else falls back to the `href[0]` target summary
(`…/browser/rendering/teaser_block.py:68-86`); the `image` property mirrors
that with `image_model` (`:88-98`). Template at
`…/browser/rendering/templates/teaser_block.pt:1-30`.

`listing_block.py` — same two properties per item, variant from `blockWidth`
(`…/browser/rendering/listing_block.py:148-169`), items serialised with
`ISerializeToJsonSummary` and `metadata_fields=_all` so `image_scales` /
`image_field` are present (`:88-94`).

---

## 4. Reuse — is there a helper, or does each renderer redo it?

**There is a helper, and all three renderers already use it.** It is not a
base class and not part of the promised API.

- `picture_tag(item, variant_name, alt="", css_class=None)` —
  `…/browser/rendering/picture.py:81`
- `variant_for_image_block(data, variants=None)` — `picture.py:30`
- `variant_for_block_width(data, fallback, variants=None)` — `picture.py:61`
- `image_model(item, image_field=None, alt="")` — `scales.py:20`
- `path_of(url)` — `scales.py:13`

Callers: `image_block.py:25,34`; `teaser_block.py:86,92,97`;
`listing_block.py:151,160,165`. Every one of them re-implements the *same
three lines of glue* (a `picture` property, an `image` property, a
`picture or image` template condition) — the glue is duplicated, the
scale/variant logic is not.

The base class that *is* promised carries no image support at all:

```python
class BaseBlockView(BrowserView):
    """Base for per-block views; the dispatcher fills these before rendering."""
    data = None
    block_type = ""
    def __call__(self):
        return self.index()
```

`…/browser/rendering/base.py:77-84`, re-exported from the stable path
`plone.blicca.auroraeditor.rendering`
(`plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/rendering.py:1-15`).

And the helpers are **explicitly excluded** from the promised surface:

> The wrapper's internal image/picture/scales/listing helpers are **not**
> promised — promoted later on demand.

`plone.blicca.auroraeditor/docs/design/aurora-block-addon-contract.md:307-308`
(§5.2, restated in `rendering.py:7-9`).

`plone.blicca.heroblock`, the reference add-on named by contract §8 as the
dogfooding example for exactly this (image reference + transformer +
deserialiser), **does not exist in this checkout** — `find` across
`/workspaces/derico.de/derico.de` for `*heroblock*` / `*hero*block*`
(excluding `node_modules` and `.venv`) returns nothing. The map for this
block confirms it stays unbuilt
(`plonetheme.derico/.scratch/derico-hero-block/map.md`, "No relationship to
`plone.blicca.heroblock`"). There is likewise **no scaffold**: the
`blicca_block_addon` copier template of §9 was not found in the checkout.

Editor-side there is no reusable image helper either — `@plone/layout`'s
`Image` component
(`.../@plone/layout/components/Image/Image.tsx:45-136`) is the only one, and it
calls `useRouteLoaderData<RootLoader>('root')` at `:57` to read
`plone.allowed_sizes` from the site data. Whether that resolves inside the
wrapper's one-route MemoryRouter was **not determined** from sources; both
upstream blocks use it and Blicca has not replaced it, which is weak evidence
it works (it is only used to decide whether to append an `original` entry to
the srcset, `:98-110`).

---

## What this means for the Derico Hero

**Field type / widget.** There is no image field *type* to choose. Declare two
properties with `widget: 'object_browser', mode: 'image'` — the Teaser's
`preview_image` idiom
(`@plone/blocks/Teaser/schema.tsx:58-64`) — not the Image block's
`widget: 'image'`. Reason: with Blicca's widget substitutions in place, only
the object_browser path survives the sidebar's one-argument `onChange`
(§1.5); `widget: 'image'` in a sidebar would store a URL string with no
`image_field`/`image_scales`, and `patchSelectedImageBlock` will not rescue a
non-`image` `@type` (`wrapper/src/widgets/ImageWidget.tsx:28-34`). Add
`selectedItemAttrs: ['@id', 'image_field', 'image_scales']` for contract
fidelity even though `BliccaObjectBrowserWidget` ignores it and always fetches
the full set (`wrapper/src/widgets/ObjectBrowserWidget.tsx:9-14`).

Trade-off to decide in ticket 02: `BliccaObjectBrowserWidget` has **no upload**
(`ObjectBrowserWidget.tsx:43-55`), while `BliccaImageWidget` does but is
`Image`-type-restricted **and** carries the `@type === 'image'` sidebar patch.
If hero authors must be able to upload from the block, the options are (a) a
custom edit component that renders `BliccaImageWidget` inline and writes the
full patch itself, the way `ImageBlockEdit` does
(`@plone/blocks/Image/ImageBlockEdit.tsx:37-58`), or (b) a small hero-local
widget wrapping `PatternHost` with `upload selectableTypes={['Image']}`. Given
"brand blocks are deliberately inflexible" and the block needs a bespoke
canvas anyway (rings, legend), (a) is the natural shape.

**Stored JSON.** Expect, on the `ploneBlock` node inside
`blocks.__somersault__.value`:

```json
{
  "type": "ploneBlock",
  "@type": "derico_hero",
  "image_wide":     [{ "@id": "../resolveuid/<uid>", "image_field": "image", … }],
  "image_portrait": [{ "@id": "../resolveuid/<uid>", "image_field": "image", … }],
  "kicker": "…", "headline": "…", "lede": "…",
  "legend": [{ "title": "…", "subtitle": "…" }, …]
}
```

A list of one object per image, `@id` in `resolveuid` form on disk, absolute
URL plus `image_scales` on the wire. Persisting a single dict instead of a
one-element list also works (`_process_data` recurses into dicts either way) —
but the list matches every upstream precedent and Blicca's `_first()` helpers.
Note that whatever extra keys the enriched brain carried (`UID`, `title`,
`review_state`, `image_field`) are persisted too unless the hero's edit
component trims the selection down to `{'@id': …}` before `setBlock` — the
same wart the Teaser has. Trimming to `@id` alone is cleaner and costs
nothing, because `image_field` is re-derived (§3.4 `_first_image`).

**Transformer: probably not needed — verify, then decide.** With the
list-of-`{@id}` shape, stock `plone.restapi` already does the whole §5.3 job
for arbitrary field names: `ResolveUIDSerializerBase._process_data` injects
`image_scales` into any nested dict whose `@id` resolves
(`.venv/…/plone/restapi/serializer/blocks.py:76-95`) and
`ResolveUIDDeserializerBase._process_data` pops `image_scales` from every dict
and rewrites `@id` back to `resolveuid`
(`.venv/…/plone/restapi/deserializer/blocks.py:86-96`). I read this from the
source but did **not** execute it against a hero-shaped block — ticket 09
should assert it with a test modelled on
`tests/test_rendering_views.py:161-176` before concluding no transformer is
needed. If it does not hold (e.g. because the hero stores strings, or a
different key name is chosen), write the transformer pair on the
`listing_transform.py` model: `order`/`block_type = "derico_hero"`, four
classes adapting `(IBlocks, <layer>)` and `(IPloneSiteRoot, <layer>)`,
serialiser adding `image_scales` (and optionally `image_field`) per image
field, deserialiser popping exactly those keys
(`…/browser/rendering/listing_transform.py:30-82`,
`…/browser/rendering/configure.zcml:96-111`).

**Reuse vs. fresh.** `picture_tag` + `variant_for_*` + `image_model` +
`path_of` do everything the server half needs and each hero image is just
`picture_tag(item, variant, alt="")` — but they are **not** promised API
(contract §5.2, `…/rendering.py:7-9`), so importing them from
`plone.blicca.auroraeditor.browser.rendering.picture` is an unpromised
dependency the hero would take knowingly, or the hero copies ~40 lines. Since
the map already fixes the hero in `plonetheme.derico` while the gate lands in
`plone.blicca.auroraeditor` (ticket 03), promoting `picture_tag` /
`variant_for_*` into the promised `plone.blicca.auroraeditor.rendering`
surface is a cheap contract amendment worth raising in ticket 03 alongside the
single-ecosystem exemption — this is precisely the "promoted later on demand"
case §5.2 anticipates.

Only `BaseBlockView` is promised today, and it offers nothing image-related.
The variant helpers are shape-driven (`size`, `blockWidth`) and the hero has
**neither** — brand blocks expose no width control — so the hero must name its
variants explicitly rather than call `variant_for_image_block`. Expect
`fullwidth` for the wide crop (installed by
`setuphandlers.py:50-57`, `sizes: "(min-width: 1600px) 1600px, 98vw"` at
`:25`) and a narrower stock variant for the portrait; ticket 05 owns that
choice, and may need a hero-specific variant registered the same way.

**Alt text.** The map fixes "no image alt" (the `<picture>` is
`aria-hidden="true"`). `picture_tag` always writes `alt` (defaulting to `""`,
`picture.py:103`) and never emits `aria-hidden`, so the hero template must add
that attribute itself — `picture_tag` returns an HTML **string**, so either
post-process it or render the `<picture>` in the hero's own template.

---

## Things I could not determine from sources

- Whether `useRouteLoaderData<RootLoader>('root')` in `@plone/layout`'s
  `Image` (`.../@plone/layout/components/Image/Image.tsx:57`) resolves under
  the wrapper's one-route MemoryRouter. Nothing in
  `plone.blicca.auroraeditor/wrapper/src/` overrides it, and the upstream
  blocks use it — but ADR 0009 replaced the *other* loader-data consumer
  (ObjectBrowserWidget) for exactly this reason, so it is worth a runtime check.
- Whether the nested-dict `image_scales` injection actually fires for a
  **non-standard field name** on a `ploneBlock` node inside the somersault
  tree. The code path reads as unconditional (§3.2), but no test in
  `plone.restapi` or in
  `plone.blicca.auroraeditor/src/plone/blicca/auroraeditor/tests/` covers a
  custom field name — I searched
  `grep -rn "image_scales" src/ --include=*.py` in the add-on (only the
  renderers matched) and the restapi test modules (`test_blocks_serializer.py`,
  `test_blocks_deserializer.py`, `test_content_get.py` — image block and
  teaser only).
- `plone.blicca.heroblock` and the `blicca_block_addon` copier template
  (contract §8/§9) are referenced but absent from this checkout; searched
  `find /workspaces/derico.de/derico.de -iname "*heroblock*" -o -iname
  "*hero*block*"` excluding `node_modules`/`.venv` — no hits. There is
  therefore **no worked image-block add-on to copy**; the closest models are
  `listing_transform.py` (transformer pair) and `image_block.py` (renderer).
