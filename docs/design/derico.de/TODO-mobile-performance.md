# TODO: mobile performance optimization

Source: [Lighthouse report, 2026-09-23](new.derico.de_2026-09-23_15-14-22.json)

Tested URL: https://new.derico.de/Plone/de

## Baseline

| Metric | Result |
| --- | ---: |
| Performance | 71/100 |
| Accessibility | 96/100 |
| Best practices | 100/100 |
| SEO | 92/100 |
| Largest Contentful Paint (modeled) | 11.46 s |
| First Contentful Paint | 2.6 s |
| Total Blocking Time | 0 ms |
| Cumulative Layout Shift | 0.005 |
| Total transfer | 3,225 KiB / 38 requests |

Images account for about 85% of transferred bytes. Prioritize image delivery and render-blocking resources, not JavaScript CPU micro-optimizations.

## 1. Optimize the mobile hero — highest LCP priority

- [ ] Inspect the selected `currentSrc`, actual Plone-generated scale, encoding settings and response size. The selected WebP is about 501 KiB; Lighthouse estimates 380 KiB removable.
- [ ] Benchmark AVIF against compressed WebP. Aim initially for 100–150 KiB if visual quality permits; this is a budget to validate, not a guaranteed result.
- [ ] Review `HERO_VARIANTS` in `src/plonetheme/derico/setuphandlers.py` and picture generation in `src/plonetheme/derico/browser/hero.py`.
- [ ] Validate responsive candidates and `sizes` against device pixel ratio and the tall `object-fit: cover` box, not viewport width alone. Avoid excessive downloads without making the background blurry.
- [ ] Preserve eager loading, initial-HTML discovery and `fetchpriority="high"`; these already pass.
- [ ] If changing picture variants, account for existing installations: `ensure_hero_variants()` is add-only and will not update an existing variant automatically.

## 2. Replace oversized promo PNG delivery

- [ ] Optimize `odoo_de.png` (about 1.04 MiB) and `frameworks_de.png` (about 0.99 MiB). Both deliver 1254×1254 images for roughly 379–412 CSS-pixel-wide elements.
- [ ] Generate compressed WebP/AVIF variants and render responsive `srcset` with accurate `sizes`, accounting for device pixel ratio.
- [ ] Check infographic text readability on real phones before choosing final resolution and compression.
- [ ] Preserve existing native lazy loading. Adding lazy loading again does not address the problem.
- [ ] Review the lower-page forest image's scale/compression as a smaller follow-up.

Lighthouse estimates approximately 1.98 MiB removable across the two promo PNGs. Treat this as an estimate, not an acceptance requirement.

## 3. Minify CSS and reduce render-blocking resources

The report includes 15 stylesheet requests, approximately 67 KiB of potential CSS minification savings and a 2.77-second render-blocking opportunity, primarily affecting FCP.

- [ ] Enable production CSS minification while preserving readable sources and source maps. `bundle-src/vite.config.ts` currently explicitly sets `minify: false`.
- [ ] Ensure standalone theme stylesheets also have a minified delivery path, not just the block bundle.
- [ ] Serve `print.css` with `media="print"`; `src/plonetheme/derico/profiles/default/registry.xml` currently documents delivery with `media="all"`.
- [ ] Review page-specific bundle loading and omit assets only where their components are genuinely absent.
- [ ] Preserve cascade layers, `@scope`, shared public/editor styles and dependency ordering when changing the build or loading strategy.
- [ ] Verify the report's “100% unused” findings for Aurora and Derico block CSS before removing anything. These sheets style the rendered blocks; coverage or scoped-CSS handling needs investigation.
- [ ] Consider critical CSS only if simpler minification and loading changes leave first paint too slow.

## 4. Reduce unnecessary public-page JavaScript

The report identifies approximately 38 KiB of duplicate JavaScript and 95 KiB of unused JavaScript. These figures overlap and must not be added together.

- [ ] Establish which public-page patterns require the Aurora host runtime and Plone bundles.
- [ ] Load editor-only runtime only where needed, without removing dependencies required by public widgets.
- [ ] Investigate duplicate jQuery and Patternslib across Plone and Aurora bundles; share compatible dependencies or avoid loading the unnecessary runtime.
- [ ] Defer compatible blocking scripts while preserving initialization/dependency order.
- [ ] Regression-test mobile navigation, search, forms, login and editing.

This is secondary to images and CSS: Total Blocking Time is already 0 ms.

## 5. Improve caching for versioned static assets

- [ ] Review CSS/font responses currently using a one-day cache lifetime.
- [ ] Apply long-lived immutable caching only to URLs that reliably change when their content changes.
- [ ] Verify cache invalidation for relative resources, generated stylesheets and updated deployments before extending lifetimes.
- [ ] Keep HTML and personalized responses outside immutable static-asset rules.
- [ ] Measure repeat visits separately; caching mainly benefits returning visitors rather than cold-load LCP.

## 6. Improve accessibility, SEO and layout robustness

- [ ] Fix invalid `dl.ring-legend` markup in `src/plonetheme/derico/browser/templates/hero.pt`: move standalone numbering inside `<dt>` or use a semantic ordered list. Preserve valid structure for partially filled entries.
- [ ] Apply the matching semantic change to the editor component and update relevant tests/styles.
- [ ] Add the missing page meta description and verify it appears in rendered HTML.
- [ ] Give the header logo explicit dimensions/aspect ratio. This is a minor cleanup; CLS already passes comfortably.

## Verification and measurement caveats

- [ ] Implement and measure in order: hero → promo images → CSS delivery → unnecessary JS → caching.
- [ ] Run at least three comparable cold-cache mobile Lighthouse tests per stage and compare medians. Keep the tested URL, browser/version, viewport and throttling settings consistent.
- [ ] Validate on a real phone, including image sharpness, infographic readability and interactive controls.
- [ ] Target LCP below 2.5 s and FCP below 1.8 s while preserving the current excellent CLS and TBT. Do not promise a specific score increase before measuring.
- [ ] Capture before/after selected image URLs, transfer sizes and metrics.

The report's modeled LCP is **11.46 s**, while observed LCP is **1.307 s**. The detailed LCP breakdown describes the observed trace and is not an additive explanation of the modeled result. Lighthouse opportunity estimates overlap and must not be summed. This report does not establish real-user INP.
