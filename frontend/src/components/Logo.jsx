export default function Logo({ size = 36, className = "" }) {
  return (
    <svg
      className={`logo ${className}`.trim()}
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="shield-grad" x1="8" y1="6" x2="32" y2="34" gradientUnits="userSpaceOnUse">
          <stop stopColor="#22d3ee" />
          <stop offset="1" stopColor="#818cf8" />
        </linearGradient>
        <linearGradient id="shield-shine" x1="10" y1="8" x2="30" y2="30" gradientUnits="userSpaceOnUse">
          <stop stopColor="#ffffff" stopOpacity="0.2" />
          <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path
        d="M20 4L34 10V19C34 27.5 28 33.5 20 36C12 33.5 6 27.5 6 19V10L20 4Z"
        fill="#111116"
        stroke="url(#shield-grad)"
        strokeWidth="1.5"
      />
      <path
        d="M20 4L34 10V19C34 27.5 28 33.5 20 36C12 33.5 6 27.5 6 19V10L20 4Z"
        fill="url(#shield-shine)"
      />
      <path
        d="M16.5 20L18.8 22.5L24 17"
        stroke="url(#shield-grad)"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="20" cy="14" r="2" fill="#22d3ee" opacity="0.7" />
    </svg>
  );
}