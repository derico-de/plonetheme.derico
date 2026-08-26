# plonetheme.derico

The derico.de brand as a Plone theme: the "Jahresringe" design language expressed
as a token layer on `plonetheme.clara`, plus the brand blocks that realise the
parts of the design tokens cannot reach.

## Language

### The design language

**Jahresringe**:
The derico.de design language — growth rings as the image of an application
that keeps its value as it grows. Chosen 2026-07-16 from three explored
variants; the other two were deleted.
_Avoid_: growth rings (as a name for the whole language), the derico look

**Token layer**:
The part of the theme that carries the Jahresringe values onto Clara by
re-pointing its tokens — colours, fonts, measure, radii. Almost all of it is
token declarations, and a rule earns its place there only when nothing else in
the theme can reach the thing it styles: a brand block's own stylesheet is
scope-wrapped and so can never touch the page around the block.
_Avoid_: skin, override sheet, tokens-only layer

**Rings figure**:
The Jahresringe signature graphic: a disc of concentric circles with numbered
markers, standing for one solution growing with its client's needs over time.
Deliberately generic — it never depicts derico's own technology timeline.
_Avoid_: growth-rings SVG, tree rings, ring disc

**Ring legend**:
The four captions beneath the rings figure, each naming one stage of that
growth. Rendered as HTML beneath the graphic, never as text inside the SVG.
_Avoid_: ring labels, ring captions, markers

**Ring halo**:
The near-black outline carried by every stroke of the rings figure, drawn as a
second, wider stroke beneath the coloured one so the disc keeps its contrast
over any photograph without being given a ground to sit on. The same treatment
the numbered markers have always had — an opaque fill inside a ground-coloured
border — applied to strokes. It is a contrast guarantee, not a shadow: it is
crisp and opaque precisely so its value can be read off the stylesheet.
_Avoid_: outline, glow, stroke shadow, drop shadow

### Blocks

**Brand block**:
An Aurora block that implements one specific design template for one project's
brand. It exposes only the text and images the design calls for, offers the
author no options, and gains a variant only when the design itself demands one.
Insertable by site administrators, not by ordinary editors — a brand block
belongs to a designed page, not to general authoring.
_Avoid_: custom block, theme block, hero block, block add-on (that is the
generic mechanism a brand block is built on, not a synonym)

**Hero wash**:
The darkening that lets the Derico Hero's words sit on its photograph — a
gradient over the image, keyed to the side the copy is on, not a flat tint over
the whole picture. It belongs to the hero's composition, not to the Jahresringe
palette. It is a compositional layer, not a contrast guarantee: ticket 18 made
the **copy scrim** carry the guarantee and left the wash deliberately
non-load-bearing.
_Avoid_: overlay, tint, gradient, scrim (that is the copy scrim, a different
layer with a different job — see below)

**Copy scrim**:
The opaque-enough backdrop under the Derico Hero's copy column that keeps its
text legible over any photograph an author uploads. Feathered to transparent
outside the copy box, and the only layer over the copy at either breakpoint —
stacking it with the hero wash would composite to a solid panel the design
avoids. Unlike the wash it exists to hit a number, not to compose.
_Avoid_: wash, overlay, gradient

**Derico Hero**:
The brand block for the derico.de homepage opening: image, kicker, headline,
lede, two calls to action, and the rings figure with its four-entry legend.
_Avoid_: hero banner, homepage block, the hero

**Headline budget**:
The headline length the Derico Hero's design holds at every width — roughly a
longest word of fourteen characters. Advice about voice, not a rule: the block's
CSS keeps any headline visible, so exceeding the budget costs typographic
quality rather than legibility. Written down for whoever writes the copy, never
enforced on the author.
_Avoid_: max length, character limit, headline validation
