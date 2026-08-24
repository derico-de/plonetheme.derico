# Decide and build: the admin-only insert gate in plone.blicca.auroraeditor

Type: task
Status: closed
Blocked by: —

## Question

Brand blocks must be insertable by site administrators only. The mechanism was
settled at charting; this ticket decides the details and lands the code in
`plone.blicca.auroraeditor`.

The shape: `@@aurora-edit` loads the bundle for **everyone** — so an ordinary
editor opening a page containing a hero sees the rendered block, not an
unknown-block placeholder — and the slash menu is filtered per user instead.

Aurora's own `restricted` (`@plone/plate/components/editor/plugins/slash-menu.tsx:66`)
is a static boolean and cannot express this; the seam that can is
`SlashMenuConfig.extendGroups`, which the wrapper already uses at
`wrapper/src/editor/plugin-kit.tsx:73`.

Decide and implement:

- **The record field.** A `permission` field on `IAuroraBlockAddon`
  (`src/plone/blicca/auroraeditor/interfaces.py`). Default value, and what an
  empty value means — presumably unrestricted, so every existing record keeps
  working. Which permission does a brand block declare?
- **The verdict's path to the client.** `blockaddons.py` currently filters
  add-ons out of `blockAddons` entirely. Here the add-on must load *and* carry a
  per-user "insertable" verdict — extend the `{name, url}` mount option, or send
  a separate list of non-insertable `@type`s? `AddonStatus` gains a field either
  way, and `types` stops being diagnostics-only for this one purpose.
- **The filter.** Extend the existing `extendGroups` to drop
  `block_<@type>` items the user may not insert, without disturbing the
  void-insert focus fix wrapped around every item there.
- **Diagnostics.** The gate should be visible on the blockaddon diagnostics view
  alongside the enabled / resolvable / compatible verdicts.
- **Is this a `block_api` bump?** The mount-option surface changes. 1.1 → 1.2 if
  the option shape grows; confirm against contract §2.2's rules.
- **Tests.** A permitted and a denied user, against the `tests/helloaddon`
  fixture.

Also amend the spec in the same change: contract §3.2/§4 for the new field and
filter, and §1.1 for the **single-ecosystem exemption** — brand blocks are built
locally for one brand and never published to npm. ADR 0013 gets a note if the
amendment changes its consequences.

Non-negotiable: this is insert-gating, not security. The block stays authorable
through the API, so `@@aurora-block-*` renderers must not assume privilege.

---

**Release companion:** [ticket 13](13-object-browser-forward-props.md) is the
other `plone.blicca.auroraeditor` change this effort needs (the object browser
forwarding `selectableTypes` / `upload`). Separate ticket, same release — 08
blocks on 13 and must not thereby block on this gate.

Ticket 02 also confirmed the hero's `@type` is **`derico-hero`**, which is what
this gate's permission check and slash-menu filter must key on.

---

## Answer

Built and landed in `plone.blicca.auroraeditor`. Blicca stays
permission-agnostic: it provides the mechanism and defines no permission.

**The grounds (the ticket's unstated blocker).** Contract §7 said site-side
curation was "none in v1" and that Blicca adopts permission-gating "when
Aurora implements it, **never ahead**". That was resolved *against* the
literal rule and *with* ADR 0008: the filter runs on
`SlashMenuConfig.extendGroups` — Aurora's own seam, already the wrapper's
curation layer (it drops the Actions group and rewrites every Blocks item) —
so it removes items rather than adding capability, which is the **subtractive
curation** ADR 0008 sanctions. The mirror ceiling is untouched and ADR 0008 is
unamended. One thing is genuinely new and is written down rather than glossed:
the two sanctioned subtractions are static and site-wide, this one is
**per-user and dynamic**, so the menu is now a function of the viewer.

**The mechanism.**

- `permission` on `IAuroraBlockAddon` — optional, empty/absent = unrestricted,
  so every existing record keeps working. It holds a permission **title**
  (`Manage portal`), not a ZCML id; an id is an unregistered permission, which
  AccessControl resolves to Manager-only.
- The verdict travels as **`restrictedBlockTypes: [...]`**, a derived list of
  `@type`s — *not* a per-record `insertable` flag. The wrapper filters items
  keyed `block_<@type>`, so shipping the derived list keeps `types` resolution
  server-side and never implies the wrapper should dispatch on it.
- Evaluated against **the object being edited**, not the portal root, because
  permissions acquire down the tree (test:
  `test_gate_is_evaluated_against_the_edited_object`).
- The wrapper filter is a module-level mutable set with a
  `setRestrictedBlockTypes()` setter, mirroring the existing
  `setFloatingToolbarButtons` precedent: `bliccaSlashKit` is built at module
  evaluation while the verdict arrives per-mount. Filter runs **before** the
  per-item void-insert focus wrap, which is left undisturbed.
- **Not a block-api bump.** Host stays **1.1**. §2.2's counter covers the
  shared-module facade surface that add-on *bundles* import; this touches only
  the mount contract, which only the wrapper reads.

**Two properties that are deliberate, not incidental.** The bundle loads for
**everyone** — only the menu entry is withheld, so an ordinary editor opening
a page containing a hero sees it rendered, not an unknown-block placeholder.
And the gate **fails open**: it is expressed through the record's `types`, so
a record omitting them keeps its blocks insertable. Guidance must not let a
packaging slip strip an admin of their own tools. Insert-gating is not
security either way — the block stays authorable through the API.

**Diagnostics.** Two columns: the declared permission and the roles currently
holding it. The view is itself `cmf.ManagePortal`-gated, so its reader is
always a Manager and "can *you* insert this?" would read as a permanent yes;
naming the holders answers the question an admin actually has.

**Spec amendments** (same change): §1.1 gained the **single-ecosystem
exemption** as a general **brand block** category — publication only; `edit`,
`view`, the canonical build and the server renderer all still bind. §3.2
gained the `permission` row and `types` became "diagnostics **and**
insert-gating; never dispatch". §4 gained the mount option and the
no-bump rationale. §7's forbidding bullet was replaced. §10's "waits for
Aurora" open item became "contributing the gate upstream". ADR 0013 carries a
"Later addition" note; **ADR 0008 was not touched**. Blicca's `docs/CONTEXT.md`
gained **brand block** and **insert gate** (the latter recorded as a third
subtraction kind alongside the two existing ones). News: `42.feature`,
`43.feature`.

**Tests** — `TestInsertGate` in `test_block_addons.py`, 10 cases against the
`helloaddon` fixture: permitted user, denied user (an ordinary **Editor**, the
case the gate exists for — a user who cannot edit never reaches the menu),
bundle-still-loads-when-denied, no-permission-is-unrestricted, fails-open on
missing `types`, skipped add-on contributes nothing, acquisition, and both
diagnostics columns. Full suite **182 passed**; wrapper typecheck clean in the
changed files (its pre-existing failures are in `node_modules` and
`portal-scope.ts`); artifacts rebuilt and committed; `block-api.json` still
`1.1`. One new ruff `BLE001`, matching the module's three existing
unsuppressed broad catches and its documented fail-soft posture.

**Handed to ticket 09** (amended there): defining and granting
`plonetheme.derico: Insert Brand Block` in the theme's `permissions.zcml` +
`rolemap.xml`, with an upgrade step, and setting it as the record's
`permission`. `cmf.ManagePortal` was rejected — its title is Manager-only in
stock Plone, and the destination says *site administrator*.

**Not done here:** the §1.1 exemption is written into the contract, but no
brand block exists yet to exercise it — that is tickets 08/09.
