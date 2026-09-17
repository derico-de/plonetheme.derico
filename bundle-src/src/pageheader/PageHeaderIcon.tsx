/**
 * The slash-menu icon: a kicker line, a heading bar, a lede — the header
 * reduced to what survives at 24px.
 *
 * A React component, never a string — the slash menu renders `<Icon />` and a
 * string breaks it. `currentColor` throughout, so the menu's palette drives it.
 */
export function PageHeaderIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      <path d="M4 5h6" />
      <path d="M4 11h11" strokeWidth="3" />
      <path d="M4 17h16" />
      <path d="M4 20h12" />
    </svg>
  );
}

export default PageHeaderIcon;
