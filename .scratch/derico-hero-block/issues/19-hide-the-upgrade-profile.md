# Build: hide the theme's upgrade profile from the add-ons control panel

Type: task
Status: resolved
Assignee: md@derico.de
Blocked by: —

## Question

`plonetheme.derico.upgrades:1001` is registered as an EXTENSION profile, and
nothing hides it — so the add-ons control panel lists **`plonetheme.derico.upgrades`**
as an installable add-on next to the theme itself. Found by
[ticket 10](10-verify-end-to-end.md) while checking the install on the sandbox
site (`GET /@addons`).

An upgrade profile is applied by its `genericsetup:upgradeDepends` step, never
by hand; offering it in the control panel invites an administrator to apply a
migration out of order.

`HiddenProfiles` in `setuphandlers.py` already exists and lists
`plonetheme.derico:uninstall` — the upgrade profile has to be added to it.
Both sibling packages do exactly this and are the precedent:

- `plone.blicca.auroraeditor` hides `…auroraeditor.upgrades:1001`
- `plonetheme.clara` hides `…clara.upgrades:1001` … `:1004`

No profile XML changes, so no upgrade step of its own. Worth a test that
scales: assert every registered `plonetheme.derico.upgrades:*` profile is
hidden, so the next `plonecli add upgrade_step` cannot reintroduce the gap
silently.

## Answer

**Built; the ticket's instruction held, and the interesting decision was the
one it did not ask about — whether to hide the *product* as well.**

The change is two lines in `setuphandlers.py`:
`HiddenProfiles.getNonInstallableProfiles` now returns
`plonetheme.derico.upgrades:1001` alongside `plonetheme.derico:uninstall`.
Blicca's precedent exactly.

### The mechanism, read rather than assumed

Both surfaces build the list identically, and the ticket's `GET /@addons`
finding and the control panel are the same defect, not two:
`ManageProductsView.marshall_addons`
(`Products/CMFPlone/controlpanel/browser/quickinstaller.py:356`) and
`plone.restapi`'s `Addons.marshall_addons`
(`plone/restapi/services/addons/addons.py:379`) both walk
`portal_setup.listProfileInfo()`, keep only `EXTENSION`, and skip a profile
when **either** its own id is in the hidden-profiles union **or** its
`product` is in the hidden-products union. So the profile is offered for
exactly the reason the ticket said, and either list would suppress it.

That "either" is what made the ticket's one line a choice.

### Rejected: the `getNonInstallableProducts` blanket

Clara declares **both** — the product `plonetheme.clara.upgrades` *and* each
of `:1001`…`:1004`. Blicca declares only the profile. The ticket cited both
as precedent without noting they differ, so it had to be settled here.

The product line is the tempting one: it hides upgrade profiles nobody has
written yet, so the gap could never reopen at all, which sounds like exactly
the "cannot reintroduce it silently" the ticket asked for. It was **measured
and rejected**, on this map's own ticket 11 rule — *two ways to say one
answer is the drift, not the safety*:

- **It is unfalsifiable by the suite.** Mutation-checked: with the product
  line removed and the profile line kept, both new tests stay green
  (2 passed). Production code no guard exercises is what ticket 08 retired
  `--derico-text-display` for.
- **It blunts the other test.** The mirror mutation — product line kept,
  profile line removed — leaves the *effect* test green and only the
  enumeration red (1 failed, 1 passed). So with the blanket in place, a
  `HiddenProfiles` that had quietly stopped naming any profile still reads
  green on the test that models what the user sees. The blanket buys
  belt-and-braces at the cost of making one of the two tests unable to see
  the belt.
- **What it actually buys is the gap between committing a new upgrade step
  and CI running.** That is what the enumeration is for.

Verified safe *before* rejecting it, so the rejection is a preference between
two working options and not a dodge: `UpgradeDepends.doStep` calls
`portal_setup.runAllImportStepsFromProfile` directly
(`Products/GenericSetup/upgrade.py:210`), never the installer, so hiding the
product would not have disturbed the upgrade — which is why Clara has run
this way across four upgrade profiles.

### Acceptance: two tests, different jobs

In `tests/test_setup.py`, class `TestUpgradeProfilesHidden`. Both were
confirmed **red against the pre-fix code** (2 failed) before the fix went in.

- `test_upgrades_are_not_offered_as_an_addon` — **the effect**, read off
  `ManageProductsView.marshall_addons()` itself rather than a reimplementation
  of its filter. Asserts `plonetheme.derico.upgrades` is absent **and**
  `plonetheme.derico` is still present, so the guard is narrow rather than a
  blanket that took the theme with it.
- `test_every_upgrade_profile_is_hidden` — **the mechanism, enumerated**.
  Reads the registered `EXTENSION` profiles whose `product` is
  `plonetheme.derico.upgrades` out of `portal_setup.listProfileInfo()` and
  asserts each is in the hidden union. This is the scaling property the
  ticket asked for: a future `1002` with no `HiddenProfiles` line turns it
  red. It carries an explicit **non-vacuity assertion** — an empty
  enumeration fails with a message saying so, because a test that scales on a
  list is worthless the day the list is empty (ticket 14 §9's "a guard that
  always skips protects nothing", in its other form).

No profile XML changed, so **no upgrade step** — confirmed, not assumed: the
change is Python read at ZCML-registration time by a utility, with no
registry value and no profile version behind it. A running instance needs a
Zope restart to pick it up, nothing more.

228 passed across the package; `ruff check .` clean. CHANGELOG entry added.
