import { useId } from "react";

export default function Logo({ size = 36, showWordmark = false, className = "" }) {
  const id = useId().replace(/:/g, "");

  return (
    <div className={`logo-mark ${className}`.trim()}>
      <svg
        className="logo"
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id={`${id}-ring`} x1="6" y1="6" x2="42" y2="42" gradientUnits="userSpaceOnUse">
            <stop stopColor="#6ee7b7" />
            <stop offset="0.5" stopColor="#34d399" />
            <stop offset="1" stopColor="#0ea5e9" />
          </linearGradient>
          <linearGradient id={`${id}-shield`} x1="14" y1="10" x2="34" y2="38" gradientUnits="userSpaceOnUse">
            <stop stopColor="#111820" />
            <stop offset="1" stopColor="#0a0e12" />
          </linearGradient>
          <linearGradient id={`${id}-shine`} x1="12" y1="8" x2="36" y2="32" gradientUnits="userSpaceOnUse">
            <stop stopColor="#ffffff" stopOpacity="0.22" />
            <stop offset="1" stopColor="#ffffff" stopOpacity="0" />
          </linearGradient>
          <filter id={`${id}-glow`} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <circle cx="24" cy="24" r="21" stroke={`url(#${id}-ring)`} strokeWidth="1.5" opacity="0.55" />
        <circle cx="24" cy="24" r="17" stroke={`url(#${id}-ring)`} strokeWidth="0.75" opacity="0.25" />

        <path
          d="M24 9L36 14.5V22.5C36 29.4 31 34.6 24 37C17 34.6 12 29.4 12 22.5V14.5L24 9Z"
          fill={`url(#${id}-shield)`}
          stroke={`url(#${id}-ring)`}
          strokeWidth="1.5"
          filter={`url(#${id}-glow)`}
        />
        <path
          d="M24 9L36 14.5V22.5C36 29.4 31 34.6 24 37C17 34.6 12 29.4 12 22.5V14.5L24 9Z"
          fill={`url(#${id}-shine)`}
        />

        <path
          d="M18 23.5H21.5V27H26.5V23.5H30"
          stroke="#6ee7b7"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M18 23.5V20.5C18 18.8 19.4 17.5 21 17.5H27C28.6 17.5 30 18.8 30 20.5V23.5"
          stroke="#34d399"
          strokeWidth="1.75"
          strokeLinecap="round"
        />

        <circle cx="24" cy="16" r="1.5" fill="#38bdf8" opacity="0.9" />
      </svg>

      {showWordmark && (
        <div className="logo-wordmark">
          <span className="logo-wordmark-title">Guardrail</span>
          <span className="logo-wordmark-sub">Gateway</span>
        </div>
      )}
    </div>
  );
}