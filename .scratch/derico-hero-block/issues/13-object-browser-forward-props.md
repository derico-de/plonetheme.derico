# Build: Blicca's object browser forwards selectableTypes and upload

Type: task
Status: open
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
