/**
 * The slash-menu icon: the growth rings, reduced to what survives at 24px.
 *
 * A React component, never a string — the slash menu renders `<Icon />` and a
 * string breaks it; a missing icon falls back to Aurora's `Square`
 * placeholder, which tells the author nothing.
 *
 * `currentColor` throughout, so the menu's own palette drives it.
 */
export function HeroIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      <circle cx="10" cy="13" r="2.5" />
      <circle cx="10.5" cy="12.5" r="5.5" />
      <circle cx="10" cy="13" r="8.5" strokeWidth="2.25" />
      <circle cx="10.4" cy="12.6" r="11" strokeDasharray="2 3" />
    </svg>
  );
}

export default HeroIcon;
