# Build: the Derico Hero's editor half

Type: task
Status: open
Blocked by: 02, 04, 06, 11, 13

## Question

With the content model (02), the workspace (04) and the CSS (06) settled, build
the JS half in `plonetheme.derico`.

- The workspace and Vite config from 04, producing committed artifacts under
  `src/plonetheme/derico/static/`.
- `install(config)` adding the `blocksConfig` entry — `id`, `title`, `icon`,
  `edit`, `view`, `blockSchema` — and returning `config`. It must return the
  config object; the wrapper throws otherwise (`main.tsx:96`).
- Both `edit` and `view` implemented, per the charting constraint.
- The scope-wrapped stylesheet emitted by the same build.
- Registration happens before `mount()`; the blocksConfig registry is not
  reactive (contract §1.3).

Tests as the code is written, per the repo's standing preference for real tests
over verification scripts.
