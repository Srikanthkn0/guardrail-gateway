export default function Logo({ size = 32, showWordmark = false, className = "" }) {
  return (
    <div className={`logo-mark ${className}`.trim()}>
      <svg
        className="logo"
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <path
          d="M16 4L26 8V15C26 21 21.5 25 16 27C10.5 25 6 21 6 15V8L16 4Z"
          fill="#181818"
          stroke="#4ade80"
          strokeWidth="1.5"
        />
        <path
          d="M12 15H14.5V18H17.5V15H20"
          stroke="#4ade80"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
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