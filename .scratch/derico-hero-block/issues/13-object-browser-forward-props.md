# Build: Blicca's object browser forwards selectableTypes and upload

Type: task
Status: closed
Assignee: md@derico.de
Blocked by: —

## Question

`BliccaObjectBrowserWidget` accepts four props and forwards `fieldId`, `mode`,
`initialPath`, `onSelection` to `PatternHost`
(`wrapper/src/widgets/ObjectBrowserWidget.tsx:44-52`). `PatternHost` already
supports **`selectableTypes`** and **`upload`** and passes them to
pat-contentbrowser (`wrapper/src/widgets/pattern-host.tsx:24-25, 92-95`) — they
are simply never handed down.

Two consequences for any block picking an image through the sidebar:

- **No type restriction.** `mode: 'image'` is not a mode Blicca implements; it
  falls through and merely reads as "not multiple", i.e.
  `maximumSelectionSize: 1` (`pattern-host.tsx:91`). An author can select a News
  Item for an image field.
- **No upload.** The image must already exist in the site; authoring a hero
  means leaving the editor, uploading, and coming back.

A block bundle cannot fix this for itself: the import map exposes only `react`,
`platejs`, `jotai` and `@plone/registry` (`aurora_edit.pt:38`), so `PatternHost`
is unreachable from an add-on.

Forward both props. The sidebar already carries arbitrary schema keys through to
the widget as props (`cmsui/components/Form/Field.tsx:181-186`) — that is how
`selectedItemAttrs` arrives — so a block declares them in its `blockSchema` and
nothing else has to change.

Decided on [ticket 02](02-content-model.md): the Derico Hero's two image fields
declare `selectableTypes: ['Image'], upload: true`, and block 08 until this
lands.

Ships in the same `plone.blicca.auroraeditor` release as
[ticket 03](03-permission-gate.md). Kept separate from 03 because 08 depends on
this and must not thereby depend on the permission gate. No GS profile XML
changes, so no upgrade step for this one on its own.

## Answer

**Built in Blicca — but not through the props the ticket named.** The
capability is exactly as scoped; the *shape* was wrong, and the correction is
the whole finding.

### The channel is Aurora's, not a new Blicca prop

The ticket proposed top-level `selectableTypes` / `upload` schema keys,
forwarded as top-level widget props. Aurora already has a shape for this:
`UseObjectBrowserConfig.widgetOptions.pattern_options`, from which its own
object browser reads `selectableTypes` (and `maximumSelectionSize`) in
`isSelectable` — `cmsui/components/ObjectBrowserWidget/utils.ts:95-105` — and
which its ImageWidget uses to restrict its own picker to `Image`
(`ImageWidget.tsx:391-398`). The envelope is not Aurora's invention either:
**`plone.restapi` already serializes relation fields with
`widgetOptions.pattern_options`** carrying pat-contentbrowser option names
verbatim (`recentlyUsed` in its own `types_document` fixture), and
`widgetOptions` is a declared key of cmsui's `BaseFieldProps`, so the sidebar
carries it through untouched.

Inventing a second, Blicca-only spelling for a thing Aurora already spells
would have broken the mirror rule twice over: a hero schema written that way
would silently lose its restriction the day this substitution is dropped for
Aurora's own widget, and Blicca would own a key nobody upstream honours. So
the widget reads `props.widgetOptions?.pattern_options` and forwards
`selectableTypes` and `upload` from there. A schema field becomes:

```ts
image_wide: {
  title: 'Wide image', widget: 'object_browser', mode: 'single',
  widgetOptions: { pattern_options: { selectableTypes: ['Image'], upload: true } },
}
```

Ticket 02's snippet is corrected in place.

`upload` has **no** Aurora counterpart — Aurora's ImageWidget owns upload
itself (drag-drop and URL, `restrictFileUpload`/`hideObjectBrowserPicker`)
rather than asking the browser for it — but it is a pat-contentbrowser option
and Aurora leaves the bag open (`PatternOptions & Record<string, any>`), so it
rides the same envelope. Under Aurora's own widget it would simply be ignored,
degrading to browse-only: the right failure.

### Deliberately only two keys

`PatternHost` computes `vocabularyUrl`, `rootPath`, `basePath`,
`contextPath`, `separator` and `maximumSelectionSize` from the mount options
and the field's `mode`; none of those may be steered from a schema, so the bag
is **not** splatted into the pattern. `maximumSelectionSize` is the one
plausible third key (Aurora honours it in multiple mode) and is **not**
forwarded — `mode` already decides it here, and two ways to say one thing is
the drift ticket 11 rejected. Noted, not built.

### Two of the ticket's other premises

- **`mode: 'image'` is not a Blicca gap.** `ObjectBrowserWidgetMode` is
  `'multiple' | 'single'` in Aurora too (`utils.ts:22`), yet Aurora's own
  schemas ship `mode: 'image'` (Teaser `preview_image`) and `mode: 'link'`
  (Image `href`). Both are Volto-era values **nothing in the stack
  implements** — they read as "not multiple". Recorded in contract §1.5 so a
  block author writes `single` and says what they mean with `selectableTypes`.
  Aurora's own teaser image override is therefore unrestricted upstream as
  well; not this map's to fix.
- **"A block bundle cannot fix this for itself" holds.** The import map
  exposes `react`, `platejs`, `jotai`, `@plone/registry` only, so `PatternHost`
  is out of an add-on's reach. Confirmed, and it is why this had to be a host
  change.

### What shipped (plone.blicca.auroraeditor)

- `wrapper/src/widgets/ObjectBrowserWidget.tsx` — the `widgetOptions`
  prop and the two-key forward; rebuilt `static/aurora-remote.js`.
- **Contract §1.5** "Restricting an `object_browser` field, and offering an
  upload" — the author-facing shape, the two honoured keys, the dead `mode`
  values, and the note that this is **not** a `block_api` bump: §2.2 covers the
  shared-module facades alone, so like the promised Python API (§5.2) this is
  versioned by the distribution. Host stays **1.1**, as with ticket 03.
- `news/46.feature`.
- The fixture add-on's block schema (`tests/helloaddon/static/hello-block.js`)
  gained a `picked` object_browser field declaring the envelope, purely as the
  e2e's target.
- `e2e/object-browser-pattern-options.e2e.js` + its README entry.

### How it is pinned

The test records the options object **pat-contentbrowser is constructed
with**, by pre-creating `window.__patternslib_registry` as a Proxy —
patternslib only creates it when undefined (`core/registry.js:49`), so it
adopts the recorder — and wrapping the `contentbrowser` class as it registers.
Three cases:

1. **The registered widget, straight from the registry** — imports the host
   facades *by URL* (`++plone++auroraeditor/shared/*.js`, located from the
   page's own resource entries) rather than by bare specifier, because the
   import map is emitted **only when an add-on survived filtering**; the
   facades re-export from the remote's chunks, so the URL import is the same
   singleton the mounted editor holds. Renders the shipped
   `object_browser` with the envelope and asserts the pattern got
   `selectableTypes: ['Image'], upload: true`. **Needs no fixture add-on.**
2. **The negative case** — Aurora's teaser `href` declares no
   `pattern_options`, so it must still mount unrestricted and non-uploading.
   Guards against this becoming a global default.
3. **The full path** — the hello fixture's `picked` field through the real
   sidebar. Needs the fixture add-on's ZCML, like `block-addon.e2e.js`.

**Run against the sandbox (Plone 8081, mockup dev server 8000): 1 and 2 pass,
and 1 was confirmed RED first** — reverting the widget and rebuilding gives
`{"selectableTypes":[],"upload":false}`, restoring it gives
`{"selectableTypes":["Image"],"upload":true}`. Case 3 could not run here: the
instance does not load `plone.blicca.auroraeditor.tests.helloaddon`, the same
limitation `block-addon.e2e.js` already carries. Blicca's 202 Python tests
still pass.

### For ticket 08

Declare the two image fields with the `widgetOptions.pattern_options`
envelope, not top-level keys. Second: **`allowExternals` is inert** — ticket
02's `cta_href` / `link_href` declare it, but no consumer exists in Aurora's
object browser or Blicca's, so it is a third dead Volto-era key alongside
`mode: 'image'` / `mode: 'link'`. Harmless (the hero's links are content picks
by design, per the map's fixed constraints) but it must not be mistaken for a
working escape hatch to an external URL. Drop it or keep it as documentation;
either way it does nothing. 08 is unblocked on this point. The changes are
**uncommitted** in `plone.blicca.auroraeditor`, alongside tickets 11/12's
work; they ship in the same release as ticket 03, as planned.
