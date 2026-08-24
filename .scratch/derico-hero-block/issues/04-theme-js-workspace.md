# Decide: the shape of plonetheme.derico's JS workspace

Type: grilling
Status: closed
Assignee: md@derico.de
Blocked by: —

## Question

The theme today is build-free — its `registry.xml` calls itself "derico's ENTIRE
theme: one bundle whose whole content is a `:root` token override", and there is
no `package.json`. This ticket decides what it becomes.

- **One bundle or several?** Verified at charting: `loadBlockAddons`
  (`plone.blicca.auroraeditor/wrapper/src/main.tsx:89`) calls `install(config)`
  once **per record**, with no dedupe. A shared bundle's module is cached by
  `import()`, but if one `install()` registers every derico block, then
  `enabled: false` on a second block's record does nothing — the first record's
  `install()` re-registers it and the kill switch stops meaning anything. So
  either **one record listing all `types`** (loses per-block enable, deviates
  from contract §3.2's one-record-per-block) or **one workspace, N Vite entry
  points, N bundles, N records** (conformant, shared code emitted as a chunk).
  Only binds once a second brand block exists — but the layout is chosen now.
- **Where things live.** Contract §3.1 puts the publishable npm workspace at
  `bundle-src/` in the repo root. The single-ecosystem exemption means nothing is
  published here, so the name is free — keep `bundle-src/` for consistency with
  the contract, or something plainer?
- **The build.** Vite lib build per contract §1.2: `jsx: 'automatic'`, externals
  matching the promised facade surface (react, jsx-runtime, react-dom(+client),
  jotai, platejs, `@plone/registry`, `@plone/helpers`). Output committed to
  `src/plonetheme/derico/static/`, never built at install time. pnpm, per the
  standing preference.
- **CSS scope-wrap.** `@plone-collective/blicca-block-tools` does not exist; the
  wrap lives at `plone.blicca.auroraeditor/wrapper/build-plugins/scope-wrap.ts`.
  Vendor a copy, import it across the checkout, or something else — and say what
  makes it survive the aurora repo moving the file.
- **`block_api` declaration.** Host is at 1.1; ticket 03 may bump it. What does
  the record declare, and how does a developer notice when it drifts?
- **CI.** The theme's `.github/workflows/ci.yml` runs pytest and Ruff. Does the
  JS build get checked there, and does CI verify the committed artifacts match
  their source?
- **The theme's self-description.** The README and that `registry.xml` comment
  both assert the theme is tokens-only. Rewrite them in the same change.

---

## Answer (2026-08-23)

Settled with md@derico.de over three grilling rounds. The theme stops being
build-free and gains a pnpm + Vite workspace; below is everything tickets 08
and 09 build against, so neither has to re-decide any of it.

### 1. Topology: one workspace, N entry points, N bundles, N records

Contract-conformant (§3.2, one record per block). The alternative — one record
listing every `type` — silently kills the per-block kill switch, because
`loadBlockAddons` (`wrapper/src/main.tsx:89`) calls `install(config)` once per
**record** with no dedupe: a single `install()` registering every derico block
means `enabled: false` on a second record does nothing, since the first
record's install re-registers it.

Costs nothing today. Vite 8's `lib.entry` is an `InputOption` (verified:
`vite/dist/node/index.d.ts:2277`), so the entry map is a record; shared code
falls out as a chunk, and because both entries resolve their relative chunk
imports under the **same** static base, the shared chunk is one URL and
therefore one module instance. Set the entry map up as a map from day one with
`hero` as its only member.

### 2. Location and tooling

`bundle-src/` at the repo root, per contract §3.1 — the deviation buys nothing
and a reader who knows the contract finds it where the contract says. pnpm,
with the proto's `pnpm-workspace.yaml` (`packages: ['.']`, `allowBuilds:
{esbuild: true}` — without the latter, pnpm's build-script blocking stops
esbuild installing its binary).

Node and pnpm are pinned **in the workspace, not the workflow**: a
`packageManager: "pnpm@<exact>"` field plus `.nvmrc`, with CI reading
`node-version-file: .nvmrc` and running `corepack enable`. Pinning only in CI
lets the two drift the moment either moves, and Q7's diff check depends on them
not drifting. `pnpm-lock.yaml` is committed (`--frozen-lockfile` requires it).
`.gitignore` needs no change — it already covers `node_modules/`,
`.pnpm-store/` and `.vite/`.

### 3. Serving the artifacts: a second, build-output-only static directory

`src/plonetheme/derico/static-blocks/`, registered **only** as
`<plone:static name="plonetheme.derico.blocks" type="plone" directory="static-blocks"/>`
→ `++plone++plonetheme.derico.blocks/hero.js`.

Rejected: reusing the existing `static/` (it is served as
`++resource++plonetheme.derico/`, and `_busted_url`'s docstring names
`++plone++` — `blockaddons.py:170`); and double-registering `static/` under both
directives, which would give every file two public URLs. Two URLs for one JS
module is precisely the duplicate-instance failure this contract exists to
prevent, so the ambiguity is not worth the tidiness even where it is currently
harmless.

The name is site-global. `name="plonetheme.derico"` was rejected because it
would put `++plone++plonetheme.derico/` and `++resource++plonetheme.derico/` on
two different directories under one name.

**`emptyOutDir: true`, set explicitly** (Vite otherwise refuses, the outDir
being outside the project root). This is what the separate directory buys:
hashed chunk names plus committed artifacts plus `emptyOutDir: false` would
accumulate orphaned chunks that `git diff --exit-code` cannot see — a renamed
chunk leaves the old file tracked and unchanged, so the check passes while the
directory rots.

**Consequence, binding on ticket 08:** no hand-written file may live in
`static-blocks/`. The explanatory README goes in `bundle-src/README.md`.

No `manifest: true` — the record points at a stable filename; the wrapper's
manifest exists only so `@@aurora-edit` can emit modulepreloads for the
remote's chunk closure.

### 4. Naming, decoupled from ticket 02

Entry key is the block's short kebab-case name: `{ hero: 'src/hero/index.tsx' }`
→ `hero.js` / `hero.js.map`. The `@type` string and the record name
(`<pkg>.<block>`) stay **ticket 02's** to fix; the build never learns the
`@type`, so 02 cannot rename build artifacts.

Stable entry names via `lib.fileName`, `chunkFileNames: 'chunks/[name]-[hash].js'`
— mirroring the wrapper, where the webresource uuid on the entry URL does the
cache-busting (ADR 0010: changed chunk hash → changed entry → new uuid).

### 5. One stylesheet, declared on every record

Lib mode's `cssFileName` is a single string (`index.d.ts:2299`) — one sheet per
**build**, not per entry. So N block records all point their `css` field at the
same asset.

`css_urls` (`blockaddons.py:292`) does not dedupe, so this emits N identical
`<link>` tags. **Accepted**: same URL, one fetch, one cache entry, and §6.3
already ships every registered block's CSS on every page. The "one designated
record owns the CSS" alternative was rejected — it creates a hidden coupling
where disabling block A silently unstyles block B.

Worth a two-line dedupe in `css_urls` upstream as cosmetics; deliberately **not**
added to ticket 03's scope.

### 6. Externals and the leak check

Externalize the **entire** §2.1 promised list — `react`, `react/jsx-runtime`,
`react-dom`, `react-dom/client`, `jotai`, `platejs`, `@plone/registry`,
`@plone/helpers` — not the three the proto config carries. Externalizing an
unimported module is free; a partial list is a landmine for the second block.

The leak check §1.2 asks for is written **here**, since the scaffold that was
supposed to ship it does not exist and is out of scope for this map. It is an
**allow-list, not a deny-list**: a `generateBundle` hook walking each emitted
chunk's `imports` and `dynamicImports`, failing the build on any specifier that
is neither relative nor in the promised-externals set. A deny-list of promised
module names would miss subpath drift like `platejs/react` or a transitive dep
reaching React under another specifier — and a promised singleton in the bundle
is two Reacts and a null hook dispatcher at runtime.

### 7. The vendored scope-wrap

`bundle-src/build-plugins/scope-wrap.ts`, vendored verbatim from
`plone.blicca.auroraeditor/wrapper/build-plugins/scope-wrap.ts` with a header
naming the upstream path and commit. DevDeps `vite` and `postcss`, pinned.

Rejected: importing across the checkout, which makes the theme unbuildable for
anyone who cloned only this repo — and since committed artifacts mean most
people never build, the few who do are the ones least worth blocking.
`@plone-collective/blicca-block-tools` does not exist and is out of scope.

**Invoked with three scope roots, not the wrapper's two:**
`scopeRoots: ['.aurora-editor', '.aurora-editor-portal', '.aurora-blocks-view']`,
`scopeLimit: '.aurora-pattern-island'` (contract §6.1). Unlike the wrapper's own
CSS, a block's sheet must also style the public page. **The vendored *code* is
identical; the *options* deliberately are not — so the drift guard below
compares the file, never the invocation.** Ticket 06 confirms the limit against
the extracted CSS.

### 8. `block_api`: declare the floor, guard the ceiling

The record declares **`1.0`**, not the host's current `1.1` — the minimum the
block actually needs (React + jsx-runtime is 1.0 surface). Declaring the host's
version would let ticket 03's possible bump to 1.2 strand the block, and a §2.4
mismatch is a fail-soft skip: the block silently vanishes from the slash menu.

### 9. Two lockstep guards, and where they actually run

Both are pytest, both in `tests/test_block_addon_lockstep.py`, sharing one
sibling-checkout resolution helper, both `pytest.skip` when
`plone.blicca.auroraeditor` is not checked out beside this package:

1. the vendored `scope-wrap.ts` still matches upstream's file;
2. the declared `block_api` is ≤ the host's, read from the wrapper's
   `static/block-api.json` (stamped by `blockApiStamp()`,
   `wrapper/vite.config.ts:18`).

**The sibling checkout goes on CI's `test` job, not the JS job** — that is where
pytest runs, and a guard that always skips reads green while protecting
nothing, which is worse than no guard. It runs three times across the Python
matrix; a conditional to avoid that is more machinery than the `git clone` it
saves. The JS job stays single-repo, which is exactly what vendoring bought.

### 10. CI

One new JS job: `corepack enable`, `pnpm install --frozen-lockfile`,
`pnpm typecheck`, `pnpm build`, then **`git diff --exit-code` over
`static-blocks/`**. Committed artifacts rot the moment someone edits source and
forgets to rebuild, and nothing at install time rebuilds — so the diff is the
only thing that makes committed artifacts safe rather than merely convenient.

Sourcemaps **are** committed (`sourcemap: true`): the delivery story is that a
no-Node admin installs this and never builds it, which makes an undebuggable
artifact a real cost. **Named abort condition:** if the first CI runs show maps
differing across machines, drop to `sourcemap: false` — never disable the diff
check. A check that cries wolf gets switched off, and then nothing guards the
artifacts at all.

### 11. TypeScript, linting, task runner

`tsconfig.json` copying the wrapper's options (`moduleResolution: 'bundler'`,
`jsx: 'react-jsx'`, `strict`, `verbatimModuleSyntax`,
`skipLibCheck`) so both halves of the checkout agree on what valid code is, plus
a `typecheck: tsc --noEmit` script run in CI.

DevDeps `@plone/types`, `react`, `react-dom`, `@types/react`, `@types/react-dom`,
**pinned to the exact versions `wrapper/package.json` declares** (React
`19.2.0`, `@plone/types` `3.0.0-alpha.2`) — these are external at runtime, so
the versions here are a types-only claim about what the host really runs. **No
third lockstep guard for this**: wrong types produce a compile error or a
visibly broken block, not the silent failure that earned §7 and §8 theirs.
Noted in `bundle-src/README.md` instead.

**No ESLint, no Prettier, no Biome.** `tsc --strict` covers what matters at this
size; a linter is config, a CI job and a dependency tree for ~200 lines of TSX.
Revisit at the second brand block — adopting a formatter later is one reformat
commit, carrying one now is friction on every commit.

`invoke build-blocks` added to `tasks.py`, wrapping
`pnpm --dir bundle-src install && pnpm --dir bundle-src build`, failing with a
readable message when pnpm is absent. `tasks.py` stays the single answer to
"how do I do anything in this repo".

### 12. Dependency posture and the theme's self-description

`plone.blicca.auroraeditor` becomes a **hard** dependency in `pyproject.toml`
`dependencies`, plus a `[tool.uv.sources]` path source beside Clara and
pageletlayout. There is no user who wants derico's brand without its brand
blocks, and a conditional dependency means ZCML guards and a half-installed
theme.

A Python dependency does not install a profile, so
`<dependency>profile-plone.blicca.auroraeditor:default</dependency>` goes into
`profiles/default/metadata.xml` above Clara's. **This needs an upgrade step like
any other profile XML change** — a new GS dependency affects only *fresh*
installs, so an already-installed derico site would otherwise get the block
record with no Blicca behind it. Scaffold via `plonecli add upgrade_step`,
narrowed to run the Blicca profile plus the registry import step; never
hand-edit `metadata.xml`'s `1000`.

**The theme's self-description is rewritten in the same change.** The README
("The whole theme is one stylesheet of custom properties") and the
`registry.xml` comment ("derico's ENTIRE theme: one bundle whose whole content
is a `:root` token override") both become false; both become "a token layer plus
the brand blocks the tokens cannot reach", which is what `CONTEXT.md` already
says — so the three stop disagreeing.

`tests/test_override_minimality.py` stays **exactly** as strict on `derico.css`;
the block's scope-wrapped sheet is a different file and out of its scope. One
line is added to the test module saying so, because a green minimality suite now
reads as a claim about the whole theme's CSS, which it no longer is.
