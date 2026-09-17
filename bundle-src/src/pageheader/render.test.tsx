/**
 * The two halves against one tree.
 *
 * The public page is drawn by `browser/templates/pageheader.pt` and the
 * canvas by `PageHeader.tsx`; they share one scope-wrapped sheet, so the
 * classes each emits are a contract. `tests/test_pageheader_view.py` pins the
 * server's side of it against the same names.
 *
 * No host here: `formAtom()` falls back to an inert atom, so the bound fields
 * read as empty and the controls start from their placeholders — the state
 * a fresh insert on a bare registry would be in.
 */
import { fireEvent, render } from '@testing-library/react';
import { describe, expect, test, vi } from 'vitest';

import PageHeaderEdit from './PageHeaderEdit';
import PageHeaderView from './PageHeaderView';
import PageHeader from './PageHeader';

const root = (container: HTMLElement) => {
  const header = container.querySelector('.derico-page-header');
  if (!header) throw new Error('the header rendered no root element');
  return header as HTMLElement;
};

describe('the shared tree', () => {
  test('owns `.derico-page-header`, never Aurora’s wrapper stamp', () => {
    const { container } = render(<PageHeader kicker="k" title="t" description="d" />);
    const header = root(container);
    expect(header.tagName).toBe('SECTION');
    expect(container.querySelector('.block-derico-page-header')).toBeNull();
  });

  test('emits the mockup’s classes, in the mockup’s order', () => {
    const { container } = render(<PageHeader kicker="k" title="t" description="d" />);
    const header = root(container);
    const grid = header.querySelector('.page-header__grid');
    expect(grid).not.toBeNull();
    expect(grid!.querySelector(':scope > div > p.page-context')?.textContent).toBe('k');
    expect(grid!.querySelector(':scope > div > h1.documentFirstHeading')?.textContent).toBe('t');
    expect(grid!.querySelector(':scope > p.lede.documentDescription')?.textContent).toBe('d');
  });

  test('omits an empty slot rather than emitting an empty element', () => {
    const { container } = render(<PageHeader title="t" />);
    const header = root(container);
    expect(header.querySelector('.page-context')).toBeNull();
    expect(header.querySelector('.lede')).toBeNull();
    expect(header.querySelector('h1')?.textContent).toBe('t');
  });

  test('never sizes itself: the wrapper carries the width', () => {
    const { container } = render(<PageHeader kicker="k" title="t" description="d" />);
    expect(root(container).getAttribute('style')).toBeNull();
    expect(container.querySelector('[style]')).toBeNull();
  });
});

describe('the view', () => {
  test('trims the kicker and drops it when blank', () => {
    const { container, rerender } = render(<PageHeaderView data={{ kicker: '  Leistungen  ' }} />);
    expect(root(container).querySelector('.page-context')?.textContent).toBe('Leistungen');
    rerender(<PageHeaderView data={{ kicker: '   ' }} />);
    expect(root(container).querySelector('.page-context')).toBeNull();
    rerender(<PageHeaderView data={{ kicker: 42 }} />);
    expect(root(container).querySelector('.page-context')).toBeNull();
  });
});

describe('the canvas', () => {
  test('draws one control per word, each standing where the page puts it', () => {
    const { container } = render(<PageHeaderEdit data={{ kicker: 'Leistungen' }} />);
    const header = root(container);
    const kicker = header.querySelector('p.page-context > textarea') as HTMLTextAreaElement;
    const title = header.querySelector('h1 > textarea') as HTMLTextAreaElement;
    const lede = header.querySelector('p.lede > textarea') as HTMLTextAreaElement;
    expect(kicker.value).toBe('Leistungen');
    expect(title.getAttribute('aria-label')).toBe('Title');
    expect(lede.getAttribute('aria-label')).toBe('Description');
  });

  test('renders every slot even while empty, so it can be typed into', () => {
    const { container } = render(<PageHeaderEdit data={{}} />);
    expect(root(container).querySelectorAll('textarea')).toHaveLength(3);
  });

  test('writes the kicker through onChangeBlock, untrimmed, keeping the node’s other keys', () => {
    const onChangeBlock = vi.fn();
    const { container } = render(
      <PageHeaderEdit block="b1" data={{ '@type': 'derico-page-header', blockWidth: 'layout' } as any} onChangeBlock={onChangeBlock} />,
    );
    const kicker = root(container).querySelector('p.page-context > textarea') as HTMLTextAreaElement;
    fireEvent.change(kicker, { target: { value: 'Leistungen ' } });
    expect(onChangeBlock).toHaveBeenCalledWith('b1', {
      '@type': 'derico-page-header',
      blockWidth: 'layout',
      kicker: 'Leistungen ',
    });
  });

  test('keeps the title to one line', () => {
    const { container } = render(<PageHeaderEdit data={{}} />);
    const title = root(container).querySelector('h1 > textarea') as HTMLTextAreaElement;
    const enter = fireEvent.keyDown(title, { key: 'Enter' });
    // `fireEvent` returns false when a handler called preventDefault().
    expect(enter).toBe(false);
  });

  test('stops its keystrokes at the control (contract §1.7)', () => {
    const seen = vi.fn();
    const { container } = render(
      <div onKeyDown={seen} onPaste={seen}>
        <PageHeaderEdit data={{}} />
      </div>,
    );
    const lede = root(container).querySelector('p.lede > textarea') as HTMLTextAreaElement;
    fireEvent.keyDown(lede, { key: 'Backspace' });
    fireEvent.paste(lede);
    expect(seen).not.toHaveBeenCalled();
  });
});
