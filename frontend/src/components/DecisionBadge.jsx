import { decisionClass } from "../utils/decisions.js";

const LABELS = {
  allow: "Passed",
  block: "Blocked",
  warn: "Warning",
};

export default function DecisionBadge({ decision, showDot = true }) {
  if (!decision) return null;
  const label = LABELS[decision] ?? decision;
  return (
    <span className={`badge ${decisionClass(decision)}`}>
      {showDot && <span className="badge-dot" aria-hidden="true" />}
      {label}
    </span>
  );
}