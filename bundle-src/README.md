# `bundle-src` — the brand blocks' editor half

This workspace builds the JavaScript that Aurora loads in the editing canvas,
and the stylesheet both the canvas and the published page use. Its output is
committed, so **installing this theme never requires Node**: a site
administrator installs the Python package and gets working blocks.

Shape and rationale were settled in hero ticket 04
(`.scratch/derico-hero-block/issues/04-theme-js-workspace.md`); this file is
the short version, and that ticket is the argument.

## Build it

```bash
uv run invoke build-blocks     # from the package root — installs, then builds
```

or directly, if you already have the workspace installed:

```bash
pnpm --dir bundle-src install
pnpm --dir bundle-src build
pnpm --dir bundle-src typecheck
pnpm --dir bundle-src test
```

**pnpm, never npm.** The lockfile is `pnpm-lock.yaml`.

## Rebuild whenever you touch `src/`

The build writes to `../src/plonetheme/derico/static-blocks/`, and those
artifacts are **committed**. Nothing rebuilds them at install time, so a source
edit without a rebuild ships stale JavaScript to every site. CI runs
`git diff --exit-code` over that directory for exactly this reason (04 §10) —
if it fails, you forgot to rebuild.

Sourcemaps are committed too: an admin who never builds this still deserves a
debuggable artifact.

## Two directories, one of them not yours

- `src/plonetheme/derico/static/` — hand-written, served as
  `++plone++plonetheme.derico`. `derico.css` lives here.
- `src/plonetheme/derico/static-blocks/` — served as
  `++plone++plonetheme.derico.blocks`, and reserved **entirely** for build
  output. `emptyOutDir` wipes it on every build, so **a hand-written file
  placed there is deleted without warning** (04 §3). Explanatory prose goes in
  this README instead — that rule is why this file exists.

## One workspace, N entry points, N bundles, N records

`hero` is the only entry today, but `vite.config.ts` takes an entry *map* from
day one: the second brand block is one line there plus one registry record,
never a re-layout.

Each bundle registers exactly **one** block and its `install()` **must return
the config object** — the loader throws otherwise. One block per bundle is not
tidiness: `loadBlockAddons` calls `install(config)` once per registry record
with no dedupe, so a shared bundle registering every block would let the first
record silently re-register a block a later record had disabled, killing the
per-block `enabled` kill switch (04 §1).

Lib mode emits **one** stylesheet per build rather than one per entry, so every
block record points its `css` field at the same `blocks.css` (04 §5).

## Dependency versions are a claim, not a choice

React, `react-dom`, their `@types`, and `@plone/types` are pinned to the exact
versions `wrapper/package.json` declares (React `19.2.0`, `@plone/types`
`3.0.0-alpha.2`). They are **external at runtime** — resolved through the
page's import map, never bundled — so the versions here are a types-only claim
about what the host actually runs. Bumping them without the host bumping is how
you get a block that compiles and then breaks in the browser.

There is deliberately **no third lockstep guard** for this: wrong types produce
a compile error or a visibly broken block, not the silent failure that earned
the vendored plugin and `block_api` theirs (04 §11).

## No ESLint, no Prettier, no Biome

`tsc --strict` covers what matters at this size. A linter is config, a CI job
and a dependency tree for a few hundred lines of TSX. Revisit at the second
brand block — adopting a formatter later is one reformat commit, carrying one
now is friction on every commit (04 §11).

There **is** a test runner: `vitest`. The seven-case degradation table is a
contract both halves must honour identically, and the public half is tested
from pytest, so without a runner here the canvas side goes unchecked until
someone clicks through the editor. It never reaches the shipped bundle.

## `build-plugins/scope-wrap.ts` is vendored — do not edit

It is copied verbatim from `plone.blicca.auroraeditor`'s
`wrapper/build-plugins/scope-wrap.ts`, so this repo builds without reaching
across a checkout (04 §7). `tests/test_block_addon_lockstep.py` compares
everything below the sentinel line against upstream whenever that package is
checked out beside this one, and skips when it is not.

The *code* is upstream's; the *invocation* is not. This build passes three
scope roots where the wrapper passes two — a block's sheet has to reach the
published page (`.aurora-blocks-view`) as well as the editor.
