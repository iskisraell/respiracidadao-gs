export function Logo({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <circle cx="16" cy="16" r="15" fill="var(--brand)" />
      <path d="M8 13c3-2.5 6-2.5 9 0s5 2.5 7 .5M8 19c3-2.5 6-2.5 9 0s5 2.5 7 .5" stroke="#fff" strokeWidth="2.4" fill="none" strokeLinecap="round" />
    </svg>
  );
}
