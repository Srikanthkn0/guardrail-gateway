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
      {scan.ml_enabled && (
        <p className="status-text">
          ML classifier:{" "}
          {scan.ml_loaded
            ? `${(scan.ml_score * 100).toFixed(1)}% injection (${scan.ml_label}, ${scan.ml_backend})`
            : "enabled but model not loaded"}
        </p>
      )}
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