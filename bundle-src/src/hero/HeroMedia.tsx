/**
 * The hero's photograph — one `<picture>`, two crops, art-directed.
 *
 * Plone's named scales give variants of ONE crop, never art direction, so the
 * wide and portrait framings stay two uploads (ticket 05). The portrait
 * `<source>` comes first and carries the narrow `media`, because a `<picture>`
 * takes the first source that matches.
 *
 * `media` is a VIEWPORT query here while the layout switch next door is a
 * container query, and that is deliberate: `<picture>` has no container-query
 * form, and the mismatch costs at most a slightly-too-large image for a
 * logged-in author whose canvas is narrower than the viewport by the toolbar.
 * Bytes, not layout — 06 §8/§9 put the error on this side on purpose.
 *
 * One plain scale per crop, derived from the `@id` (ticket 05): the editor
 * has no `image_scales` for an image the author has only just picked, since
 * the reference widget trims the brain down to its `@id` before storing it.
 * The public half builds the real resolution ladder server-side through
 * `Img2PictureTag`; this is the editor's preview and Aurora-proper's
 * fallback, and both halves emit the same `.hero-media` element either way.
 *
 * Degradation (ticket 02): both crops → art direction; one crop → that image
 * at every breakpoint, with the source it has no image for dropped; no crop →
 * `null`, so the caller emits no `<picture>` and no wash and the hero falls
 * back to its token ground.
 *
 * `aria-hidden`, and no `alt` field anywhere in the schema: the photograph is
 * decorative in this design.
 */
import { previewImage } from './data';
import type { HeroData } from './data';

export function HeroMedia({ data }: { data: HeroData }) {
  const wide = previewImage(data.image_wide);
  const portrait = previewImage(data.image_portrait);
  const fallback = wide || portrait;
  if (!fallback) return null;
  return (
    <picture className="hero-media" aria-hidden="true">
      {portrait && wide ? (
        <source media="(max-width: 55.99rem)" srcSet={portrait} />
      ) : null}
      <img src={fallback} alt="" decoding="async" fetchPriority="high" />
    </picture>
  );
}

export default HeroMedia;
