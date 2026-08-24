# Build: the Derico Hero's server half

Type: task
Status: open
Blocked by: 02, 05, 06, 11, 12

## Question

The public rendering and the Plone packaging, in `plonetheme.derico`.

- `@@aurora-block-<@type>` browser page — `for="*"`, `zope2.View`, on the
  theme's own browser layer, over the contract's public `BaseBlockView`
  (contract §5.1/§5.2). The rings SVG is static markup in its template.
- The restapi serialisation transformer and its paired stripping deserialiser
  for whatever derived image data 01 turns up (contract §5.3).
- `profiles/default/registry.xml`: the `IAuroraBlockAddon` record(s) per 04's
  shape, plus 05's picture variants — with the upgrade step.
- Uninstall profile kept in step, matching how the theme already removes its
  bundle records.
- Fail-soft error placeholder in production, loud in development (§5.4).
- The renderer assumes no privilege — the insert gate is guidance, not security.
- **`permissions.zcml` + `profiles/default/rolemap.xml`: define and grant
  `plonetheme.derico: Insert Brand Block`** (Manager + Site Administrator),
  and set it as the record's `permission` value in `registry.xml`. Surfaced by
  [ticket 03](03-permission-gate.md), which built the gate but deliberately
  left Blicca permission-agnostic. `cmf.ManagePortal` will NOT do: its title
  is held by Manager alone in stock Plone, and the destination says *site
  administrator*. `rolemap.xml` is shipped profile XML, so this gets an
  upgrade step narrowed to `rolemap`.
