# Build: hide the theme's upgrade profile from the add-ons control panel

Type: task
Status: open
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
