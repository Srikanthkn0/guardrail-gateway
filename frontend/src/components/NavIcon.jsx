const ICONS = {
  dashboard: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="2" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="2" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  ),
  rules: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M10 3L16.5 6.2V11.8C16.5 14.9 13.8 17.2 10 18.5C6.2 17.2 3.5 14.9 3.5 11.8V6.2L10 3Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path
        d="M7.5 10L9.2 11.7L12.8 8.2"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  ),
  chat: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M4 4.5H16C16.8 4.5 17.5 5.2 17.5 6V12.5C17.5 13.3 16.8 14 16 14H10.5L6.5 16.5V14H4C3.2 14 2.5 13.3 2.5 12.5V6C2.5 5.2 3.2 4.5 4 4.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <circle cx="7" cy="9.2" r="0.9" fill="currentColor" />
      <circle cx="10" cy="9.2" r="0.9" fill="currentColor" />
      <circle cx="13" cy="9.2" r="0.9" fill="currentColor" />
    </svg>
  ),
  logs: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M5 5H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M5 9H15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M5 13H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path
        d="M3.5 3.5H16.5V16.5H3.5V3.5Z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  ),
  github: (
    <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M10 2C5.58 2 2 5.69 2 10.03c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.39 0-.19-.01-.82-.01-1.49-2.22.49-2.69-1.08-2.69-1.08-.36-.93-.89-1.17-.89-1.17-.73-.5.06-.49.06-.49.81.06 1.24.84 1.24.84.72 1.24 1.89.88 2.35.67.07-.53.28-.88.51-1.08-1.77-.2-3.64-.9-3.64-4.02 0-.89.31-1.62.82-2.19-.08-.2-.36-1.02.08-2.12 0 0 .67-.22 2.2.84a7.5 7.5 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.06 2.2-.84 2.2-.84.44 1.1.16 1.92.08 2.12.51.57.82 1.3.82 2.19 0 3.13-1.87 3.82-3.65 4.02.29.25.54.74.54 1.49 0 1.08-.01 1.95-.01 2.21 0 .22.15.47.55.39A8.01 8.01 0 0 0 18 10.03C18 5.69 14.42 2 10 2Z"
      />
    </svg>
  ),
  external: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M11 3H17V9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 12L17 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <path
        d="M13 3H17V7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6 6H5C3.9 6 3 6.9 3 8V15C3 16.1 3.9 17 5 17H12C13.1 17 14 16.1 14 15V14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  ),
};

export default function NavIcon({ name, className = "" }) {
  const icon = ICONS[name];
  if (!icon) return null;
  return <span className={`nav-icon ${className}`.trim()}>{icon}</span>;
}