import { decisionClass } from "../utils/decisions.js";

export default function DecisionBadge({ decision }) {
  if (!decision) return null;
  return <span className={`badge ${decisionClass(decision)}`}>{decision}</span>;
}