import DecisionBadge from "./DecisionBadge.jsx";
import HitTable from "./HitTable.jsx";

function mlMeterClass(score) {
  if (score >= 0.85) return "ml-meter-danger";
  if (score >= 0.5) return "ml-meter-warn";
  return "ml-meter-safe";
}

export default function ScanPanel({ title, scan }) {
  if (!scan) return null;

  const mlScore = scan.ml_score ?? 0;
  const mlPercent = (mlScore * 100).toFixed(1);

  return (
    <div className="scan-panel">
      <div className="scan-panel-header">
        <span className="scan-panel-title">{title}</span>
        <DecisionBadge decision={scan.decision} />
      </div>

      {scan.ml_enabled && (
        <div className="ml-meter">
          <div className="ml-meter-header">
            <span>
              ML injection score
              {scan.ml_loaded
                ? ` · ${scan.ml_label} (${scan.ml_backend})`
                : " · model not loaded"}
            </span>
            {scan.ml_loaded && <span>{mlPercent}%</span>}
          </div>
          {scan.ml_loaded && (
            <div className="ml-meter-track">
              <div
                className={`ml-meter-fill ${mlMeterClass(mlScore)}`}
                style={{ width: `${Math.min(mlScore * 100, 100)}%` }}
              />
            </div>
          )}
        </div>
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