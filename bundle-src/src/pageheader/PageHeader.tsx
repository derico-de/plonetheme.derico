/**
 * The Derico Page Header, as one tree rendered by both `edit` and `view` —
 * the mockup's `.page-hero` (site.css:652, 665–668, 1450): a kicker over the
 * title on the left, the description as the lede at the far right, the two
 * bottom-aligned once the header is 56rem wide, stacked below that.
 *
 * `.derico-page-header`, never Aurora's `.block-derico-page-header` wrapper
 * stamp: the wrapper is a different box on each surface (hero ticket 07),
 * and the block owns its own root so one sheet measures the same on both.
 * The block never sets its width; `defaultBlockWidth: 'layout'` is the whole
 * of the wiring, and the wrapper carries it.
 *
 * Every slot is a ReactNode: the view hands in the words, the canvas hands
 * in a control per word. An empty slot is omitted, never an empty element.
 * No whitespace-only text nodes — the Plate editable's `pre-wrap` inherits
 * in, and JSX drops inter-element whitespace by construction.
 */
import type { ReactNode } from 'react';

export type PageHeaderProps = {
  kicker?: ReactNode;
  title?: ReactNode;
  description?: ReactNode;
};

export function PageHeader({ kicker, title, description }: PageHeaderProps) {
  return (
    <section className="derico-page-header">
      <div className="page-header__grid">
        <div>
          {kicker ? <p className="page-context">{kicker}</p> : null}
          {title ? <h1 className="documentFirstHeading">{title}</h1> : null}
        </div>
        {description ? <p className="documentDescription lede">{description}</p> : null}
      </div>
    </section>
  );
}

export default PageHeader;
