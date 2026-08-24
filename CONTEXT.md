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
The part of the theme that is only a `:root` override of Clara's public
`--plone-*` token API — colours, fonts, measure, radii, and nothing else.
_Avoid_: skin, override sheet

**Rings figure**:
The Jahresringe signature graphic: a disc of concentric circles with numbered
markers, standing for one solution growing with its client's needs over time.
Deliberately generic — it never depicts derico's own technology timeline.
_Avoid_: growth-rings SVG, tree rings, ring disc

**Ring legend**:
The four captions beneath the rings figure, each naming one stage of that
growth. Rendered as HTML beneath the graphic, never as text inside the SVG.
_Avoid_: ring labels, ring captions, markers

### Blocks

**Brand block**:
An Aurora block that implements one specific design template for one project's
brand. It exposes only the text and images the design calls for, offers the
author no options, and gains a variant only when the design itself demands one.
Insertable by site administrators, not by ordinary editors — a brand block
belongs to a designed page, not to general authoring.
_Avoid_: custom block, theme block, hero block, block add-on (that is the
generic mechanism a brand block is built on, not a synonym)

**Derico Hero**:
The brand block for the derico.de homepage opening: image, kicker, headline,
lede, two calls to action, and the rings figure with its four-entry legend.
_Avoid_: hero banner, homepage block, the hero
