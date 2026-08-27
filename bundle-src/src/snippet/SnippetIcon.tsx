/**
 * The slash-menu icon: the Balkenlage in section, reduced to what survives at
 * 24px — the Dielen band and three Balkenköpfe beneath it.
 *
 * A React component, never a string, `currentColor` throughout — same rules
 * as `HeroIcon`.
 */
export function SnippetIcon(props: React.SVGProps<SVGSVGElement>) {
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
      <path d="M2 8h20" />
      <path d="M2 11h20" />
      <rect x="3.5" y="11" width="4.5" height="3.5" />
      <rect x="9.75" y="11" width="4.5" height="3.5" />
      <rect x="16" y="11" width="4.5" height="3.5" />
    </svg>
  );
}

export default SnippetIcon;
