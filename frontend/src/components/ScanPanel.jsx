import DecisionBadge from "./DecisionBadge.jsx";
import HitTable from "./HitTable.jsx";

export default function ScanPanel({ title, scan }) {
  if (!scan) return null;

  return (
    <div className="scan-panel">
      <div className="result-header">
        <span>{title}</span>
        <DecisionBadge decision={scan.decision} />
      </div>
      {scan.reasons?.length > 0 && (
        <ul className="plain-list">
          {scan.reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}
      <HitTable hits={scan.hits} />
    </div>
  );
}