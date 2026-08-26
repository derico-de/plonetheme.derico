# Task: give CI read access to plone.blicca.auroraeditor

Type: task
Status: closed
Blocked by: —

## Question

Nothing to decide — work only the repository owner can do.

[Ticket 09](09-build-server-half.md) made `plone.blicca.auroraeditor` a hard
dependency of `plonetheme.derico`: `browser/hero.py` imports its promised
rendering API at module level, and the GS profile depends on Blicca's. The
package is **private and not on PyPI**, so CI's
`pip install -e ".[test]"` cannot resolve it without a checkout, and the
checkout needs a token.

The workflow now **fails with a named error** when `BLICCA_TOKEN` is empty,
rather than installing nothing and running a green job over an uninstallable
package. So the `test` job is red until this is done.

Set the repository secret `BLICCA_TOKEN` on `derico-de/plonetheme.derico` to a
token with read access to `derico-de/plone.blicca.auroraeditor`.

Doing this also closes the older, quieter gap [ticket 04
§9](04-theme-js-workspace.md) named: the two lockstep guards — the vendored
`scope-wrap.ts` against upstream, and the declared `block_api` floor against
the host's stamp — have been skipping on CI since they were written. *"A guard
that always skips reads green while protecting nothing, which is worse than no
guard."* Both run locally today and neither has ever run on CI.

Not on the route to the Destination: the block installs and works on the
sandbox site whether or not CI can build it. Ticketed anyway because a red CI
with no ticket behind it is a thing that gets normalised.

Resolved when a CI run on `master` is green.

## Closed — out of scope

Ruled out of scope by md@derico.de on 2026-08-26: CI is not relevant to this
effort. The ticket had already said as much about the route — "the block
installs and works on the sandbox site whether or not CI can build it" — and
kept itself open only on the argument that a red CI with no ticket behind it
gets normalised. That argument is the repository owner's to weigh, not this
map's, and the Destination does not pass through it.

Closed rather than left open so it is unambiguously off the frontier. Nothing
here is withdrawn: `BLICCA_TOKEN` is still what CI needs, and the two lockstep
guards from ticket 04 §9 (the vendored `scope-wrap.ts`, the declared
`block_api` floor) still skip there. Both run locally, and the local run is
what this map relied on throughout.
