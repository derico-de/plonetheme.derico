/**
 * The hero's photograph — one `<picture>`, two crops, art-directed.
 *
 * Wide and portrait framings are two uploads; the portrait `<source>` comes
 * first because `<picture>` takes the first match. `media` is a viewport
 * query since `<picture>` has no container-query form.
 *
 * One plain scale per crop, derived from the `@id`; the public view builds
 * the real ladder server-side. One crop → that image everywhere; none →
 * `null`.
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
