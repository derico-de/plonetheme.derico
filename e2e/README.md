# Derico Hero browser tests

Two browser tests that answer the two questions the Python suite cannot: does
the block work in a real `@@aurora-edit`, and does the published page look like
the design source?

| file | what it proves | needs the editor bundle |
| --- | --- | --- |
| `hero-editor.e2e.js` | insert, author, save, reload, the insert gate, one React, `<html lang>`, no clipping at 320/375 | yes |
| `hero-view.e2e.js` | the published page measured against `docs/design/derico.de/site`, at 1440 / 900 / 375 / 320 | no |

They build their own fixture over `plone.restapi` (`hero-fixture.js`) and
delete it again; set `DERICO_E2E_KEEP=1` to leave it on the site to look at.

## Prerequisites

- A running Plone with `plonetheme.derico` installed at profile version
  **1001** or later, and `plone.restapi`.
- A content type carrying the blocks behaviour. The fixture uses `Article`;
  override with `DERICO_E2E_PAGE_TYPE`.
- For `hero-editor.e2e.js` only: the mockup `bundle-plone` (pat-auroraeditor,
  pat-contentbrowser) reachable from the edit page, either as the committed
  bundle or from a dev server. `hero-view.e2e.js` never loads the editor.
- A Chromium `playwright-core` can launch: either `npx playwright-core install
  chromium` once, or point `DERICO_E2E_CHROMIUM` at an existing executable.

## Running

```sh
pnpm install
DERICO_E2E_BASE=http://127.0.0.1:8081/Plone \
DERICO_E2E_CHROMIUM=/usr/bin/chromium pnpm run e2e
```

Environment (all optional): `DERICO_E2E_BASE` (default
`http://127.0.0.1:8081/Plone`), `DERICO_E2E_USER` / `DERICO_E2E_PASSWORD`
(default `admin`/`admin`), `DERICO_E2E_CHROMIUM`, `DERICO_E2E_PAGE_TYPE`,
`DERICO_E2E_KEEP`. Each also accepts its `AURORA_E2E_*` spelling, so a shell
already set up for the Blicca suite works unchanged.

## How the view test compares

`hero-view.e2e.js` serves `docs/design/derico.de/site` from this repository on
a throwaway port and loads the mockup and the Plone page in the same browser,
at the same viewport, one after the other. Every number it asserts is measured
on both — "matches the mockup" is a claim about two renderings, and a constant
copied out of an old session is evidence about neither.

The page is browsed **anonymously**. The hero is `blockWidth: full` and the
breakout subtracts `--plone-toolbar-width`, so a logged-in measurement is
viewport-minus-toolbar (1220 at a 1440 viewport) and would compare a narrower
hero against a full-width mockup.

Contrast is measured against the pixels the text actually sits on, not against
a computed `background-color`: the hero paints ground, then photograph, then
the wash gradient over it. The test screenshots the hero twice — as rendered,
and with every glyph painted transparent — and reads the difference. Pixels
the two shots disagree on are pixels a glyph covered, and the second shot says
what it covered. Reported per element: the worst ratio, the median, and the
share of the glyph's own area below the threshold — which is what separates a
speckle of bright forest under one letter from a line nobody can read.

## Known gaps this suite reports rather than asserts

Both are open tickets, and both are printed as `note` lines on every run:

- **ticket 17** — the hero's body font and leading fall through to Blicca's
  `.aurora-blocks-view` defaults instead of the theme's own.
- **ticket 18** — the ring legend's `is-now` row misses WCAG AA over the
  brightest part of the photograph, and at 375 the numerals go with it. The
  design source fails the same way. The exceptions in the test are named one
  by one, so a *new* contrast failure anywhere else still fails the run.
