import { percent } from "../utils/format.js";

function DecisionBars({ stats }) {
  if (!stats || stats.total_requests === 0) {
    return <p className="status-text">No requests logged yet.</p>;
  }

  const rows = [
    { key: "allow", count: stats.allow_count, className: "bar-allow" },
    { key: "warn", count: stats.warn_count, className: "bar-warn" },
    { key: "block", count: stats.block_count, className: "bar-block" },
  ];

  return (
    <div className="bar-chart">
      {rows.map((row) => (
        <div className="bar-row" key={row.key}>
          <span className="bar-label">{row.key}</span>
          <div className="bar-track">
            <div
              className={`bar-fill ${row.className}`}
              style={{ width: `${percent(row.count, stats.total_requests)}%` }}
            />
          </div>
          <span className="bar-value">
            {row.count} ({percent(row.count, stats.total_requests)}%)
          </span>
        </div>
      ))}
    </div>
  );
}

export default function StatsSummary({
  stats,
  showBars = true,
  showProviders = true,
  compact = false,
}) {
  if (!stats) return null;

  if (compact) {
    return (
      <>
        {showBars && <DecisionBars stats={stats} />}
        {showProviders && stats.by_provider?.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Requests</th>
                  <th>Avg latency</th>
                </tr>
              </thead>
              <tbody>
                {stats.by_provider.map((row) => (
                  <tr key={row.provider}>
                    <td>{row.provider}</td>
                    <td>{row.count}</td>
                    <td>
                      {row.avg_latency_ms != null ? `${Math.round(row.avg_latency_ms)} ms` : "n/a"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </>
    );
  }

  return (
    <>
      <div className="status-list">
        <div className="status-list-item">
          <span className="label">Total requests</span>
          <span className="value">{stats.total_requests}</span>
        </div>
        <div className="status-list-item">
          <span className="label">Block rate</span>
          <span className="value">{(stats.block_rate * 100).toFixed(1)}%</span>
        </div>
        <div className="status-list-item">
          <span className="label">Warn rate</span>
          <span className="value">{(stats.warn_rate * 100).toFixed(1)}%</span>
        </div>
        <div className="status-list-item">
          <span className="label">Avg latency</span>
          <span className="value">
            {stats.avg_latency_ms != null ? `${Math.round(stats.avg_latency_ms)} ms` : "n/a"}
          </span>
        </div>
      </div>

      <div className="status-list">
        <div className="status-list-item">
          <span className="label">Allow</span>
          <span className="value">{stats.allow_count}</span>
        </div>
        <div className="status-list-item">
          <span className="label">Warn</span>
          <span className="value">{stats.warn_count}</span>
        </div>
        <div className="status-list-item">
          <span className="label">Block</span>
          <span className="value">{stats.block_count}</span>
        </div>
        <div className="status-list-item">
          <span className="label">Forwarded</span>
          <span className="value">{stats.forwarded_count}</span>
        </div>
      </div>

      {showBars && <DecisionBars stats={stats} />}

      {showProviders && stats.by_provider?.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Requests</th>
                <th>Avg latency</th>
              </tr>
            </thead>
            <tbody>
              {stats.by_provider.map((row) => (
                <tr key={row.provider}>
                  <td>{row.provider}</td>
                  <td>{row.count}</td>
                  <td>
                    {row.avg_latency_ms != null ? `${Math.round(row.avg_latency_ms)} ms` : "n/a"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}