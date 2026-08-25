# Build: the token-layer changes the hero needs

Type: task
Status: closed
Assignee: md@derico.de
Blocked by: —

## Question

Neither half of the block: three edits to `plonetheme.derico`'s own token layer
that both halves depend on, decided by
[ticket 06](06-css-and-full-bleed.md).

- **Re-publish Clara's private type tokens.** `derico.css` gains
  `--derico-text-display`, `--derico-text-lede`, `--derico-text-label` and
  `--derico-font-display`, each `var()`-ing the corresponding `--clara-*`.
  These have no `--plone-*` equivalent, and `derico.css` is the one place in
  the theme allowed to name a `--clara-*` token. The block sheet then speaks
  only `--derico-*` and `--plone-*`.
- **The chrome-suppression rule.** When the hero is the first block on a
  blocks-view page, hide `.element-breadcrumbs`, `.element-contentheader` and
  `.element-byline`/`#section-byline` so the hero sits flush under Clara's
  header — mirroring Clara's own `body:has(.clara-home)` treatment. Public
  view only. It cannot live in the block's stylesheet: `scope-wrap.ts:41`
  rewrites `body` to `:where(:scope)`.
- **Widen, don't delete, the minimality tests.**
  `tests/test_override_minimality.py` encodes "this sheet is `:root` and
  nothing else", which the chrome rule breaks.
  `test_sheet_declares_only_root_level_selectors` and
  `test_sheet_declares_nothing_but_custom_properties` get an explicit
  allow-list entry for the chrome selector, so they still fail on any *other*
  component rule; `test_every_derico_token_is_used` grows its corpus to
  include the block stylesheets, or the four new aliases read as
  declared-but-unused. The guard's intent must survive all three edits.

No GenericSetup profile XML changes here — `derico.css` ships through the
bundle record that already exists, so no upgrade step. Confirm that before
closing.

## Answer

All three edits landed; the theme's own suite is **103 passed, 2 skipped**
(the two skips are the block-sheet guards, which have nothing to run against
until ticket 08 builds the first sheet). Nothing here changed a decision — but
two things the ticket asked to *confirm* turned out to have mechanisms worth
writing down, and one guard is stricter than "allow-list the selector".

### 1. The four aliases — `derico.css` §3

`--derico-text-display`, `--derico-text-lede`, `--derico-text-label`,
`--derico-font-display`, each a bare `var(--clara-*)`. All four targets verified
present in the shipped `clara.min.css`. They sit immediately after §2 (the
`derico → Clara` re-pointing) because they are the *other direction of the same
seam*; the following sections renumbered, and §7 is new.

**They are aliases, not values, and a test now says so.** A value would fork
Clara's type scale silently — and the scale is the single largest thing the
theme deliberately inherits (the header lists it first). `test_published_-`
`aliases_are_aliases_of_claras_own_tokens` requires the declaration to match
`var(--clara-*)` verbatim, and a `@needs_clara` companion checks the target
still exists. Mutating one alias into the literal `clamp()` it currently
resolves to fails both.

### 2. The chrome rule — `derico.css` §7

The selector is 06 §1's verbatim, and 07's correction holds: Aurora stamps
`block-<@type>` on the **wrapper** on both surfaces, so `.block-derico-hero` is
free for exactly this. Confirmed against the markup rather than assumed —
`blocks_view.pt` renders the blocks directly inside `.aurora-blocks-view`, and
`plate.py:_render_sequence` **skips the title node entirely** (`continue`,
emitting nothing) rather than emitting an empty wrapper, so a hero authored
second in the tree is genuinely the first *rendered* child and `:first-child`
matches.

**"No gap is added" is now measured, not hoped.** Every bit of vertical space
above the first block lives on the three hidden elements themselves —
`.element-breadcrumbs { padding-block: var(--plone-space-s) 0 }`,
`.element-contentheader { padding-block: var(--plone-space-xl) var(--plone-space-m) }`
— and Clara sets `--plone-layout-space: 0` on `.plone-layout`, so its row-gap
contributes nothing once the two are out of the grid. `.element-body` carries
`padding-block-end` only, and `.aurora-blocks-view` carries `padding-inline`
only. So the three `display: none` declarations *are* the whole of "flush", and
Clara's companion `body:has(.clara-home) .element-body { padding-block-end: 0 }`
is deliberately **not** mirrored: that one exists because the homepage *ends* in
a full-bleed band, and the hero opens the page rather than closing it.

`.element-byline` is aspirational and `#section-byline` is the live hook (Clara
says so in `_clara-components.scss`); both are listed because Clara lists both,
and on the blocks-view path the byline viewlet may not render at all.

### 3. The tests were widened — and the exception was pinned, not just allowed

An allow-listed selector would have let the exception grow into a real component
rule. So the guard is structural and narrow:

- `_is_chrome_suppression()` matches a selector only when **every** comma-part
  is `CHROME_PREFIX` + one of the four named chrome hooks. Reformatting the
  sheet cannot break it; a different rule cannot slip past it.
- `test_sheet_declares_nothing_but_custom_properties` no longer merely skips
  the rule — it asserts its body is **exactly `display: none`**. Adding
  `margin-block: 2rem` to it fails.
- `test_the_chrome_rule_is_present_and_stays_narrow` asserts there is exactly
  **one** such rule, and asserts `.aurora-blocks-view` and `:first-child` are
  in `CHROME_PREFIX` **itself** rather than in the matched selector — the
  latter would be circular, since nothing reaches the assertion unless the
  prefix already matched. Widening the guard is now a conscious deletion.
- `test_every_derico_token_is_used` reads a corpus of `derico.css` **plus**
  `static-blocks/*.css`, via a new `css_tools.block_stylesheets()` that returns
  `[]` when the directory is absent. The four aliases are **exempt** from it and
  covered by `test_published_aliases_reach_a_block_sheet` instead, which
  `skipif`s on there being no block sheet. Exempting them beats skipping the
  whole test: 04 §9's "a guard that always skips reads green while protecting
  nothing" applies to the other ~25 tokens too, and they are checkable today.

Every one of these was mutation-checked red-then-green, including both
block-sheet guards against a temporary `static-blocks/` sheet.

**One guard goes slightly past the ticket's three bullets, deliberately:**
`test_block_sheets_never_name_a_clara_token` fails a block sheet that reaches
for `--clara-*` directly. It is the *reason* the aliases exist (06 §3's second
half — "the block sheet then speaks only `--derico-*` and `--plone-*`"), and
without it the aliases are a convention rather than a seam. Skipped today;
**binding on ticket 08.**

### 4. "No upgrade step" — confirmed, with the mechanism

The ticket asked to confirm this before closing, and the confirmation is
stronger than "we didn't touch the XML". Plone builds bundle URLs through
`webresource` with `unique=True`
(`Products/CMFPlone/resources/browser/resource.py:95`), and that unique key is a
**hash of the file's own bytes** (`webresource/resources.py:135`, `file_hash`).
There is no `last_compilation` in this bundle's record and none is needed:
editing `derico.css` busts its own cache. So the content change ships through
the existing `plone.bundles/plonetheme-derico` record with **no registry value
changed and no upgrade step** — the one case where a stale-cache argument could
have forced one, and it does not.

### 5. Two self-descriptions were falsified by this change, and fixed here

`derico.css`'s own header said "no component rules"; `registry.xml`'s comment
said "one bundle whose whole content is a `:root` token override". Both are now
false *because of this ticket*, so both were corrected in place, phrased as
`CONTEXT.md` already phrases it — a rule earns its place only when nothing else
in the theme can reach the thing it styles. The `registry.xml` edit is a
**comment only**; GenericSetup imports records, not comments, so re-importing
the profile yields identical registry state and §4 stands.

The broader README + "ENTIRE theme" rewrite stays where **04 §12** put it — the
packaging change that adds the Blicca dependency — because that sentence only
becomes false when the blocks actually land.

### Shipped

- `src/plonetheme/derico/static/derico.css` — §3 (four aliases), §7 (chrome
  rule), header rewritten, §4–§6 renumbered.
- `src/plonetheme/derico/profiles/default/registry.xml` — comment only.
- `tests/clara_css.py` — `block_stylesheets()`.
- `tests/test_override_minimality.py` — three tests widened, four added, module
  docstring now states what a green run does and does not claim.
- `CHANGELOG.md` — one entry under `1.0.0a1 (unreleased)`, which explicitly
  narrows the earlier "any selector beyond `:root`/dark" claim in the same
  unreleased block rather than rewriting it.

No new lint errors (`ruff check` reports the same 2 pre-existing findings in
`clara_css.py:_blocks` with these changes stashed and unstashed).
