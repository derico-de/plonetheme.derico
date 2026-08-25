# Decide: what the hero's headline does when its longest word will not fit

Type: grilling
Status: resolved
Blocked by: —

## Question

Surfaced by [ticket 07](07-prototype-rings-in-canvas.md), and **inherited from
the mockup rather than introduced by Plone**: at a 320px viewport the design's
own headline overflows its column and is clipped by the hero's
`overflow: hidden`.

Measured, same headline ("Anwendungen, die bleiben."), 44px Literata — the
bottom of the `--derico-text-display` clamp:

| surface | hero box | copy column | h1 first line | overflow |
|---|---|---|---|---|
| mockup, standalone, 320 | 320 | 288 | 320 | 16px, clipped |
| canvas, 320 viewport, toolbar collapsed | 260 | 228 | 309 | 65px, clipped |
| canvas, 375 viewport, toolbar collapsed | 315 | 283 | 309 | 26px, clipped |

The canvas is worse only because the toolbar takes 60px off the width; the
defect is in the design source. Ticket 07 deliberately did not fix it — the
prototype's job was to report, and this is a design call, not a canvas one.

What should happen when a headline word is wider than the column?

- **Shorten the display step at the bottom of the clamp.** `--derico-text-display`
  bottoms out at 2.75rem; a lower floor buys the room back but changes the
  design's voice at exactly the size where the hero is one column of type.
- **Let it break.** `overflow-wrap: break-word` is what the canvas already does
  by inheritance and it never clips — but it breaks mid-token
  ("Anwendungen" / ", die bleiben."), which is worse than clipping to read.
- **Hyphenate.** `hyphens: auto` with `lang="de"` breaks at syllable
  boundaries. German compounds are exactly the case it exists for, and the site
  is bilingual, so the `lang` has to be right on the element anyway.
- **Constrain the content.** A brand block "offers the author no options" (the
  map's standing principle), but it can still document a headline length the
  design holds at every width, and the hero is one designed page's opening.

Whatever comes out of it applies to the **kicker and the lede too**, which have
the same exposure with longer German compounds, and it interacts with ticket 07's
finding that the hero should force `overflow-wrap: normal` to keep the canvas
wrap identical to the view's — that force is what turns a canvas break into a
canvas clip.

## Answer

Grilled with md@derico.de, 2026-08-25, against measurements taken on the design
source itself: [`assets/15-wrap-measurements.md`](../assets/15-wrap-measurements.md).

**The ticket asked the wrong question.** All four of its options treat this as
"the words are too big". The box is what overflows. `.home-hero__grid > div` is
a grid item, so its automatic minimum size is `min-content` — the longest word —
and at a 320 viewport the copy cell measures **320px inside a 288px shell**
(383px with a longer compound). The cell sticks out and the hero's
`overflow: hidden` cuts it. The mockup already pins this at ≥56rem with
`minmax(0, 1.02fr)`; the single-column range never got it.

So the answer is a **ladder**, each rung catching what the one above cannot,
and the guarantee living on the bottom rung rather than in the type:

1. **`min-width: 0` on the hero's grid and flex items — the guarantee.** One
   declaration, no threshold, and it holds for a headline nobody has written
   yet. Nothing else in this answer is load-bearing for "never clipped".
2. **`overflow-wrap: break-word` on the text — keeps an unfittable word
   visible.** It **cannot** substitute for rung 1: measured, it does not feed
   intrinsic sizing, so with it alone the cell still blew out to 320 / 383 and
   still clipped. `overflow-wrap: anywhere` *does* feed intrinsic sizing and is
   therefore a pin by itself — rejected anyway, because it produced wraps
   identical to rung 1 + rung 2 in all 8 measured cases while hiding the
   layout fix inside a text property.
3. **A re-ramped display step — makes the shipped headline fit so rung 2 never
   fires at 320.** See below.
4. **`hyphens: auto` — an enhancement, never the guarantee.** It is a **no-op
   in this Chromium**: `de` and `en` probes both stayed on one line, no
   dictionaries in the container. Ship it (German compounds are exactly its
   case), label it, and let a test assert the *declaration*, never the
   rendering.

### The ramp: `clamp(2.4rem, 1.4rem + 5cqi, 5rem)`

**Lowering the floor does not do what this ticket assumed.** At a 320 viewport
`clamp(2.4rem, 1.85rem + 4vw, 5rem)` returns its *middle* term — 42.4px — not
its floor; only below ~315px does the floor bind at all. The old 2.75rem floor
did bind, so dropping it to 2.4rem moves 320 from 44px to 42.4px, the word still
needs 308px in a 288px column, and the headline still breaks. Applied and
measured before this was caught: `Anwendunge` / `n, die bleiben.`

Fitting at 320 needs a new **slope**. Of the candidates, `1.4rem + 5vw` was
chosen over `1.5rem + 4vw`: the latter buys the fit by shrinking the whole
mid-range ~9%, paying at every width for a defect at one. The chosen ramp gives
38.4px at 320 (word 279px, 9px of slack), tracks the old ramp where the design
is usually seen (60.8 against 60.3 at 768), and reaches the 5rem cap at a
**1152px** box instead of 1260.

**`cqi`, not `vw`.** Ticket 07's table shows the hero measures **1220 @220** on
the *public view* as well as in the canvas — that `@220` is the Plone toolbar.
So the hero box equals the viewport only for an anonymous visitor, and a
`vw` ramp sizes the headline against a box the page does not have for every
logged-in user, on both surfaces — the 320px defect in miniature. `cqi` reads
the hero's own box, which 06 already made the measuring stick for its layout;
a second, different measuring stick for its type is the two-answers-for-one-
thing drift tickets 11 and 13 both rejected. The anonymous visitor gets a size
identical to the mockup; the cap at 1152 means a toolbar-shrunk 1220px hero
still reaches the full 80px.

The block states this clamp itself, on `.derico-hero h1` — **not** as a token
override. `--derico-text-display` is an alias of `--clara-text-display`
(derico.css §3: "Aliases, never values"), Clara's other consumer is
`.clara-home-copy h1`, and 06 already established the block owns type it cannot
reach through the ladder. The floor is this design's voice at one width, not
the theme's scale.

### Scope

All of it, as **one rule over the hero's grid and flex items**, not per element:
headline, kicker, lede, the four legend `{title, subtitle}` pairs and both CTA
labels. The mechanism is identical everywhere — intrinsic min-width in a grid or
flex item — and writing it six times invites one to be forgotten. (The legend's
inner `minmax(0, 1fr)` already pins its second column; its text still needs
rung 2.)

### `max-width: 14.5ch` stays

At 1440 the h1 box and the copy column coincide at 590px and the shipped
headline's longest line is 582 — **8px** of slack, so a marginally longer word
crosses it and breaks at desktop. Left alone deliberately: it is the mockup's
measure, the ladder makes that failure graceful rather than absent, and the
headline budget below addresses the cause.

### `lang` is inherited, never stamped

`hyphens: auto` needs a correct `lang`, which comes from `main_template`'s
`portal_state.language()`. `aurora_edit.pt` declares `lang="en"` on the element
carrying `metal:use-macro`, which METAL discards in favour of the macro's own
element — so the canvas should inherit the content language exactly as the view
does. **Unverified**: no instance was running. Handed to ticket 10 as an
assertion rather than trusted. No `lang` field on the block: a DE page with an
EN tagline is real but rare, and a field is an author-facing option the standing
principle forbids.

### The headline budget

One README line, no field caption: state the length the design holds at every
width (the longest word must fit ~14 characters at the floor). It can no longer
be a rule now that the CSS never clips, only advice about voice — and a caption
in the sidebar would be a UI commitment every future brand block has to match.

### Done in this ticket: the design source is fixed

The defect is in `docs/design/derico.de/site/assets/site.css` and the next brand
block is authored from that file. Rungs 1, 2 and 4 plus the new ramp are applied
there and verified in the browser:

| viewport | size | copy cell | hero overflow | doc overflow | headline |
|---|---|---|---|---|---|
| 320 | 38.4px | 288 (was 320) | 0 | 0 | `Anwendungen,` / `die bleiben.` |
| 320, compound | 38.4px | 288 (was 383) | 0 | 0 | falls to rung 2 |
| 1440 | 80px | 590 | 0 | 0 | unchanged from the mockup |

The mockup keeps `vw`; it has no toolbar and no container context. That
divergence from the block's `cqi` is exactly the toolbar and is recorded here.

### Correction to ticket 07

07 attributed the canvas's differing 1440 wrap (`Anwendungen` / `, die
bleiben.`) to `overflow-wrap: break-word`. At 1440 all five configurations —
including break-word — produced the identical two lines. The culprit is the
co-inherited `white-space: pre-wrap`, not break-word. This is what makes rung 2
safe at desktop, and it amends the `overflow-wrap: normal` instruction 07 wrote
into tickets 08 and 09 (both updated).
